# Royal Family Tree - Phase 1

A read-only genealogy browser for exploring the royal family tree. Phase 1 provides free browsing of the base historical data. Phase 2 will enable paid extensions for users to attach their own family branches at leaf nodes (people with no children).

## Tech Stack

- **Backend**: Python 3.11, Flask, SQLAlchemy, PostgreSQL, Gunicorn (deployed on Render)
- **Frontend**: HTML/CSS/Vanilla JavaScript (deployed on Netlify)

## Project Structure

```
Royal_Family_Tree/
├── backend/
│   ├── app.py              # Flask application
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # API routes
│   ├── config.py           # Configuration
│   ├── requirements.txt    # Python dependencies
│   ├── Procfile            # Render deployment config
│   ├── .env.example        # Environment variables template
│   └── .gitignore          # Git ignore rules
├── frontend/
│   ├── index.html          # Main HTML
│   ├── api.js              # API client
│   ├── tree.js             # Tree rendering logic
│   └── styles.css          # Styling
└── README.md
```

## Local Development

### Backend Setup

1. **Create virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file in the `backend` directory:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/royal_family_tree
   SECRET_KEY=your-secret-key-here-change-in-production
   ADMIN_TOKEN=your-admin-token-here-change-in-production
   ALLOWED_ORIGINS=http://localhost:5500,http://127.0.0.1:5500
   ROOT_PERSON_ID=
   LOG_LEVEL=INFO
   ```

4. **Initialize database:**
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

5. **Run the server:**
   ```bash
   flask run
   # Or with gunicorn:
   gunicorn app:app
   ```

   Server will run on `http://localhost:5000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Update API_BASE_URL in api.js:**
   ```javascript
   const API_BASE_URL = 'http://localhost:5000';
   ```

3. **Start local server:**
   ```bash
   python -m http.server 5500
   ```

   Frontend will be available at `http://localhost:5500`

## Deployment

### Backend on Render

1. **Create a new Web Service on Render**

2. **Connect your repository**

3. **Configure the service:**
   - **Build Command**: `cd backend && pip install -r requirements.txt`
   - **Start Command**: `cd backend && gunicorn app:app`
   - **Environment**: Python 3
   - **Python Version**: Render automatically detects from `runtime.txt` in the root directory (already created)
     - No manual setting needed - Render reads `runtime.txt` automatically
     - If it's still using Python 3.13, try a manual redeploy after the latest commit

4. **Set environment variables in Render dashboard:**
   ```
   DATABASE_URL=postgresql://...
   SECRET_KEY=your-secret-key
   ADMIN_TOKEN=your-admin-token
   ALLOWED_ORIGINS=https://your-site.netlify.app
   ROOT_PERSON_ID=optional-uuid
   LOG_LEVEL=INFO
   ```

5. **Add PostgreSQL database:**
   - Create a PostgreSQL database in Render
   - Use the connection string as `DATABASE_URL`

6. **Run migrations:**
   - After first deployment, SSH into the service or use Render shell:
   ```bash
   cd backend
   export DATABASE_URL=your-database-url
   flask db upgrade
   ```

### Frontend on Netlify

1. **Build settings:**
   - **Base directory**: `frontend`
   - **Publish directory**: `frontend`
   - **Build command**: (leave empty, static site)

2. **Update API_BASE_URL in api.js:**
   ```javascript
   const API_BASE_URL = 'https://your-render-backend.onrender.com';
   ```

3. **Deploy:**
   - Connect repository
   - Netlify will auto-detect and deploy

## Admin Import

To import historical book data, use the admin endpoints:

### Import People

```bash
curl -X POST https://your-backend.onrender.com/admin/import/people \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: your-admin-token" \
  -d '{
    "people": [
      {
        "id": "optional-uuid",
        "name_original": "King Sahle Selassie",
        "birth_year": 1795,
        "death_year": 1847,
        "gender": "male"
      }
    ]
  }'
```

### Import Relationships

```bash
curl -X POST https://your-backend.onrender.com/admin/import/relationships \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-TOKEN: your-admin-token" \
  -d '{
    "relationships": [
      {
        "parent_id": "parent-uuid",
        "child_id": "child-uuid",
        "relation_type": "father"
      }
    ]
  }'
```

## API Endpoints

### Public Endpoints

- `GET /health` - Health check with database status
- `GET /api/root` - Get root person (King Sahle Selassie or oldest base person)
- `GET /api/search?q=...` - Search people by name (max 25 results)
- `GET /api/neighborhood/<person_id>` - Get 3-section view (parent, person, children)
- `GET /api/person/<person_id>` - Get person with all parents and children
- `GET /api/relationship?person1_id=...&person2_id=...` - Find shortest relationship path

### Admin Endpoints (Protected)

- `POST /admin/import/people` - Import people (requires X-ADMIN-TOKEN header)
- `POST /admin/import/relationships` - Import relationships (requires X-ADMIN-TOKEN header)

### Response Formats

All API endpoints return JSON. Errors follow this format:
```json
{
  "error": {
    "code": "NOT_FOUND|BAD_REQUEST|SERVER_ERROR",
    "message": "Error description"
  }
}
```

## Features

### Phase 1 (Current)

- ✅ Read-only browsing of base family tree
- ✅ Three-section view: parent, selected person, children
- ✅ Dynamic org-chart style connecting lines
- ✅ Search functionality
- ✅ Relationship finder (shortest path between two people)
- ✅ Mobile-first responsive design
- ✅ Leaf node indicators (preparation for Phase 2)

### Phase 2 (Future)

- User authentication
- Payment integration
- Ability to attach family trees at leaf nodes (people with no children)
- Photo uploads
- Extended family view (both sets of parents, multiple spouses)

## Data Model

### People Table
- `id` (UUID, primary key)
- `name_original` (TEXT, required)
- `name_normalized` (TEXT, indexed for search)
- `layer` (TEXT, default 'base')
- `birth_year` (INTEGER, nullable)
- `death_year` (INTEGER, nullable)
- `gender` (TEXT, nullable)
- `created_at` (TIMESTAMP)

### Relationships Table
- `id` (UUID, primary key)
- `parent_id` (UUID, FK to people.id, indexed)
- `child_id` (UUID, FK to people.id, indexed)
- `relation_type` (TEXT: 'father', 'mother', or 'parent')
- `visibility` (TEXT, default 'public')
- `created_at` (TIMESTAMP)

Constraints:
- No self-referential relationships
- Unique (parent_id, child_id, relation_type) combinations

## License

[Your License Here]
