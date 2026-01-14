-- Safe database schema creation
-- This script creates tables in the correct order and handles existing tables

-- Step 1: Create people table first
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

-- Step 2: Create index on people table
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);

-- Step 3: Create relationships table (depends on people table)
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    relation_type VARCHAR(20) NOT NULL,
    visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Step 4: Add constraints to relationships table
-- Remove existing constraints if they exist (for re-running)
DO $$ 
BEGIN
    -- Drop constraints if they exist
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'no_self_reference') THEN
        ALTER TABLE relationships DROP CONSTRAINT no_self_reference;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_relationship') THEN
        ALTER TABLE relationships DROP CONSTRAINT unique_relationship;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_relation_type') THEN
        ALTER TABLE relationships DROP CONSTRAINT valid_relation_type;
    END IF;
END $$;

-- Add constraints
ALTER TABLE relationships 
    ADD CONSTRAINT no_self_reference CHECK (parent_id != child_id);

ALTER TABLE relationships 
    ADD CONSTRAINT unique_relationship UNIQUE (parent_id, child_id, relation_type);

ALTER TABLE relationships 
    ADD CONSTRAINT valid_relation_type CHECK (relation_type IN ('father', 'mother', 'parent'));

-- Step 5: Add foreign keys (after both tables exist)
-- Remove existing foreign keys if they exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_parent') THEN
        ALTER TABLE relationships DROP CONSTRAINT fk_relationships_parent;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_child') THEN
        ALTER TABLE relationships DROP CONSTRAINT fk_relationships_child;
    END IF;
END $$;

-- Add foreign keys
ALTER TABLE relationships 
    ADD CONSTRAINT fk_relationships_parent 
    FOREIGN KEY (parent_id) REFERENCES people(id);

ALTER TABLE relationships 
    ADD CONSTRAINT fk_relationships_child 
    FOREIGN KEY (child_id) REFERENCES people(id);

-- Step 6: Create indexes on relationships
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

-- Verify tables were created
SELECT 'Tables created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

