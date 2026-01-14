# Royal Family Tree - Project Context

## Project Overview

This is a **Phase 1** implementation of a read-only genealogy browser for exploring the royal family tree. The project is designed to allow users to browse historical family data from a book, with Phase 2 planned to enable paid extensions where users can attach their own family branches at leaf nodes (people with no children).

## Project Structure

```
Royal_Family_Tree/
├── backend/                    # Flask backend (deployed on Render)
│   ├── app.py                 # Flask application factory
│   ├── models.py              # SQLAlchemy models (Person, Relationship)
│   ├── routes.py              # API endpoints (public + admin)
│   ├── config.py              # Configuration management
│   ├── requirements.txt       # Python dependencies
│   ├── runtime.txt            # Python version pin (3.11.9)
│   ├── Procfile               # Render deployment config
│   ├── setup.py               # Database initialization helper
│   ├── ENV_VARIABLES.md       # Environment variables reference
│   └── .gitignore             # Git ignore rules
├── frontend/                   # Static frontend (deployed on Netlify)
│   ├── index.html             # Main HTML with tree view and relationship finder
│   ├── api.js                 # API client with error handling
│   ├── tree.js                # Tree rendering with SVG connecting lines
│   └── styles.css             # Mobile-first responsive styling
├── README.md                   # Complete project documentation
├── QUICKSTART.md              # Quick start guide
├── context.md                  # This file - project context
└── .gitignore                 # Root gitignore
```

## What Has Been Implemented

### Backend (Flask + PostgreSQL)

**Models:**
- `Person` model with fields:
  - id (UUID, primary key)
  - name_original (required)
  - name_normalized (indexed for search)
  - layer (default 'base', prepared for Phase 2)
  - birth_year, death_year, gender (optional)
  - created_at timestamp
- `Relationship` model with fields:
  - parent_id, child_id (UUIDs, indexed)
  - relation_type ('father', 'mother', 'parent')
  - visibility (default 'public')
  - Constraints: no self-reference, unique relationships

**API Endpoints (Public):**
- `GET /health` - Health check with database status
- `GET /api/root` - Get root person (uses ROOT_PERSON_ID env var or oldest base person)
- `GET /api/search?q=...` - Search people by name (max 25 results, ranked: exact > starts with > contains)
- `GET /api/neighborhood/<person_id>` - 3-section view (parent, person, children)
  - Returns exactly ONE parent (prefers father > mother > any)
  - Includes `is_leaf` flag for Phase 2 attachment points
- `GET /api/person/<person_id>` - Full person details with all parents and children
- `GET /api/relationship?person1_id=...&person2_id=...` - Find shortest path using BFS

**Admin Endpoints (Protected with X-ADMIN-TOKEN):**
- `POST /admin/import/people` - Import/upsert people
- `POST /admin/import/relationships` - Import relationships with validation

**Features:**
- CORS configured for frontend origins
- Input validation (UUID format, query length limits)
- Error handling with standardized JSON error responses
- Request logging
- Cache headers for read-only API (5 minutes)
- Database health checks

### Frontend (Vanilla JavaScript)

**Tree View:**
- 3-section layout: parent (top), selected person (center), children (bottom)
- Dynamic SVG connecting lines (org-chart style)
  - Single parent: vertical line to center
  - Single child: direct line from center
  - Multiple children: horizontal bus line with vertical drops
