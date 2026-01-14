from sqlalchemy import Column, String, DateTime, ForeignKey, CheckConstraint, UniqueConstraint, Integer, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

# Import db from app - this works because app.py creates db before importing models
from app import db


class Person(db.Model):
    __tablename__ = 'people'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name_original = Column(Text, nullable=False)  # English name
    name_amharic = Column(Text, nullable=True)  # Amharic name (optional)
    name_normalized = Column(Text, nullable=False, index=True)
    layer = Column(String(50), default='base', nullable=False)
    birth_year = Column(Integer, nullable=True)
    death_year = Column(Integer, nullable=True)
    gender = Column(String(10), nullable=True)  # 'male', 'female', or null
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    parent_relationships = relationship('Relationship', foreign_keys='Relationship.child_id', back_populates='child')
    child_relationships = relationship('Relationship', foreign_keys='Relationship.parent_id', back_populates='parent')
    
    def to_dict(self):
        return {
            'id': str(self.id),
            'name': self.name_original,  # English name
            'name_amharic': self.name_amharic if self.name_amharic else None
        }
    
    def __repr__(self):
        return f'<Person {self.name_original}>'


class Relationship(db.Model):
    __tablename__ = 'relationships'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    parent_id = Column(UUID(as_uuid=True), ForeignKey('people.id'), nullable=False, index=True)
    child_id = Column(UUID(as_uuid=True), ForeignKey('people.id'), nullable=False, index=True)
    relation_type = Column(String(20), nullable=False)  # 'father', 'mother', 'parent'
    visibility = Column(String(20), default='public', nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    parent = relationship('Person', foreign_keys=[parent_id], back_populates='child_relationships')
    child = relationship('Person', foreign_keys=[child_id], back_populates='parent_relationships')
    
    __table_args__ = (
        CheckConstraint('parent_id != child_id', name='no_self_reference'),
        UniqueConstraint('parent_id', 'child_id', 'relation_type', name='unique_relationship'),
        CheckConstraint("relation_type IN ('father', 'mother', 'parent')", name='valid_relation_type'),
    )
    
    def __repr__(self):
        return f'<Relationship {self.parent_id} -> {self.child_id} ({self.relation_type})>'

