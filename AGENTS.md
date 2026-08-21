# Base44 Dev Environment — Student OS

## What this is
A Flask university/school management portal (Jinja2 templates, vanilla CSS). Role-based auth (Student/Teacher/Admin), academic management, messaging, exam predictor.

## Stack
- **Backend:** Python 3.11, Flask, Flask-Login, Flask-WTF (CSRF), Flask-Mail, Flask-Babel.
- **Database:** SQLite by default (file `student_os.db` at repo root). PostgreSQL supported if `DATABASE_URL` is set — not used in the Base44 dev setup. `db.py` has a `CursorWrapper` that translates `%s`→`?` and `RETURNING id` for SQLite.
- **Frontend:** Jinja2 templates + static CSS/JS (glassmorphism). No build step.

## Running here (Base44)
- `docker compose -f docker-compose.base44.yml up -d --build`
- The `web` service builds `Dockerfile.base44` (deps only: python:3.11-slim + tesseract/poppler + pip requirements), then bind-mounts the repo at `/app` and runs `python app.py` (Flask dev server, debug reloader on port 5000, mapped to host port 3000).
- Live edits reload automatically (Werkzeug reloader). If a change isn't picked up, call `reload_preview`.
- Placeholders live in `.env.base44-defaults` (listed first in `env_file`); real secrets override via `/run/base44/app.env` (listed last).

## First-boot behavior
- DB schema + migrations run lazily on the **first request** (`@app.before_request safe_init` → `startup_init`). So the container starts before any table exists; hit any route to trigger init.
- `SEED_DEMO=true` auto-creates demo data: 1 school (Genesis High), admin (`admin`/`admin123` via `ADMIN_*` env), 3 teachers, 4 students, 3 courses.
- If `ADMIN_PASSWORD` is unset, a random admin password is generated and printed to logs.

## Env vars
- `SECRET_KEY` — required for sessions/CSRF (placeholder set in defaults).
- `FLASK_ENV=development` — keeps session cookies working over the preview proxy (no HTTPS-only).
- `SEED_DEMO`, `ADMIN_USERNAME`, `ADMIN_PASSWORD` — demo bootstrapping.
- **Optional (email features only, not needed to boot):** `MAIL_USERNAME`/`MAIL_PASSWORD` (Gmail SMTP), `BREVO_API_KEY`/`SENDER_EMAIL`/`SENDER_NAME` (Brevo transactional email via `brevo_mail.py`). Admissions email sending fails gracefully if these are absent.

## Verifying it works
- `curl -sf http://localhost:3000/` → 200, landing page.
- `curl -sf -H "Host: 3000-$BASE44_PUBLIC_HOST_SUFFIX" http://localhost:3000/` → 200 (external preview host).
- `/login` loads with a CSRF token → SECRET_KEY is configured.
- DB seeded: 1 school, 1 admin, 4 students, 3 teachers, 3 courses.

## Notes / quirks
- Subdomain-based school detection in `inject_school_context` falls back to school id 1 for the preview host.
- `pdf2image`/`pytesseract` need poppler/tesseract binaries (installed in `Dockerfile.base44`) — used by the exam predictor PDF features.
- `Student_OS_Govt_Backup_Jan29.zip` is a large backup archive committed to the repo; not needed at runtime.
