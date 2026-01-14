# Final Database Setup - Step by Step

## Current Status
- ✅ `relationships` table exists
- ❌ `people` table is missing

## Solution: Create people table

### Step 1: Run this SQL (copy the entire block)

```sql
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
```

**Important:** 
- Remove `IF NOT EXISTS` - just use `CREATE TABLE people`
- Run this statement alone first
- Wait for "Success" message

### Step 2: After table is created, run indexes

```sql
CREATE INDEX idx_people_name_normalized ON people(name_normalized);
CREATE INDEX idx_people_created_at ON people(created_at);
```

### Step 3: Verify both tables exist

```sql
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships')
ORDER BY table_name;
```

You should see:
- `people`
- `relationships`

## If CREATE TABLE fails

Try this alternative (without IF NOT EXISTS):

```sql
-- Check if table exists first
SELECT EXISTS (
    SELECT FROM information_schema.tables 
    WHERE table_schema = 'public' 
    AND table_name = 'people'
);
```

If it returns `false`, then run:

```sql
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
```

## After Both Tables Exist

1. ✅ Database is ready
2. ✅ You can import data
3. ✅ Go to `/admin-import.html` to start importing

