from flask import Blueprint, request, jsonify
from sqlalchemy import or_, func, and_
from sqlalchemy.orm import joinedload
from collections import deque
import uuid
import re
import logging
from models import db, Person, Relationship
from config import Config

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def normalize_name(name):
    """Normalize name for search: lowercase, remove extra spaces"""
    if not name:
        return ''
    normalized = ' '.join(name.lower().split())
    return normalized


def validate_uuid(uuid_string):
    """Validate UUID format"""
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False


def get_error_response(code, message, status_code=400):
    """Standard error response format"""
    return jsonify({'error': {'code': code, 'message': message}}), status_code


# ==================== API ROUTES ====================

@api_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute(db.text('SELECT 1'))
        db_status = 'connected'
    except Exception as e:
        logger.error(f'Database health check failed: {e}')
        db_status = 'disconnected'
    
    return jsonify({
        'status': 'ok',
        'database': db_status
    })


@api_bp.route('/api/root', methods=['GET'])
def get_root():
    """Get the root person (King Sahle Selassie or oldest base person)"""
    try:
        if Config.ROOT_PERSON_ID:
            if not validate_uuid(Config.ROOT_PERSON_ID):
                return get_error_response('BAD_REQUEST', 'Invalid ROOT_PERSON_ID format')
            
            root = Person.query.filter_by(id=Config.ROOT_PERSON_ID, layer='base').first()
            if not root:
                return get_error_response('NOT_FOUND', 'Root person not found')
        else:
            # Fallback: oldest base person
            root = Person.query.filter_by(layer='base').order_by(Person.created_at.asc()).first()
            if not root:
                return get_error_response('NOT_FOUND', 'No base persons found in database')
        
        return jsonify(root.to_dict())
    except Exception as e:
        logger.error(f'Error getting root: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Failed to get root person', 500)