- Click navigation: click parent/child to navigate
- Responsive grid for children (4 per row on desktop, wraps on mobile)
- Leaf node indicators (shows "Attachment point for Phase 2")
- Loading states and error handling
- URL hash routing (#/person/<id>)

**Relationship Finder:**
- Two searchable inputs with autocomplete
- Debounced search (300ms)
- Displays relationship path with arrows
- Shows common ancestor if found

**Styling:**
- Mobile-first responsive design
- Clean, modern UI with gradient center card
- Smooth transitions and hover effects
- Accessible color scheme

## Key Decisions Made

1. **Technology Stack:**
   - Backend: Flask (lightweight, flexible)
   - Database: PostgreSQL (robust, scalable)
   - Frontend: Vanilla JS (no framework dependencies, fast)
   - Deployment: Render (backend) + Netlify (frontend)

2. **Data Model:**
   - UUID primary keys (better for distributed systems)
   - Normalized names for search (lowercase, trimmed)
   - Layer separation ('base' for Phase 1, ready for user layers in Phase 2)
   - Visibility field (prepared for future gating)

3. **API Design:**
   - RESTful endpoints
   - Standardized error format
   - Read-only for Phase 1 (admin endpoints for data import only)
   - Search ranking: exact > starts with > contains

4. **Frontend Architecture:**
   - No build step (static files, fast deployment)
   - SVG for connecting lines (dynamic, responsive)
   - Debounced search (performance)
   - Hash-based routing (simple, no server config needed)

## Current Status

### ✅ Completed
- [x] Backend API implementation (all endpoints)
- [x] Frontend UI implementation (tree view + relationship finder)
- [x] Database models with constraints
- [x] Error handling and validation
- [x] Documentation (README, QUICKSTART)
- [x] Git repository setup and initial push
- [x] Render deployment configuration (Procfile, runtime.txt)

### 🔧 Fixed Issues
- **Render Deployment Error - Python/SQLAlchemy Compatibility (2025-01-XX):** Fixed SQLAlchemy 2.0.23 + Python 3.13 compatibility issue
  - Created `runtime.txt` to pin Python 3.11.9
  - Updated SQLAlchemy from 2.0.23 to 2.0.36
  - Added Flask-SQLAlchemy dependency
  - Solution committed and pushed

- **Render Deployment Error - Circular Import (2025-01-XX):** Fixed circular import between app.py and models.py
  - Created `db = SQLAlchemy()` directly in app.py before importing models
  - Models now import db from app after db is initialized
  - Solution committed and pushed

- **Render Deployment Error - Missing DATABASE_URL (2025-01-XX):** Added validation for DATABASE_URL
  - Added error message if DATABASE_URL is not set
  - **Action Required:** Set DATABASE_URL environment variable in Render dashboard

### 📋 Pending/Next Steps
- [ ] **CRITICAL:** Set `DATABASE_URL` environment variable in Render dashboard
  - Create PostgreSQL database in Render
  - Copy the connection string
  - Add as `DATABASE_URL` environment variable in Web Service settings
- [ ] Set other required environment variables in Render:
  - `SECRET_KEY` (generate a random string)
  - `ADMIN_TOKEN` (for admin import endpoints)
  - `ALLOWED_ORIGINS` (include your Netlify frontend URL)
  - `ROOT_PERSON_ID` (optional, UUID of root person)
- [ ] Deploy backend to Render (should work after DATABASE_URL is set)
- [ ] Run database migrations: `flask db upgrade` (via Render shell or SSH)
- [ ] Deploy frontend to Netlify
- [ ] Update `API_BASE_URL` in `frontend/api.js` with Render backend URL
- [ ] Import historical book data using admin endpoints
- [ ] Test full deployment end-to-end

## Environment Variables Required

**Backend (Render):**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - Flask secret key
- `ADMIN_TOKEN` - Token for admin import endpoints
- `ALLOWED_ORIGINS` - Comma-separated CORS origins (include Netlify URL)
- `ROOT_PERSON_ID` - (Optional) UUID of root person
- `LOG_LEVEL` - (Optional) Logging level (default: INFO)

**Frontend:**
- Update `API_BASE_URL` in `frontend/api.js` after backend deployment

## Phase 2 Preparation

The codebase is prepared for Phase 2 with:
- `layer` field in Person model (currently only 'base')
- `is_leaf` flag in API responses (indicates attachment points)
- `visibility` field in Relationship model (currently only 'public')
- Admin import endpoints ready for data loading
- Frontend shows leaf node indicators

## Important Notes

1. **Python Version:** Pinned to 3.11.9 via `runtime.txt` (Render compatibility)
2. **Database Migrations:** Use Flask-Migrate (`flask db init/migrate/upgrade`)
3. **Admin Import:** Use `X-ADMIN-TOKEN` header for admin endpoints
4. **CORS:** Must include frontend URL in `ALLOWED_ORIGINS`
5. **Root Person:** Set `ROOT_PERSON_ID` env var or system uses oldest base person

## Git Repository

- **Remote:** https://github.com/jaklilu/Royal_Family_Tree.git
- **Branch:** main
- **Last Commit:** Fix for Render deployment (Python version + SQLAlchemy update)

## Deployment Checklist

### Backend (Render)
- [ ] Create PostgreSQL database
- [ ] Create Web Service
- [ ] Set environment variables
- [ ] Configure build command: `cd backend && pip install -r requirements.txt`
- [ ] Configure start command: `cd backend && gunicorn app:app`
- [ ] Run migrations: `flask db upgrade`
- [ ] Test health endpoint

### Frontend (Netlify)
- [ ] Connect repository
- [ ] Set base directory: `frontend`
- [ ] Set publish directory: `frontend`
- [ ] Update `API_BASE_URL` in `api.js`
- [ ] Deploy and test

## Testing

**Local Testing:**
1. Backend: `cd backend && flask run` (http://localhost:5000)
2. Frontend: `cd frontend && python -m http.server 5500` (http://localhost:5500)
3. Test API endpoints with curl or Postman
4. Test admin import with proper token

**Production Testing:**
1. Verify health endpoint responds
2. Test root person loads
3. Test navigation through tree
4. Test search functionality
5. Test relationship finder
6. Verify CORS works (frontend can call backend)

---

**Last Updated:** 2025-01-XX
**Phase:** 1 (Read-Only Base Tree)
**Status:** Ready for deployment after environment setup

