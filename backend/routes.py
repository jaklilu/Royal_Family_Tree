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
        
        children = [rel.child for rel in child_rels]
        children = sorted(children, key=lambda p: p.name_normalized)
        
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
        
        children = sorted([rel.child for rel in child_rels], key=lambda p: p.name_normalized)
        
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


@api_bp.route('/api/relationship', methods=['GET'])
def get_relationship():
    """Find shortest path between two people using BFS"""
    person1_id = request.args.get('person1_id')
    person2_id = request.args.get('person2_id')
    
    if not person1_id or not person2_id:
        return get_error_response('BAD_REQUEST', 'Both person1_id and person2_id are required')
    
    if not validate_uuid(person1_id) or not validate_uuid(person2_id):
        return get_error_response('BAD_REQUEST', 'Invalid person ID format')
    
    if person1_id == person2_id:
        return jsonify({
            'found': True,
            'path': [],
            'common_ancestor': None,
            'message': 'Same person'
        })
    
    try:
        person1 = Person.query.filter_by(id=person1_id, layer='base').first()
        person2 = Person.query.filter_by(id=person2_id, layer='base').first()
        
        if not person1 or not person2:
            return get_error_response('NOT_FOUND', 'One or both persons not found')
        
        # BFS to find shortest path (undirected graph)
        path = bfs_shortest_path(person1_id, person2_id)
        
        if path:
            # Find common ancestor (first shared node when walking up from both)
            common_ancestor = find_common_ancestor(person1_id, person2_id)
            
            return jsonify({
                'found': True,
                'path': [{'id': str(p_id), 'name': get_person_name(p_id)} for p_id in path],
                'common_ancestor': common_ancestor.to_dict() if common_ancestor else None
            })
        else:
            return jsonify({
                'found': False,
                'path': [],
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
    """Find common ancestor by walking up both trees"""
    # Get all ancestors of person1
    ancestors1 = get_all_ancestors(person1_id)
    
    # Walk up person2's tree until we find a match
    current = person2_id
    visited = set()
    
    while current:
        if current in ancestors1:
            return Person.query.get(current)
        
        if current in visited:
            break
        visited.add(current)
        
        # Get parent
        parent_rel = Relationship.query.filter_by(
            child_id=current,
            visibility='public'
        ).first()
        
        if parent_rel:
            current = parent_rel.parent_id
        else:
            break
    
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
                if 'name_original' not in person_data:
                    rejected.append({'row': idx, 'reason': 'Missing name_original'})
                    continue
                
                name_original = person_data['name_original'].strip()
                if not name_original:
                    rejected.append({'row': idx, 'reason': 'Empty name_original'})
                    continue
                
                # Amharic name (optional)
                name_amharic = person_data.get('name_amharic', '').strip() or None
                
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

