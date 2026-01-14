# Database Setup Instructions

## Initial Database Creation

If you're getting "people table does not exist" error, you need to create the database tables first.

## Step 1: Create Tables

### Option A: Using SQL Script (Easiest)

1. Go to your Render dashboard
2. Open your **PostgreSQL database** (not the web service)
3. Click **"Connect"** or find the **"psql"** / **"Query"** option
4. Copy and paste the entire contents of `backend/create_tables.sql`
5. Execute the SQL

### Option B: Using Flask-Migrate (If you have local access)

If you're running locally or have shell access:

```bash
cd backend
flask db init          # Only needed once
flask db migrate -m "Initial schema"
flask db upgrade
```

### Option C: Using Render Shell

1. Go to Render dashboard → Your Web Service
2. Click **"Shell"** tab
3. Run:
   ```bash
   cd backend
   export DATABASE_URL=your-database-url-here
   flask db init
   flask db migrate -m "Initial schema"
   flask db upgrade
   ```

## Step 2: Verify Tables Were Created

Run this SQL to verify:

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('people', 'relationships');
```

You should see both `people` and `relationships` in the results.

## Step 3: Check Table Structure

Verify the people table has all columns:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'people';
```

You should see:
- id
- name_original
- name_amharic
- name_normalized
- layer
- birth_year
- death_year
- gender
- created_at

## Troubleshooting

### If you get permission errors:
- Make sure you're connected to the correct database
- Check that your database user has CREATE TABLE permissions

### If tables already exist:
- You can skip Step 1
- Just verify with Step 2

### If you need to start over:
```sql
-- WARNING: This deletes all data!
DROP TABLE IF EXISTS relationships;
DROP TABLE IF EXISTS people;
```
Then run `create_tables.sql` again.

## Next Steps

After tables are created:
1. ✅ Database is ready
2. ✅ You can now import data
3. ✅ Use the admin import tool at `/admin-import.html`

