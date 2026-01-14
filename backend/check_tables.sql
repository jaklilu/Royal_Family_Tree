-- Check what tables exist in your database
-- Run this first to see current state

SELECT 
    table_name,
    'EXISTS' as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;

-- If you see both tables, you're good!
-- If you see only one or none, run create_tables_safe.sql

