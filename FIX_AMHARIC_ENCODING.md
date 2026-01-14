# Fixing Amharic Character Encoding Issues

## Problem
Amharic names appear as "?????" instead of proper Amharic characters.

## Root Causes
1. **Flask JSON encoding**: Flask's `jsonify()` defaults to `ensure_ascii=True`, which escapes non-ASCII characters
2. **CSV import encoding**: CSV files must be saved with UTF-8 encoding
3. **Database encoding**: PostgreSQL must use UTF-8 encoding
4. **Response headers**: HTTP responses must specify UTF-8 charset

## Fixes Applied

### 1. Backend (Flask) - ✅ Fixed
- Added `app.config['JSON_AS_ASCII'] = False` to preserve UTF-8 characters in JSON responses
- Added `response.charset = 'utf-8'` in after_request handler

### 2. Frontend CSV Import - ✅ Fixed
- Updated FileReader to explicitly use UTF-8: `reader.readAsText(file, 'UTF-8')`

### 3. Database - Check Required
PostgreSQL on Render should already use UTF-8, but verify:
```sql
SHOW server_encoding;
-- Should return: UTF8
```

### 4. CSV File Format - User Action Required
**IMPORTANT**: Your CSV file must be saved with UTF-8 encoding:

#### In Excel:
1. File → Save As
2. Choose "CSV UTF-8 (Comma delimited) (*.csv)" 
3. **NOT** "CSV (Comma delimited) (*.csv)" - that uses Windows-1252 encoding

#### In Google Sheets:
1. File → Download → Comma-separated values (.csv)
2. Google Sheets exports as UTF-8 by default, so this should work

#### Verify CSV Encoding:
Open your CSV in a text editor (Notepad++, VS Code) and check:
- File should show UTF-8 encoding
- Amharic characters should display correctly in the editor
- If you see "?????" in the editor, the file is not UTF-8

## Testing

### 1. Re-import Your Data
After fixing the CSV encoding:
1. Save your CSV as UTF-8
2. Re-import using the admin tool
3. Check if Amharic names display correctly

### 2. Check Database Directly
```sql
SELECT name_original, name_amharic FROM people LIMIT 5;
```
If Amharic names show correctly here but not in the frontend, it's a frontend display issue.

### 3. Check API Response
Visit: `https://royal-family-tree.onrender.com/api/person/<some-id>`
Check if `name_amharic` shows proper characters in the JSON response.

## If Still Not Working

### Option 1: Re-import with UTF-8 CSV
1. Export your Excel/Sheets as UTF-8 CSV
2. Delete existing data (optional, or just update)
3. Re-import using admin tool

### Option 2: Update Existing Records
If data is already in database with wrong encoding, you may need to:
1. Export correct UTF-8 CSV
2. Re-import (system will update existing records)

### Option 3: Manual Database Update
If only a few records are affected:
```sql
UPDATE people 
SET name_amharic = 'ንጉሠ ሰለሰ' 
WHERE name_original = 'King Sahle Selassie';
```

## Verification Checklist

- [ ] Backend code updated (JSON_AS_ASCII = False)
- [ ] CSV file saved as UTF-8
- [ ] Data re-imported with UTF-8 CSV
- [ ] Database shows correct Amharic characters
- [ ] API response shows correct Amharic characters
- [ ] Frontend displays correct Amharic characters

