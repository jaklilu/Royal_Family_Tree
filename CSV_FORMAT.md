# CSV Import Format

## Recommended Format (with Amharic names)

Use these column names in your CSV file:

```csv
english_name,amharic_name,english_parent_name,amharic_parent_name
King Sahle Selassie,ንጉሠ ሰለሰ,,
Haile Melekot,ሃይለ መለኮት,King Sahle Selassie,ንጉሠ ሰለሰ
Menelik II,ምኒልክ ዳግማዊ,Haile Melekot,ሃይለ መለኮት
```

## Column Descriptions

- **english_name** (required): The person's name in English
- **amharic_name** (optional): The person's name in Amharic
- **english_parent_name** (optional): Parent's English name (leave empty for root person)
- **amharic_parent_name** (optional): Parent's Amharic name (for reference/validation, not used for matching)

## Notes

- **Root person**: Leave `english_parent_name` and `amharic_parent_name` empty for the root ancestor
- **Parent matching**: The system uses `english_parent_name` to find and link the parent
- **Amharic parent name**: Included for reference but not used for matching (helps with data validation)
- **Both names display**: If `amharic_name` is provided, it will display below the English name on each card

## Example Excel Setup

| english_name | amharic_name | english_parent_name | amharic_parent_name |
|--------------|--------------|---------------------|---------------------|
| King Sahle Selassie | ንጉሠ ሰለሰ | | |
| Haile Melekot | ሃይለ መለኮት | King Sahle Selassie | ንጉሠ ሰለሰ |
| Menelik II | ምኒልክ ዳግማዊ | Haile Melekot | ሃይለ መለኮት |

## Import Process

1. Import all people first (all rows with `english_name`)
2. System automatically creates relationships using `english_parent_name`
3. Both English and Amharic names will display on cards

## Minimal Format (English only)

If you only have English names, you can use:

```csv
english_name,english_parent_name
King Sahle Selassie,
Haile Melekot,King Sahle Selassie
Menelik II,Haile Melekot
```

The `amharic_name` and `amharic_parent_name` columns are optional.

