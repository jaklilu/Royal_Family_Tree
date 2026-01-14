-- SIMPLE: Create people table
-- Run this ENTIRE script at once

-- Drop table if it exists (optional - only if you want to start fresh)
-- DROP TABLE IF EXISTS people CASCADE;

-- Create people table
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

-- Create indexes (run these AFTER table is created)
CREATE INDEX idx_people_name_normalized ON people(name_normalized);
CREATE INDEX idx_people_created_at ON people(created_at);

-- Verify
SELECT 'People table created successfully!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'people';

