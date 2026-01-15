# Importing a Single Branch (e.g., Ras Darge and All Descendants)

This guide shows you how to import one person and all their descendants down through multiple generations.

## Strategy: Import All Generations at Once

You can import all generations in a single CSV file. The system will:
- Create all people first
- Then link relationships based on parent names
- Handle multiple generations automatically

## CSV Structure for Multiple Generations

Here's how to structure your CSV for Ras Darge and all descendants:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም
Child 1 of Ras Darge,የልጅ 1,Ras Darge,ራስ ዳርጌ
Child 2 of Ras Darge,የልጅ 2,Ras Darge,ራስ ዳርጌ
Grandchild 1 (child of Child 1),የልጅ ልጅ 1,Child 1 of Ras Darge,የልጅ 1
Grandchild 2 (child of Child 1),የልጅ ልጅ 2,Child 1 of Ras Darge,የልጅ 1
Grandchild 3 (child of Child 2),የልጅ ልጅ 3,Child 2 of Ras Darge,የልጅ 2
Great-Grandchild 1,የልጅ ልጅ ልጅ 1,Grandchild 1 (child of Child 1),የልጅ ልጅ 1
Great-Grandchild 2,የልጅ ልጅ ልጅ 2,Grandchild 1 (child of Child 1),የልጅ ልጅ 1
```

## Step-by-Step Process

### Step 1: Prepare Your Data in Excel/Sheets

1. **Create your CSV with these columns:**
   - `english_name` - Person's English name
   - `amharic_name` - Person's Amharic name (optional)
   - `english_parent_name` - Parent's English name (must match exactly)
   - `amharic_parent_name` - Parent's Amharic name (optional, for reference)

2. **Add all generations:**
   - Row 1: Ras Darge (with his parent if he's not already in the database)
   - Rows 2-N: All his children
   - Rows N+1: All grandchildren (parent = child's name)
   - Rows N+2: All great-grandchildren (parent = grandchild's name)
   - Continue for all generations

3. **Important:** 
   - `english_parent_name` must match the `english_name` exactly (case-sensitive)
   - You can include all generations in one CSV file
   - Order doesn't matter - the system handles it

### Step 2: Example Structure

Here's a concrete example:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
Ras Darge,ራስ ዳርጌ,King Sahle Selassie,ንጉሠ ሰለሰ
Son 1,የልጅ 1,Ras Darge,ራስ ዳርጌ
Son 2,የልጅ 2,Ras Darge,ራስ ዳርጌ
Daughter 1,የሴት ልጅ 1,Ras Darge,ራስ ዳርጌ
Grandson 1,የልጅ ልጅ 1,Son 1,የልጅ 1
Grandson 2,የልጅ ልጅ 2,Son 1,የልጅ 1
Granddaughter 1,የሴት ልጅ ልጅ 1,Son 2,የልጅ 2
Great-Grandson 1,የልጅ ልጅ ልጅ 1,Grandson 1,የልጅ ልጅ 1
Great-Grandson 2,የልጅ ልጅ ልጅ 2,Grandson 1,የልጅ ልጅ 1
```

### Step 3: Save as UTF-8 CSV

**In Excel:**
1. File → Save As
2. Choose: **"CSV UTF-8 (Comma delimited) (*.csv)"**
3. **NOT** "CSV (Comma delimited)" - that uses wrong encoding
4. Save the file

### Step 4: Import Using Admin Tool

1. **Go to admin import page:**
   - `https://royal-family-tree.netlify.app/admin-import.html`

2. **Configure:**
   - Backend URL: `https://royal-family-tree.onrender.com`
   - Admin Token: Your `ADMIN_TOKEN` from Render
   - Batch Size: 100 (default)

3. **Upload and import:**
   - Upload your CSV file
   - Click "Start Import"
   - Watch the progress

### Step 5: Verify the Branch

After import:

1. **Search for Ras Darge:**
   - Use the search function
   - Click on "Ras Darge"

2. **Navigate down the tree:**
   - Click on his children
   - Click on grandchildren
   - Continue down to verify all generations are connected

3. **Check relationships:**
   - Each person should show their parent above
   - Each person should show their children below

## Tips for Success

### 1. Name Matching is Critical

- `english_parent_name` must match `english_name` **exactly**
- Case-sensitive: "Ras Darge" ≠ "ras darge" ≠ "RAS DARGE"
- Spaces matter: "Ras Darge" ≠ "RasDarge"
- Check spelling carefully

### 2. If Ras Darge Already Exists

If Ras Darge is already in your database:
- You can still include him in the CSV (system will update, not duplicate)
- Or skip him and start with his children
- Make sure his children's `english_parent_name` matches his exact name in the database

### 3. Verify Parent Names

Before importing, check:
- Search for the parent name in your existing database
- Make sure the `english_parent_name` in your CSV matches exactly
- Use the search function to find the exact spelling

### 4. Import Order Doesn't Matter

You can include:
- All generations in one CSV (recommended)
- Or import generation by generation
- The system handles relationships automatically

### 5. Large Branches

If you have a very large branch (100+ people):
- The import tool processes in batches of 100
- It will handle it automatically
- Just wait for it to complete

## Troubleshooting

### "Parent not found" errors

- Check the exact spelling of parent names
- Use the search function to find the correct name
- Update your CSV with the exact name

### Relationships not showing

- Verify parent names match exactly
- Check the import logs for rejected rows
- Re-import if needed (system updates existing records)

### Duplicate people

- The system updates existing people if names match
- If you see duplicates, check for spelling variations
- You may need to manually fix in the database

## Next Steps

After importing Ras Darge's branch:

1. **Verify the branch is complete**
2. **Pick another child** and repeat the process
3. **Continue until all branches are imported**

This systematic approach helps you build out the entire tree branch by branch!

