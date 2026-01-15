# Handling Duplicate Names in Family Tree

When multiple people have the same name, the system uses several strategies to match the correct person.

## Problem

If you have two people both named "Ras Darge", the system needs to know which one you're referring to when creating relationships.

## Solutions

### 1. Use Birth Year (Recommended)

Include `birth_year` in your CSV to differentiate people with the same name:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,birth_year
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1800
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1850
```

The system will match based on:
1. Name match
2. Birth year match (if provided)

### 2. Use Death Year

If birth year is not available, use `death_year`:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,death_year
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1870
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1920
```

### 3. Use Direct Person ID (Most Reliable)

If you know the person's UUID from the database, you can specify it directly:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,person_id
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,a1b2c3d4-e5f6-7890-1234-567890abcdef
```

**How to get a person's ID:**
1. Search for the person on your site
2. Click on them
3. Check the URL: `#person/a1b2c3d4-e5f6-7890-1234-567890abcdef`
4. Or use the API: `GET /api/person/<id>`

### 4. Use Parent Context

The system also uses parent-child relationships to help disambiguate:
- If a child has a specific birth_year
- And the parent has multiple people with the same name
- The system will try to match based on which parent has that child

## Matching Priority

The system matches in this order:

1. **Direct ID** (if `person_id` is provided) - Most reliable
2. **Name + Birth Year** (if both match)
3. **Name + Death Year** (if birth year not available)
4. **Name + Parent Context** (if child's birth_year is known)
5. **Most Recent** (falls back to most recently created person with that name)

## CSV Format with All Options

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,birth_year,death_year,person_id
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1800,1870,
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1850,1920,
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ,1820,,
```

**Note:** 
- `person_id` is optional but most reliable
- `birth_year` and `death_year` are optional but help with matching
- You can use any combination of these fields

## Best Practices

### For Importing New Data:

1. **Always include birth_year** when available
2. **Include death_year** if birth_year is not available
3. **Use person_id** for people already in the database (most reliable)

### For Existing Duplicates:

If you already have duplicate names in your database:

1. **Export the data** to see all people with the same name
2. **Note their IDs** or birth/death years
3. **Use person_id** in your CSV for unambiguous matching
4. **Or add birth_year/death_year** to existing records and re-import

## Example: Importing Child of Duplicate Name Parent

If you have two "Ras Darge" people and want to add a child to the specific one:

**Option 1: Use person_id**
```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,person_id
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ,,a1b2c3d4-e5f6-7890-1234-567890abcdef
```

**Option 2: Use birth_year**
```csv
english_name,amharic_name,english_parent_name,amharic_parent_name,birth_year
Ras Darge,ራስ ዳርጌ,Parent Name,የአባት ስም,1800
Child 1,የልጅ 1,Ras Darge,ራስ ዳርጌ,1820
```

The system will match "Ras Darge" with birth_year=1800 to the child.

## Troubleshooting

### "Parent not found or ambiguous" error

This means there are multiple people with the same parent name and the system can't determine which one to use.

**Solution:**
- Add `birth_year` or `death_year` to the parent row in your CSV
- Or use `person_id` for the parent

### Wrong parent matched

If the system matched the wrong parent:

1. Check if you have multiple people with that name
2. Add `birth_year` or `person_id` to be more specific
3. Re-import with the correct information

### Finding Person IDs

To find a person's ID:
1. Search for them on your site
2. Click on them
3. Check the browser URL: `#person/<uuid>`
4. Or use the search API and check the response

## Summary

- **Best practice:** Always include `birth_year` when available
- **Most reliable:** Use `person_id` for people already in database
- **Fallback:** System uses most recently created person if no other match
- **Warning:** System logs a warning when it has to guess between duplicates

