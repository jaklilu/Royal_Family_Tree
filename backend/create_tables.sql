-- Initial database schema creation
-- Run this FIRST to create all tables

-- Create people table
CREATE TABLE IF NOT EXISTS people (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name_original TEXT NOT NULL,
    name_amharic TEXT,
    name_normalized TEXT NOT NULL,
    layer VARCHAR(50) NOT NULL DEFAULT 'base',
    birth_year INTEGER,
    death_year INTEGER,
    gender VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Create index on name_normalized for search
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);

-- Create index on created_at
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);

-- Create relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    relation_type VARCHAR(20) NOT NULL,
    visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    CONSTRAINT no_self_reference CHECK (parent_id != child_id),
    CONSTRAINT unique_relationship UNIQUE (parent_id, child_id, relation_type),
    CONSTRAINT valid_relation_type CHECK (relation_type IN ('father', 'mother', 'parent'))
);

-- Create foreign keys
ALTER TABLE relationships 
    ADD CONSTRAINT fk_relationships_parent 
    FOREIGN KEY (parent_id) REFERENCES people(id);

ALTER TABLE relationships 
    ADD CONSTRAINT fk_relationships_child 
    FOREIGN KEY (child_id) REFERENCES people(id);

-- Create indexes on relationships
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

-- Verify tables were created
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

