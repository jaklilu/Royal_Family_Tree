-- QUICK SETUP: Copy and paste this entire script into your SQL editor
-- This will create both tables safely

-- Step 1: Create people table
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

-- Step 2: Create relationships table
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    relation_type VARCHAR(20) NOT NULL,
    visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Step 3: Add constraints to relationships
ALTER TABLE relationships 
    ADD CONSTRAINT IF NOT EXISTS no_self_reference 
    CHECK (parent_id != child_id);

ALTER TABLE relationships 
    ADD CONSTRAINT IF NOT EXISTS unique_relationship 
    UNIQUE (parent_id, child_id, relation_type);

ALTER TABLE relationships 
    ADD CONSTRAINT IF NOT EXISTS valid_relation_type 
    CHECK (relation_type IN ('father', 'mother', 'parent'));

-- Step 4: Add foreign keys
ALTER TABLE relationships 
    ADD CONSTRAINT IF NOT EXISTS fk_relationships_parent 
    FOREIGN KEY (parent_id) REFERENCES people(id);

ALTER TABLE relationships 
    ADD CONSTRAINT IF NOT EXISTS fk_relationships_child 
    FOREIGN KEY (child_id) REFERENCES people(id);

-- Step 5: Create indexes
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

-- Step 6: Verify (run this after the above)
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';

