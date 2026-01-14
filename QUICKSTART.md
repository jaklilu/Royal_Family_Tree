# Quick Start Guide

## Prerequisites

- Python 3.11+
- PostgreSQL database
- Node.js (optional, for local frontend server)

## Backend Setup (5 minutes)

1. **Navigate to backend:**
   ```bash
   cd backend
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   ```
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create `.env` file:**
   Copy the template from `ENV_VARIABLES.md` and fill in your values:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/royal_family_tree
   SECRET_KEY=your-random-secret-key
   ADMIN_TOKEN=your-admin-token
   ALLOWED_ORIGINS=http://localhost:5500
   ```

5. **Initialize database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```
   Or use the helper script:
   ```bash
   python setup.py
   ```

6. **Start server:**
   ```bash
   flask run
   ```
   Backend will be available at `http://localhost:5000`

## Frontend Setup (2 minutes)

1. **Navigate to frontend:**
   ```bash
   cd frontend
   ```

2. **Update API URL in `api.js`:**
   ```javascript
   const API_BASE_URL = 'http://localhost:5000';
   ```

3. **Start local server:**
   ```bash
   python -m http.server 5500
   ```
   Frontend will be available at `http://localhost:5500`

## Import Sample Data

Once your backend is running, you can import data using the admin endpoints:

```bash
# Import a person
curl -X POST http://localhost:5000/admin/import/people \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: your-admin-token" \
  -d '{
    "people": [
      {
        "name_original": "King Sahle Selassie",
        "birth_year": 1795,
        "gender": "male"
      }
    ]
  }'
```

## Testing

1. Open `http://localhost:5500` in your browser
2. The app should load the root person (or show an error if no data exists)
3. Click on people to navigate the tree
4. Use "Find Relationship" to search for connections

## Next Steps

- Import your historical book data using the admin endpoints
- Deploy to Render (backend) and Netlify (frontend)
- See `README.md` for deployment instructions

