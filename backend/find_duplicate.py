"""
Helper script to find duplicate person entries.
Run this to identify duplicates before deletion.
"""
import os
import sys
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from app import create_app, db
from models import Person, Relationship

app = create_app()

with app.app_context():
    # Search for "Ras Asrate" variations
    search_terms = [
        "ras asrate",
        "ras asrat",
        "asrate",
        "asrat"
    ]
    
    print("Searching for duplicate entries...")
    print("=" * 60)
    
    all_matches = []
    for term in search_terms:
        normalized = ' '.join(term.lower().split())
        matches = Person.query.filter(
            Person.name_normalized.like(f'%{normalized}%')
        ).all()
        all_matches.extend(matches)
    
    # Remove duplicates
    unique_matches = {p.id: p for p in all_matches}.values()
    
    # Filter for "Ras Asrate" specifically
    ras_asrate_matches = [
        p for p in unique_matches 
        if 'asrate' in p.name_normalized or 'asrat' in p.name_normalized
    ]
    
    print(f"\nFound {len(ras_asrate_matches)} potential matches:\n")
    
    for person in ras_asrate_matches:
        # Count relationships
        parent_count = Relationship.query.filter_by(parent_id=person.id).count()
        child_count = Relationship.query.filter_by(child_id=person.id).count()
        
        print(f"ID: {person.id}")
        print(f"  English Name: {person.name_original}")
        print(f"  Amharic Name: {person.name_amharic}")
        print(f"  Created: {person.created_at}")
        print(f"  Relationships: {parent_count} as parent, {child_count} as child")
        print(f"  Total relationships: {parent_count + child_count}")
        print("-" * 60)
    
    # Identify the duplicate (the one with "the prince" in lowercase)
    duplicate = None
    correct = None
    
    for person in ras_asrate_matches:
        if 'the prince' in person.name_original.lower():
            duplicate = person
        elif 'prince' in person.name_original.lower() and 'the prince' not in person.name_original.lower():
            correct = person
    
    if duplicate and correct:
        print("\n" + "=" * 60)
        print("DUPLICATE IDENTIFIED:")
        print(f"  DUPLICATE (to DELETE): {duplicate.id}")
        print(f"    Name: {duplicate.name_original}")
        print(f"    Amharic: {duplicate.name_amharic}")
        print(f"    Relationships: {Relationship.query.filter_by(parent_id=duplicate.id).count() + Relationship.query.filter_by(child_id=duplicate.id).count()}")
        print(f"\n  CORRECT (to KEEP): {correct.id}")
        print(f"    Name: {correct.name_original}")
        print(f"    Amharic: {correct.name_amharic}")
        print(f"    Relationships: {Relationship.query.filter_by(parent_id=correct.id).count() + Relationship.query.filter_by(child_id=correct.id).count()}")
        print("\n" + "=" * 60)
        print(f"\nTo delete the duplicate, use this person_id: {duplicate.id}")
    else:
        print("\nCould not automatically identify duplicate. Please review the list above.")