@api_bp.route('/api/search', methods=['GET'])
def search():
    """Search for people by name (max 25 results)"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return get_error_response('BAD_REQUEST', 'Query parameter "q" is required')
    
    if len(query) > 100:
        return get_error_response('BAD_REQUEST', 'Query too long (max 100 characters)')
    
    try:
        normalized_query = normalize_name(query)
        
        # Base query - only base layer for Phase 1
        base_query = Person.query.filter_by(layer='base')
        
        # Search: exact match, starts with, contains (English names)
        exact_matches = base_query.filter(Person.name_normalized == normalized_query).all()
        starts_with = base_query.filter(
            Person.name_normalized.like(f'{normalized_query}%')
        ).filter(Person.name_normalized != normalized_query).all()
        contains = base_query.filter(
            Person.name_normalized.like(f'%{normalized_query}%')
        ).filter(
            ~Person.name_normalized.like(f'{normalized_query}%')
        ).all()
        
        # Also search Amharic names if query contains non-ASCII characters (likely Amharic)
        if any(ord(char) > 127 for char in query):
            amharic_matches = base_query.filter(
                Person.name_amharic.ilike(f'%{query}%')
            ).all()
            # Merge without duplicates
            existing_ids = {p.id for p in exact_matches + starts_with + contains}
            for match in amharic_matches:
                if match.id not in existing_ids:
                    contains.append(match)
        
        # Combine and limit to 25
        results = exact_matches + starts_with + contains[:25 - len(exact_matches) - len(starts_with)]
        results = results[:25]
        
        return jsonify({
            'results': [person.to_dict() for person in results]
        })
    except Exception as e:
        logger.error(f'Error in search: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Search failed', 500)


@api_bp.route('/api/neighborhood/<person_id>', methods=['GET'])
def get_neighborhood(person_id):
    """
    Get 3-section view: parent (one), person, children (all)
    Returns exactly ONE parent (prefer father, else mother, else any)
    """
    if not validate_uuid(person_id):
        return get_error_response('BAD_REQUEST', 'Invalid person ID format')
    
    try:
        person = Person.query.filter_by(id=person_id, layer='base').first()
        if not person:
            return get_error_response('NOT_FOUND', 'Person not found')
        
        # Get parent relationships (where this person is the child)
        parent_rels = Relationship.query.filter_by(
            child_id=person.id,
            visibility='public'
        ).options(joinedload(Relationship.parent)).all()
        
        # Choose parent: prefer father, else mother, else any
        parent = None
        parent_type = None
        for rel in parent_rels:
            if rel.relation_type == 'father':
                parent = rel.parent
                parent_type = 'father'
                break
        
        if not parent:
            for rel in parent_rels:
                if rel.relation_type == 'mother':
                    parent = rel.parent
                    parent_type = 'mother'
                    break
        
        if not parent and parent_rels:
            parent = parent_rels[0].parent
            parent_type = parent_rels[0].relation_type
        
        # Get children (where this person is the parent)
        child_rels = Relationship.query.filter_by(
            parent_id=person.id,
            visibility='public'
        ).options(joinedload(Relationship.child)).all()
        
        # Preserve import order by sorting by relationship created_at (matches CSV import order)
        children = sorted(child_rels, key=lambda rel: rel.created_at)
        children = [rel.child for rel in children]
        
        response = {
            'parent': parent.to_dict() if parent else None,
            'parent_type': parent_type,
            'person': person.to_dict(),
            'children': [child.to_dict() for child in children],
            'is_leaf': len(children) == 0  # Phase 2: attachment point indicator
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f'Error getting neighborhood: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Failed to get neighborhood', 500)


@api_bp.route('/api/person/<person_id>', methods=['GET'])
def get_person(person_id):
    """Get person with all parents and children"""
    if not validate_uuid(person_id):
        return get_error_response('BAD_REQUEST', 'Invalid person ID format')
    
    try:
        person = Person.query.filter_by(id=person_id, layer='base').first()
        if not person:
            return get_error_response('NOT_FOUND', 'Person not found')
        
        # Get all parent relationships
        parent_rels = Relationship.query.filter_by(
            child_id=person.id,
            visibility='public'
        ).options(joinedload(Relationship.parent)).all()
        
        father = None
        mother = None
        other_parents = []
        
        for rel in parent_rels:
            if rel.relation_type == 'father':
                father = rel.parent
            elif rel.relation_type == 'mother':
                mother = rel.parent
            else:
                other_parents.append(rel.parent)
        
        # Get all children
        child_rels = Relationship.query.filter_by(
            parent_id=person.id,
            visibility='public'
        ).options(joinedload(Relationship.child)).all()
        
        # Preserve import order by sorting by relationship created_at (matches CSV import order)
        children = sorted(child_rels, key=lambda rel: rel.created_at)
        children = [rel.child for rel in children]
        
        return jsonify({
            'person': person.to_dict(),
            'parents': {
                'father': father.to_dict() if father else None,
                'mother': mother.to_dict() if mother else None,
                'other': [p.to_dict() for p in other_parents]
            },
            'children': [child.to_dict() for child in children],
            'is_leaf': len(children) == 0
        })
    except Exception as e:
        logger.error(f'Error getting person: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Failed to get person', 500)


@api_bp.route('/api/people', methods=['GET'])
def get_all_people():
    """Get all people for dropdown selection"""
    try:
        people = Person.query.filter_by(layer='base').order_by(Person.name_original.asc()).all()
        return jsonify({
            'people': [person.to_dict() for person in people]
        })
    except Exception as e:
        logger.error(f'Error getting all people: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Failed to get people', 500)


@api_bp.route('/api/relationship', methods=['GET'])
def get_relationship():
    """Find relationship with ancestry paths going up to common ancestor"""
    person1_id = request.args.get('person1_id')
    person2_id = request.args.get('person2_id')
    
    if not person1_id or not person2_id:
        return get_error_response('BAD_REQUEST', 'Both person1_id and person2_id are required')
    
    if not validate_uuid(person1_id) or not validate_uuid(person2_id):
        return get_error_response('BAD_REQUEST', 'Invalid person ID format')
    
    if person1_id == person2_id:
        person = Person.query.filter_by(id=person1_id, layer='base').first()
        if not person:
            return get_error_response('NOT_FOUND', 'Person not found')
        return jsonify({
            'found': True,
            'person1_lineage': [person.to_dict()],
            'person2_lineage': [],
            'common_ancestor': person.to_dict(),
            'message': 'Same person'
        })
    
    try:
        person1 = Person.query.filter_by(id=person1_id, layer='base').first()
        person2 = Person.query.filter_by(id=person2_id, layer='base').first()
        
        if not person1 or not person2:
            return get_error_response('NOT_FOUND', 'One or both persons not found')
        
        # Find common ancestor first
        common_ancestor = find_common_ancestor(person1_id, person2_id)
        
        if common_ancestor:
            # Build paths from each person up to the common ancestor
            # This ensures we follow paths that actually lead to the common ancestor
            person1_lineage = get_path_to_ancestor(person1_id, common_ancestor.id)
            person2_lineage = get_path_to_ancestor(person2_id, common_ancestor.id)
            
            return jsonify({
                'found': True,
                'person1_lineage': person1_lineage,
                'person2_lineage': person2_lineage,
                'common_ancestor': common_ancestor.to_dict()
            })
        else:
            # No common ancestor found, return full lineages
            person1_lineage = get_ancestry_path(person1_id)
            person2_lineage = get_ancestry_path(person2_id)
            return jsonify({
                'found': False,
                'person1_lineage': person1_lineage,
                'person2_lineage': person2_lineage,
                'common_ancestor': None
            })
    except Exception as e:
        logger.error(f'Error finding relationship: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', 'Failed to find relationship', 500)


def bfs_shortest_path(start_id, end_id):
    """BFS to find shortest path between two people (undirected)"""
    if start_id == end_id:
        return [start_id]
    
    # Build adjacency list (undirected)
    relationships = Relationship.query.filter_by(visibility='public').all()
    graph = {}
    
    for rel in relationships:
        parent_id = str(rel.parent_id)
        child_id = str(rel.child_id)
        
        if parent_id not in graph:
            graph[parent_id] = []
        if child_id not in graph:
            graph[child_id] = []
        
        graph[parent_id].append(child_id)
        graph[child_id].append(parent_id)
    
    start_str = str(start_id)
    end_str = str(end_id)
    
    if start_str not in graph or end_str not in graph:
        return []
    
    # BFS
    queue = deque([(start_str, [start_str])])
    visited = {start_str}
    
    while queue:
        current, path = queue.popleft()
        
        if current == end_str:
            return [uuid.UUID(p) for p in path]
        
        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))
    
    return []


def find_common_ancestor(person1_id, person2_id):
    """Find common ancestor by getting all ancestors of both and finding intersection"""
    # Get all ancestors of person1
    ancestors1 = get_all_ancestors(person1_id)
    
    # Get all ancestors of person2
    ancestors2 = get_all_ancestors(person2_id)
    
    # Find common ancestors (intersection)
    common_ancestors = ancestors1.intersection(ancestors2)
    
    if not common_ancestors:
        return None
    
    # Find the most recent common ancestor (closest to both people)
    # We'll use BFS from both people to find the closest one
    # For now, just return the first one found (we can improve this later)
    for ancestor_id in common_ancestors:
        ancestor = Person.query.get(ancestor_id)
        if ancestor:
            return ancestor
    
    return None


def get_all_ancestors(person_id):
    """Get all ancestors of a person (recursive)"""
    ancestors = set()
    queue = deque([person_id])
    
    while queue:
        current = queue.popleft()
        if current in ancestors:
            continue
        ancestors.add(current)
        
        # Get parents
        parent_rels = Relationship.query.filter_by(
            child_id=current,
            visibility='public'
        ).all()
        
        for rel in parent_rels:
            queue.append(rel.parent_id)
    
    return ancestors


def get_ancestry_path(person_id):
    """Get ancestry path going up (person -> parent -> grandparent -> ...)"""
    path = []
    current_id = person_id
    visited = set()
    
    while current_id:
        if current_id in visited:
            break
        visited.add(current_id)
        
        person = Person.query.get(current_id)
        if not person:
            break
        
        path.append(person.to_dict())
        
        # Get parent (prefer father, else mother, else any)
        parent_rels = Relationship.query.filter_by(
            child_id=current_id,
            visibility='public'
        ).all()
        
        parent = None
        for rel in parent_rels:
            if rel.relation_type == 'father':
                parent = rel.parent
                break
        
        if not parent:
            for rel in parent_rels:
                if rel.relation_type == 'mother':
                    parent = rel.parent
                    break
        
        if not parent and parent_rels:
            parent = parent_rels[0].parent
        
        if parent:
            current_id = parent.id
        else:
            break
    
    return path


def get_person_name(person_id):
    """Helper to get person name by ID"""
    person = Person.query.get(person_id)
    return person.name_original if person else 'Unknown'


# ==================== ADMIN ROUTES ====================

def check_admin_token():
    """Check admin token from header"""
    token = request.headers.get('X-ADMIN-TOKEN')
    if not token or token != Config.ADMIN_TOKEN:
        return get_error_response('BAD_REQUEST', 'Invalid or missing admin token', 401)
    return None


@admin_bp.route('/import/people', methods=['POST'])
def import_people():
    """Import people (admin only)"""
    auth_error = check_admin_token()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        if not data or 'people' not in data:
            return get_error_response('BAD_REQUEST', 'Missing "people" array in request body')
        
        people_data = data['people']
        if not isinstance(people_data, list):
            return get_error_response('BAD_REQUEST', '"people" must be an array')
        
        created_count = 0
        updated_count = 0
        rejected = []
        
        for idx, person_data in enumerate(people_data):
            try:
                # Support both formats: 'name_original' (old) or 'english_name' (new)
                name_original = person_data.get('english_name', person_data.get('name_original', '')).strip()
                if not name_original:
                    rejected.append({'row': idx, 'reason': 'Missing english_name or name_original'})
                    continue
                
                # Amharic name (optional) - support both 'amharic_name' and 'name_amharic'
                name_amharic = person_data.get('amharic_name', person_data.get('name_amharic', '')).strip() or None
                
                person_id = None
                if 'id' in person_data and person_data['id']:
                    if not validate_uuid(person_data['id']):
                        rejected.append({'row': idx, 'reason': 'Invalid UUID format'})
                        continue
                    person_id = uuid.UUID(person_data['id'])
                
                name_normalized = normalize_name(name_original)
                
                # Upsert
                if person_id:
                    person = Person.query.get(person_id)
                    if person:
                        person.name_original = name_original
                        person.name_amharic = name_amharic
                        person.name_normalized = name_normalized
                        person.layer = person_data.get('layer', 'base')
                        if 'birth_year' in person_data:
                            person.birth_year = person_data['birth_year']
                        if 'death_year' in person_data:
                            person.death_year = person_data['death_year']
                        if 'gender' in person_data:
                            person.gender = person_data['gender']
                        updated_count += 1
                    else:
                        person = Person(
                            id=person_id,
                            name_original=name_original,
                            name_amharic=name_amharic,
                            name_normalized=name_normalized,
                            layer=person_data.get('layer', 'base'),
                            birth_year=person_data.get('birth_year'),
                            death_year=person_data.get('death_year'),
                            gender=person_data.get('gender')
                        )
                        db.session.add(person)
                        created_count += 1
                else:
                    person = Person(
                        name_original=name_original,
                        name_amharic=name_amharic,
                        name_normalized=name_normalized,
                        layer=person_data.get('layer', 'base'),
                        birth_year=person_data.get('birth_year'),
                        death_year=person_data.get('death_year'),
                        gender=person_data.get('gender')
                    )
                    db.session.add(person)
                    created_count += 1
                
            except Exception as e:
                rejected.append({'row': idx, 'reason': str(e)})
        
        db.session.commit()
        
        return jsonify({
            'created': created_count,
            'updated': updated_count,
            'rejected': rejected,
            'total_processed': len(people_data)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error importing people: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', f'Import failed: {str(e)}', 500)


@admin_bp.route('/import/combined', methods=['POST'])
def import_combined():
    """
    Import people and relationships from a single CSV-like structure.
    Accepts format: english_name, amharic_name, english_parent_name, amharic_parent_name
    """
    auth_error = check_admin_token()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        if not data or 'rows' not in data:
            return get_error_response('BAD_REQUEST', 'Missing "rows" array in request body')
        
        rows_data = data['rows']
        if not isinstance(rows_data, list):
            return get_error_response('BAD_REQUEST', '"rows" must be an array')
        
        # Step 1: Import all people first
        people_data = []
        relationships_data = []
        
        for row in rows_data:
            # Extract person data
            english_name = row.get('english_name', row.get('name_original', '')).strip()
            if not english_name:
                continue
            
            person_entry = {
                'english_name': english_name,
                'amharic_name': row.get('amharic_name', row.get('name_amharic', '')).strip() or None
            }
            
            # Include birth_year and death_year for duplicate name matching
            if 'birth_year' in row and row['birth_year']:
                try:
                    person_entry['birth_year'] = int(row['birth_year'])
                except (ValueError, TypeError):
                    pass
            
            if 'death_year' in row and row['death_year']:
                try:
                    person_entry['death_year'] = int(row['death_year'])
                except (ValueError, TypeError):
                    pass
            
            # Support direct ID specification for unambiguous matching
            if 'person_id' in row and row['person_id']:
                person_entry['id'] = row['person_id'].strip()
            
            people_data.append(person_entry)
            
            # Extract relationship data
            english_parent_name = row.get('english_parent_name', row.get('parent_name', '')).strip()
            if english_parent_name:
                relationships_data.append({
                    'child_english_name': english_name,
                    'parent_english_name': english_parent_name,
                    'relation_type': row.get('relation_type', 'parent').strip().lower() or 'parent',
                    'child_birth_year': person_entry.get('birth_year'),
                    'child_death_year': person_entry.get('death_year')
                })
        
        # Import people
        people_result = import_people_batch(people_data)
        
        # Step 2: Create name to ID mapping with smart matching for duplicates
        # Build a map of all imported people first (by order of import)
        imported_people_map = {}  # Maps name -> list of (person_entry, index) in import order
        for idx, person_entry in enumerate(people_data):
            english_name = person_entry['english_name']
            if english_name not in imported_people_map:
                imported_people_map[english_name] = []
            imported_people_map[english_name].append((person_entry, idx))
        
        name_to_id = {}
        for person_entry in people_data:
            english_name = person_entry['english_name']
            
            # If direct ID is provided, use it
            if 'id' in person_entry and person_entry['id']:
                try:
                    person_id = uuid.UUID(person_entry['id'])
                    person = Person.query.get(person_id)
                    if person:
                        name_to_id[english_name] = str(person.id)
                        continue
                except (ValueError, TypeError):
                    pass  # Invalid UUID, fall through to name matching
            
            name_normalized = normalize_name(english_name)
            birth_year = person_entry.get('birth_year')
            death_year = person_entry.get('death_year')
            
            # Find all people with this name
            query = Person.query.filter_by(name_normalized=name_normalized, layer='base')
            candidates = query.all()
            
            if len(candidates) == 0:
                # Person not found - will be created during import
                continue
            elif len(candidates) == 1:
                # Only one match - use it
                name_to_id[english_name] = str(candidates[0].id)
            else:
                # Multiple people with same name - use smart matching
                matched = None
                
                # First try: birth_year or death_year if provided
                if birth_year:
                    matched = next((p for p in candidates if p.birth_year == birth_year), None)
                if not matched and death_year:
                    matched = next((p for p in candidates if p.death_year == death_year), None)
                
                # Second try: Use import order - if this person appears earlier in the import,
                # they were likely imported earlier, so match to the most recently created
                # person with this name (likely from a previous import of the same branch)
                if not matched:
                    # Get the import index of this person
                    import_entries = imported_people_map.get(english_name, [])
                    current_idx = next((idx for entry, idx in import_entries if entry == person_entry), None)
                    
                    if current_idx is not None:
                        # Check if this person appears earlier in the import (likely the parent/ancestor)
                        earlier_entries = [idx for entry, idx in import_entries if idx < current_idx]
                        if earlier_entries:
                            # This person was imported before, so use the most recent match
                            matched = sorted(candidates, key=lambda p: p.created_at, reverse=True)[0]
                        else:
                            # This is the first occurrence, use most recent
                            matched = sorted(candidates, key=lambda p: p.created_at, reverse=True)[0]
                    else:
                        # Fallback: use most recently created
                        matched = sorted(candidates, key=lambda p: p.created_at, reverse=True)[0]
                
                if matched:
                    name_to_id[english_name] = str(matched.id)
                    if not birth_year and not death_year:
                        logger.info(f"Multiple people named '{english_name}' found. Using most recent match: {matched.id}. Import order and context will be used for disambiguation.")
        
        # Step 3: Import relationships
        created_rels = 0
        rejected_rels = []
        
        for idx, rel_data in enumerate(relationships_data):
            parent_id = name_to_id.get(rel_data['parent_english_name'])
            child_id = name_to_id.get(rel_data['child_english_name'])
            
            # If parent not found or ambiguous, use parent-child relationship context
            if not parent_id:
                parent_name = rel_data['parent_english_name']
                parent_normalized = normalize_name(parent_name)
                parent_candidates = Person.query.filter_by(name_normalized=parent_normalized, layer='base').all()
                
                if len(parent_candidates) == 1:
                    parent_id = str(parent_candidates[0].id)
                    name_to_id[parent_name] = parent_id
                elif len(parent_candidates) > 1:
                    # Multiple parents with same name - use relationship context
                    # Check if child_id is known and if any parent already has this child
                    if child_id:
                        for candidate in parent_candidates:
                            existing_rel = Relationship.query.filter_by(
                                parent_id=candidate.id,
                                child_id=child_id
                            ).first()
                            if existing_rel:
                                parent_id = str(candidate.id)
                                name_to_id[parent_name] = parent_id
                                break
                    
                    # If still not matched, check if any parent has children that match the pattern
                    # (e.g., if we're importing "Child 1" and one parent already has "Child 2", likely same family)
                    if not parent_id and child_id:
                        child = Person.query.get(child_id)
                        if child:
                            child_normalized = normalize_name(child.name_original)
                            # Find parents who have children with similar names (same family likely)
                            for candidate in parent_candidates:
                                child_rels = Relationship.query.filter_by(parent_id=candidate.id).all()
                                # If this parent has other children, likely the right one
                                if len(child_rels) > 0:
                                    parent_id = str(candidate.id)
                                    name_to_id[parent_name] = parent_id
                                    logger.info(f"Matched parent '{parent_name}' based on existing children context.")
                                    break
                    
                    # Final fallback: use most recently created parent
                    if not parent_id:
                        matched = sorted(parent_candidates, key=lambda p: p.created_at, reverse=True)[0]
                        parent_id = str(matched.id)
                        name_to_id[parent_name] = parent_id
                        logger.info(f"Multiple parents named '{parent_name}' found. Using most recent: {matched.id}.")
            
            if not parent_id:
                rejected_rels.append({'row': idx, 'reason': f"Parent '{rel_data['parent_english_name']}' not found."})
                continue
            
            if not child_id:
                rejected_rels.append({'row': idx, 'reason': f"Child '{rel_data['child_english_name']}' not found."})
                continue
            
            # Check if relationship already exists
            existing = Relationship.query.filter_by(
                parent_id=parent_id,
                child_id=child_id,
                relation_type=rel_data['relation_type']
            ).first()
            
            if existing:
                continue
            
            # Create relationship
            relationship = Relationship(
                parent_id=parent_id,
                child_id=child_id,
                relation_type=rel_data['relation_type'],
                visibility='public'
            )
            db.session.add(relationship)
            created_rels += 1
        
        db.session.commit()
        
        return jsonify({
            'people': {
                'created': people_result.get('created', 0),
                'updated': people_result.get('updated', 0),
                'rejected': people_result.get('rejected', [])
            },
            'relationships': {
                'created': created_rels,
                'rejected': rejected_rels
            },
            'total_processed': len(rows_data)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error in combined import: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', f'Import failed: {str(e)}', 500)


def import_people_batch(people_data):
    """Helper function to import a batch of people"""
    created_count = 0
    updated_count = 0
    rejected = []
    
    for idx, person_data in enumerate(people_data):
        try:
            english_name = person_data['english_name']
            amharic_name = person_data.get('amharic_name')
            
            name_normalized = normalize_name(english_name)
            
            # Check if person exists
            existing = Person.query.filter_by(name_normalized=name_normalized, layer='base').first()
            
            if existing:
                existing.name_original = english_name
                if amharic_name:
                    existing.name_amharic = amharic_name
                updated_count += 1
            else:
                person = Person(
                    name_original=english_name,
                    name_amharic=amharic_name,
                    name_normalized=name_normalized,
                    layer='base'
                )
                db.session.add(person)
                created_count += 1
        
        except Exception as e:
            rejected.append({'row': idx, 'reason': str(e)})
    
    db.session.commit()
    
    return {
        'created': created_count,
        'updated': updated_count,
        'rejected': rejected
    }


@admin_bp.route('/delete/person', methods=['POST'])
def delete_person():
    """Delete a person and their relationships (admin only)"""
    auth_error = check_admin_token()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        person_id = data.get('person_id')
        person_name = data.get('person_name')  # Alternative: search by name
        
        if not person_id and not person_name:
            return get_error_response('BAD_REQUEST', 'Either person_id or person_name is required')
        
        # Find the person
        if person_id:
            if not validate_uuid(person_id):
                return get_error_response('BAD_REQUEST', 'Invalid person ID format')
            person = Person.query.get(uuid.UUID(person_id))
        else:
            # Search by name (exact match)
            name_normalized = normalize_name(person_name)
            persons = Person.query.filter_by(name_normalized=name_normalized, layer='base').all()
            if len(persons) > 1:
                # Multiple matches - return them for user to choose
                return jsonify({
                    'matches': [{'id': str(p.id), 'name': p.name_original, 'name_amharic': p.name_amharic} for p in persons],
                    'message': 'Multiple people found with this name. Please specify person_id.'
                }), 200
            elif len(persons) == 0:
                return get_error_response('NOT_FOUND', 'Person not found')
            person = persons[0]
        
        if not person:
            return get_error_response('NOT_FOUND', 'Person not found')
        
        # Get all relationships involving this person
        parent_rels = Relationship.query.filter_by(parent_id=person.id).all()
        child_rels = Relationship.query.filter_by(child_id=person.id).all()
        
        # Delete relationships
        for rel in parent_rels:
            db.session.delete(rel)
        for rel in child_rels:
            db.session.delete(rel)
        
        # Delete the person
        db.session.delete(person)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Deleted person: {person.name_original}',
            'deleted_relationships': len(parent_rels) + len(child_rels)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error deleting person: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', f'Delete failed: {str(e)}', 500)


@admin_bp.route('/import/relationships', methods=['POST'])
def import_relationships():
    """Import relationships (admin only)"""
    auth_error = check_admin_token()
    if auth_error:
        return auth_error
    
    try:
        data = request.get_json()
        if not data or 'relationships' not in data:
            return get_error_response('BAD_REQUEST', 'Missing "relationships" array in request body')
        
        rels_data = data['relationships']
        if not isinstance(rels_data, list):
            return get_error_response('BAD_REQUEST', '"relationships" must be an array')
        
        created_count = 0
        rejected = []
        
        for idx, rel_data in enumerate(rels_data):
            try:
                # Validate required fields
                if 'parent_id' not in rel_data or 'child_id' not in rel_data:
                    rejected.append({'row': idx, 'reason': 'Missing parent_id or child_id'})
                    continue
                
                if 'relation_type' not in rel_data:
                    rejected.append({'row': idx, 'reason': 'Missing relation_type'})
                    continue
                
                # Validate UUIDs
                parent_id = rel_data['parent_id']
                child_id = rel_data['child_id']
                
                if not validate_uuid(parent_id) or not validate_uuid(child_id):
                    rejected.append({'row': idx, 'reason': 'Invalid UUID format'})
                    continue
                
                parent_id = uuid.UUID(parent_id)
                child_id = uuid.UUID(child_id)
                
                if parent_id == child_id:
                    rejected.append({'row': idx, 'reason': 'Parent and child cannot be the same'})
                    continue
                
                # Validate relation_type
                relation_type = rel_data['relation_type']
                if relation_type not in ['father', 'mother', 'parent']:
                    rejected.append({'row': idx, 'reason': f'Invalid relation_type: {relation_type}'})
                    continue
                
                # Check if people exist
                parent = Person.query.get(parent_id)
                child = Person.query.get(child_id)
                
                if not parent:
                    rejected.append({'row': idx, 'reason': f'Parent {parent_id} not found'})
                    continue
                if not child:
                    rejected.append({'row': idx, 'reason': f'Child {child_id} not found'})
                    continue
                
                # Check for circular relationship (simple check: A->B and B->A)
                existing_reverse = Relationship.query.filter_by(
                    parent_id=child_id,
                    child_id=parent_id
                ).first()
                
                if existing_reverse:
                    rejected.append({'row': idx, 'reason': 'Circular relationship detected'})
                    continue
                
                # Check if relationship already exists
                existing = Relationship.query.filter_by(
                    parent_id=parent_id,
                    child_id=child_id,
                    relation_type=relation_type
                ).first()
                
                if existing:
                    # Skip duplicate
                    continue
                
                # Create relationship
                relationship = Relationship(
                    parent_id=parent_id,
                    child_id=child_id,
                    relation_type=relation_type,
                    visibility=rel_data.get('visibility', 'public')
                )
                db.session.add(relationship)
                created_count += 1
                
            except Exception as e:
                rejected.append({'row': idx, 'reason': str(e)})
        
        db.session.commit()
        
        return jsonify({
            'created': created_count,
            'rejected': rejected,
            'total_processed': len(rels_data)
        })
    
    except Exception as e:
        db.session.rollback()
        logger.error(f'Error importing relationships: {e}', exc_info=True)
        return get_error_response('SERVER_ERROR', f'Import failed: {str(e)}', 500)

