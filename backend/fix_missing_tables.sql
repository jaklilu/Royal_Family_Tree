-- Fix script: Creates missing tables
-- Run this if you get "table does not exist" errors

-- Check and create people table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'people') THEN
        CREATE TABLE people (
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
        CREATE INDEX idx_people_name_normalized ON people(name_normalized);
        CREATE INDEX idx_people_created_at ON people(created_at);
        RAISE NOTICE 'Created people table';
    ELSE
        RAISE NOTICE 'people table already exists';
    END IF;
END $$;

-- Check and create relationships table if missing
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'relationships') THEN
        CREATE TABLE relationships (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            parent_id UUID NOT NULL,
            child_id UUID NOT NULL,
            relation_type VARCHAR(20) NOT NULL,
            visibility VARCHAR(20) NOT NULL DEFAULT 'public',
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
        RAISE NOTICE 'Created relationships table';
    ELSE
        RAISE NOTICE 'relationships table already exists';
    END IF;
END $$;

-- Add constraints to relationships (safe - won't fail if they exist)
DO $$ 
BEGIN
    -- Add check constraints
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'no_self_reference') THEN
        ALTER TABLE relationships ADD CONSTRAINT no_self_reference CHECK (parent_id != child_id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'unique_relationship') THEN
        ALTER TABLE relationships ADD CONSTRAINT unique_relationship UNIQUE (parent_id, child_id, relation_type);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_relation_type') THEN
        ALTER TABLE relationships ADD CONSTRAINT valid_relation_type CHECK (relation_type IN ('father', 'mother', 'parent'));
    END IF;
    
    -- Add foreign keys
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_parent') THEN
        ALTER TABLE relationships ADD CONSTRAINT fk_relationships_parent FOREIGN KEY (parent_id) REFERENCES people(id);
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'fk_relationships_child') THEN
        ALTER TABLE relationships ADD CONSTRAINT fk_relationships_child FOREIGN KEY (child_id) REFERENCES people(id);
    END IF;
END $$;

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_relationships_parent_id ON relationships(parent_id);
CREATE INDEX IF NOT EXISTS idx_relationships_child_id ON relationships(child_id);

-- Verify
SELECT 'Setup complete! Tables:' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

