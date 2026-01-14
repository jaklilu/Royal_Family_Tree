# Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/royal_family_tree

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ADMIN_TOKEN=your-admin-token-here-change-in-production

# CORS
ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500,https://your-site.netlify.app

# Optional: Root person ID (UUID)
ROOT_PERSON_ID=

# Logging
LOG_LEVEL=INFO
```

## Variable Descriptions

- **DATABASE_URL**: PostgreSQL connection string
- **SECRET_KEY**: Flask secret key for sessions (generate a random string)
- **ADMIN_TOKEN**: Token for admin import endpoints (set in X-ADMIN-TOKEN header)
- **ALLOWED_ORIGINS**: Comma-separated list of allowed CORS origins
- **ROOT_PERSON_ID**: Optional UUID of the root person (if not set, uses oldest base person)
- **LOG_LEVEL**: Logging level (DEBUG, INFO, WARNING, ERROR)

