# Copilot Instructions: Mergington High School Activities API

## Architecture Overview

This is a simple FastAPI application with a static frontend for managing school extracurricular activities.

**Backend**: `src/app.py` - FastAPI server with in-memory data storage (resets on restart)
**Frontend**: `src/static/` - Vanilla HTML/CSS/JS (no framework)
**Tests**: `tests/test_api.py` - pytest with FastAPI TestClient

## Key Data Structures

Activities are stored as a dictionary in `src/app.py`:
```python
activities = {
    "Activity Name": {
        "description": str,
        "schedule": str,
        "max_participants": int,
        "participants": [emails...]
    }
}
```

Activity names serve as identifiers (not IDs). Student emails identify participants.

## API Endpoints

- `GET /activities` - Returns all activities with participant lists
- `POST /activities/{activity_name}/signup?email={email}` - Add participant
- `DELETE /activities/{activity_name}/participants/{email}` - Remove participant
- `GET /` - Redirects to `/static/index.html`

## Frontend Patterns

**Auto-refresh on mutations**: Call `fetchActivities()` after signup/deletion to update the UI without page reload
**Participant display**: Each participant shows as a card with email and delete button (× icon)
**No frameworks**: Direct DOM manipulation with `document.querySelector` and `fetch`

## Development Workflow

**Run server**: `python src/app.py` or `uvicorn src.app:app --reload` (port 8000)
**Run tests**: `pytest` (uses pytest.ini config with pythonpath = .)
**Install deps**: `pip install -r requirements.txt` (fastapi, uvicorn, pytest, httpx)

## Testing Conventions

- Use `reset_activities` fixture with `autouse=True` to reset state before each test
- Import activities dict directly: `from src.app import app, activities`
- Group tests by endpoint in classes (e.g., `TestSignupForActivity`)
- Test both success paths and error conditions (404s, 400s)
- Verify state changes by fetching activities after mutations

## Styling Standards

- Primary color: `#1a237e` (dark blue for headers, buttons)
- Success: green background (`#e8f5e9`), Error: red background (`#ffebee`)
- Participant cards: light gray background (`#f5f5f5`) with hover effect
- Delete buttons: transparent with red × icon, scale on hover
- No bullet points for participant lists (use `list-style-type: none`)

## Commit Message Format

Use conventional commits: `type(scope): description`
- Types: feat, fix, docs, style, refactor, test, chore
- Example: `feat(api): add participant deletion endpoint`
