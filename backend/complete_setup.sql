-- COMPLETE SETUP - Run this entire script
-- This will create both tables and all constraints

-- ============================================
-- PART 1: Create people table
-- ============================================
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

-- Verify people table exists
SELECT 'People table created' as status;

-- ============================================
-- PART 2: Create relationships table
-- ============================================
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    relation_type VARCHAR(20) NOT NULL,
    visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- Verify relationships table exists
SELECT 'Relationships table created' as status;

-- ============================================
-- PART 3: Add constraints (only after tables exist)
-- ============================================

-- Remove existing constraints if they exist
DO $$ 
BEGIN
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'no_self_reference') THEN
        ALTER TABLE relationships DROP CONSTRAINT no_self_reference;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_relationship') THEN
        ALTER TABLE relationships DROP CONSTRAINT unique_relationship;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_relation_type') THEN
        ALTER TABLE relationships DROP CONSTRAINT valid_relation_type;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_parent') THEN
        ALTER TABLE relationships DROP CONSTRAINT fk_relationships_parent;
    END IF;
    IF EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_child') THEN
        ALTER TABLE relationships DROP CONSTRAINT fk_relationships_child;
    END IF;
END $$;

-- Add constraints
ALTER TABLE relationships ADD CONSTRAINT no_self_reference CHECK (parent_id != child_id);
ALTER TABLE relationships ADD CONSTRAINT unique_relationship UNIQUE (parent_id, child_id, relation_type);
ALTER TABLE relationships ADD CONSTRAINT valid_relation_type CHECK (relation_type IN ('father', 'mother', 'parent'));
ALTER TABLE relationships ADD CONSTRAINT fk_relationships_parent FOREIGN KEY (parent_id) REFERENCES people(id);
ALTER TABLE relationships ADD CONSTRAINT fk_relationships_child FOREIGN KEY (child_id) REFERENCES people(id);

SELECT 'Constraints added' as status;

-- ============================================
-- PART 4: Create indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

SELECT 'Indexes created' as status;

-- ============================================
-- PART 5: Final verification
-- ============================================
SELECT 'FINAL CHECK - Tables:' as info;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

