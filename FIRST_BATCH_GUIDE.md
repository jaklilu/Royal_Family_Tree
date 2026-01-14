# First Batch Import Guide

## Step 1: Prepare Your Excel File

1. Open Excel (or Google Sheets)
2. Create these column headers in Row 1:
   ```
   A1: english_name
   B1: amharic_name
   C1: english_parent_name
   D1: amharic_parent_name
   ```

## Step 2: Add Your First Batch

Start with King Sahle Selassie and his 15 children:

### Row 2 (Root Person):
```
A2: King Sahle Selassie
B2: ንጉሠ ሰለሰ
C2: (leave empty - he's the root)
D2: (leave empty)
```

### Rows 3-17 (His 15 Children):
```
A3: [Child 1 English Name]
B3: [Child 1 Amharic Name]
C3: King Sahle Selassie
D3: ንጉሠ ሰለሰ

A4: [Child 2 English Name]
B4: [Child 2 Amharic Name]
C4: King Sahle Selassie
D4: ንጉሠ ሰለሰ

... (continue for all 15 children)
```

## Step 3: Save as CSV

1. File → Save As
2. Choose "CSV (Comma delimited) (*.csv)"
3. Name it: `royal_family_batch1.csv`
4. Save it

## Step 4: Import Using Web Tool

### Option A: Web Import Tool (Recommended)

1. **Open the admin import page:**
   - Go to: `https://your-netlify-site.netlify.app/admin-import.html`
   - Or if local: `http://localhost:5500/admin-import.html`

2. **Configure:**
   - Backend URL: `https://your-render-backend.onrender.com`
   - Admin Token: (your admin token from Render environment variables)
   - Batch Size: 100 (default is fine)

3. **Upload CSV:**
   - Click "Choose CSV File" or drag & drop your `royal_family_batch1.csv`
   - The tool will show: "Loaded X people and X relationships"

4. **Start Import:**
   - Click "Start Import"
   - Watch the progress and logs

### Option B: Using API Directly (Advanced)

If you prefer using curl or a script:

```bash
# First, convert CSV to JSON format
# Then use the combined import endpoint:

curl -X POST https://your-backend.onrender.com/admin/import/combined \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: your-admin-token" \
  -d @batch1.json
```

## Step 5: Verify Import

After import, test it:

1. **Check the tree view:**
   - Go to your main site
   - You should see King Sahle Selassie in the center
   - His 15 children should appear below

2. **Test search:**
   - Use the search to find any person
   - Try searching by English or Amharic name

3. **Test navigation:**
   - Click on any child
   - That child should move to center
   - King Sahle Selassie should appear at top

## Step 6: Continue with Next Batch

Once the first batch works:

1. **Pick one child** (e.g., your great-great-great-great grandfather)
2. **Add their descendants** to a new CSV or continue in the same file
3. **Import again** - the system will update existing people and add new ones

## Troubleshooting

### If import fails:
- Check the logs in the import tool
- Verify your admin token is correct
- Make sure CSV format matches exactly
- Check that parent names match exactly (case-sensitive)

### If relationships don't work:
- Verify `english_parent_name` matches exactly (including spaces, capitalization)
- Check that the parent was imported before the child
- Look at the "rejected" list in the import results

## Quick Template

Here's a minimal template to get started:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
King Sahle Selassie,ንጉሠ ሰለሰ,,
```

Just add rows below this for the children!

