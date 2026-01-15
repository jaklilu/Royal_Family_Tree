# Handling Duplicate Names (Names Only, No Dates)

Since you only have names (and sometimes titles), the system uses smart matching based on **import order** and **parent-child relationship context**.

## How It Works

### 1. Import Order Matching

When you import a branch (e.g., Ras Darge and all descendants), the system:
- Matches people based on the order they appear in your CSV
- If a person appears earlier in the import, they're likely an ancestor
- Uses the most recently created person with that name (likely from your previous imports)

**Example:**
```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ
Child 2,የልጅ 2,Ras Darge,ራስ ዳርጌ
```

If there are two "Ras Darge" people in the database:
- The system will match to the one that was most recently created
- This works well when importing branch by branch

### 2. Parent-Child Relationship Context

When linking a child to a parent with a duplicate name, the system:
- Checks if any parent with that name already has this child
- Checks if any parent has other children (indicating it's the right family)
- Uses this context to pick the correct parent

**Example:**
If you're importing "Child 1" with parent "Ras Darge":
- System checks which "Ras Darge" already has "Child 1" → uses that one
- Or checks which "Ras Darge" has other children → likely the right family

### 3. Direct Person ID (Most Reliable)

If you know the person's UUID, you can specify it directly:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,person_id
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,a1b2c3d4-e5f6-7890-1234-567890abcdef
```

**How to get a person's ID:**
1. Search for them on your site
2. Click on them
3. Check the URL: `#person/a1b2c3d4-e5f6-7890-1234-567890abcdef`
4. Copy that UUID and use it in your CSV

## Best Practices

### 1. Import Branch by Branch

Import one complete branch at a time:
- Import all of Ras Darge's descendants together
- Then import another branch
- This helps the system match correctly based on import order

### 2. Use Consistent Naming

- Use the exact same name spelling throughout
- Include titles consistently (e.g., always "Ras Darge" not sometimes "Ras Darge" and sometimes "Darge")

### 3. Verify After Each Import

After importing a branch:
1. Search for the root person
2. Navigate down the tree
3. Verify all relationships are correct
4. If wrong matches occurred, note the person IDs and use them in future imports

### 4. Use Person ID for Ambiguous Cases

If you encounter issues with duplicate names:
1. Find the person's ID (from the URL when you click on them)
2. Add a `person_id` column to your CSV
3. Use the ID for that specific person

## CSV Format

### Basic Format (Names Only)
```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ
Child 2,የልጅ 2,Ras Darge,ራስ ዳርጌ
```

### With Person ID (For Ambiguous Cases)
```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,person_id
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,a1b2c3d4-e5f6-7890-1234-567890abcdef
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ,
```

## How Matching Works (Priority Order)

1. **Direct ID** (if `person_id` provided) - Most reliable
2. **Name + Existing Relationship** (if parent already has this child)
3. **Name + Family Context** (if parent has other children, likely same family)
4. **Name + Import Order** (most recently created person with that name)
5. **Most Recent** (falls back to most recently created)

## Troubleshooting

### Wrong Parent Matched

If the system matched the wrong parent:

1. **Find the correct person's ID:**
   - Search for them on your site
   - Click on them
   - Copy the UUID from the URL

2. **Add person_id to your CSV:**
   ```csv
   english_name,amharic_name,english_parent_name,amharic_parent_name,person_id
   Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ,correct-parent-uuid-here
   ```

3. **Re-import with the person_id**

### "Parent not found" Error

This usually means:
- The parent name doesn't match exactly (check spelling, case, spaces)
- Or the parent hasn't been imported yet

**Solution:**
- Make sure parent is imported before children
- Check exact spelling matches

### Multiple Matches Warning

If you see a warning about multiple matches:
- The system is using its best guess (most recent person)
- Verify the relationships after import
- Use `person_id` for future imports to be explicit

## Summary

- **No dates needed:** System uses import order and relationship context
- **Import branch by branch:** Helps with correct matching
- **Use person_id when needed:** For ambiguous cases, get the ID from the URL
- **Verify after import:** Check relationships to ensure correctness

The system is designed to work with names only, using smart context matching!

