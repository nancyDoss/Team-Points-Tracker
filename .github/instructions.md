## Repo snapshot

This is a small, single-process Flask app that tracks team points in a local SQLite database.

Key files:
- `app.py` — main Flask server and database logic (routes, schema, DB helper functions).
- `admin.html`, `leaderboard.html` — UI pages used by the server templates.
- `README.md` — setup and run instructions.

## High-level architecture

- Single Flask app (no build step). Runs via `python app.py` and calls `init_db()` on startup to create `points.db`.
- Data storage: local `sqlite3` database file `points.db` with a single table `kids_points` (id, name UNIQUE, points).
- Client flows:
  - Public page `/` renders `leaderboard.html` and fetches `/data` to populate a chart.
  - Admin page `/admin` provides forms that POST to endpoints which mutate the DB and redirect back to `/admin`.

## Important routes & behaviors (source: `app.py`)
- `/` — public leaderboard (renders `leaderboard.html`).
- `/admin` — admin UI (renders `admin.html`).
- `/add/<int:team_id>` (POST) — increments points; expects form field `points` (defaults to 1).
- `/add_team` (POST) — creates a new team; expects form field `name`. Uses `INSERT OR IGNORE` so duplicates are ignored.
- `/clear_points` (POST) — resets all points to zero.
- `/delete_team/<int:team_id>` (POST) — deletes a team.
- `/data` — returns JSON { labels: [...names], points: [...] } used by the chart on the public page.

## Project-specific conventions and patterns

- DB helper: `get_db_connection()` sets `conn.row_factory = sqlite3.Row` so views/handlers read rows like dicts (e.g., `row['name']`).
- `init_db()` seeds default teams (emoji names) using `INSERT OR IGNORE` — new names are idempotent.
- Admin endpoints perform writes via POST forms and then `redirect('/admin')` — keep this pattern when adding features.
- No ORM, no migrations: schema changes should be done carefully; `init_db()` uses `CREATE TABLE IF NOT EXISTS`.

## Developer workflows (how to run / test quickly)

1. Install deps: `pip install flask` (there is no `requirements.txt`).
2. Run locally: `python app.py` — the app creates `points.db` on first start and runs with `debug=True`.
3. Open browser: public leaderboard at `http://127.0.0.1:5000/`, admin at `/admin`.

## Concrete examples (copy/paste)

- Add 5 points to team id 2 (form POST): POST to `/add/2` with form field `points=5`.
- Add a new team named "🦊 Fox Squad": POST to `/add_team` with form field `name=🦊 Fox Squad`.
- Chart client: GET `/data` -> expects JSON { labels: ["Team A", "Team B"], points: [10, 3] }.

## Quick checks before edits

- If you change the JSON shape from `/data`, update `leaderboard.html` chart code accordingly.
- Keep SQL parameterized (current code uses `?` placeholders) — don't switch to string interpolation.
- If moving templates, ensure Flask finds them (default `templates/` folder) or set `app.template_folder`.

