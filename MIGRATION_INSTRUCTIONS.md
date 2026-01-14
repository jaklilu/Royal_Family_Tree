# Database Migration Instructions

## Add name_amharic Column

Since we added Amharic name support, you need to add the `name_amharic` column to your database.

## Option 1: Using Render Shell (Recommended)

1. Go to your Render dashboard
2. Open your Web Service
3. Click the **"Shell"** tab
4. Run:
   ```bash
   cd backend
   flask db upgrade
   ```

If that doesn't work (migrations not initialized), use Option 2.

## Option 2: Direct SQL (Quick)

1. Go to your Render dashboard
2. Open your **PostgreSQL database** (not the web service)
3. Click **"Connect"** or **"psql"**
4. Run this SQL:
   ```sql
   ALTER TABLE people ADD COLUMN IF NOT EXISTS name_amharic TEXT;
   ```

Or use the SQL file:
- Copy contents of `backend/add_name_amharic.sql`
- Paste into Render's database query interface
- Execute

## Option 3: Using Flask-Migrate (If migrations are set up)

If you have migrations initialized:

```bash
cd backend
flask db migrate -m "Add name_amharic field"
flask db upgrade
```

## Verify Migration

After running the migration, verify it worked:

```sql
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'people' AND column_name = 'name_amharic';
```

You should see `name_amharic | text` in the results.

## If Migration Fails

If you get errors, the column might already exist. You can check:

```sql
SELECT * FROM people LIMIT 1;
```

If the query works and includes `name_amharic`, you're all set!

## Next Steps

After migration:
1. ✅ Database is ready
2. ✅ Import tool is ready at `/admin-import.html`
3. ✅ Start importing your first batch!

