-- Create people table (if missing)
-- Run this if you only see 'relationships' in your table list

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

-- Create indexes on people table
CREATE INDEX IF NOT EXISTS idx_people_name_normalized ON people(name_normalized);
CREATE INDEX IF NOT EXISTS idx_people_created_at ON people(created_at);

-- Verify people table was created
SELECT 'People table created!' as status;
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

