-- STEP-BY-STEP SETUP
-- Run each section one at a time, in order
-- Wait for "Success" before moving to the next step

-- ============================================
-- STEP 1: Create people table
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

-- ============================================
-- STEP 2: Create relationships table
-- ============================================
CREATE TABLE IF NOT EXISTS relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    parent_id UUID NOT NULL,
    child_id UUID NOT NULL,
    relation_type VARCHAR(20) NOT NULL,
    visibility VARCHAR(20) NOT NULL DEFAULT 'public',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

-- ============================================
-- STEP 3: Verify tables exist (run this to check)
-- ============================================
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_name IN ('people', 'relationships');

-- ============================================
-- STEP 4: Add constraints to relationships
-- Only run this AFTER both tables exist!
-- ============================================

-- Check constraint: no self-reference
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'no_self_reference') THEN
        ALTER TABLE relationships ADD CONSTRAINT no_self_reference CHECK (parent_id != child_id);
    END IF;
END $$;

-- Unique constraint
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_relationship') THEN
        ALTER TABLE relationships ADD CONSTRAINT unique_relationship UNIQUE (parent_id, child_id, relation_type);
    END IF;
END $$;

-- Check constraint: valid relation type
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_relation_type') THEN
        ALTER TABLE relationships ADD CONSTRAINT valid_relation_type CHECK (relation_type IN ('father', 'mother', 'parent'));
    END IF;
END $$;

-- ============================================
-- STEP 5: Add foreign keys
-- Only run this AFTER both tables exist!
-- ============================================

-- Foreign key: parent_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_parent') THEN
        ALTER TABLE relationships ADD CONSTRAINT fk_relationships_parent FOREIGN KEY (parent_id) REFERENCES people(id);
    END IF;
END $$;

-- Foreign key: child_id
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_child') THEN
        ALTER TABLE relationships ADD CONSTRAINT fk_relationships_child FOREIGN KEY (child_id) REFERENCES people(id);
    END IF;
END $$;

-- ============================================
-- STEP 6: Create indexes
-- ============================================
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

-- ============================================
-- STEP 7: Final verification
-- ============================================
SELECT 'Setup Complete!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

