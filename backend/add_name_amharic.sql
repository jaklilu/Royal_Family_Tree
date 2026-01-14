-- Migration script to add name_amharic column
-- Run this in your PostgreSQL database (Render or local)

-- Add the name_amharic column
ALTER TABLE people ADD COLUMN IF NOT EXISTS name_amharic TEXT;

-- Verify the column was added
-- SELECT column_name, data_type 
-- FROM information_schema.columns 
-- WHERE table_name = 'people' AND column_name = 'name_amharic';

