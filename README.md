# IDS Notice Board — Deployment Instructions

This repository contains a small Flask app used as an internal staff status dashboard and slideshow.

Files added to support deployment:

- `requirements.txt` — Python dependencies
- `Procfile` — process command for Railway / Heroku
- `.gitignore` — ignores local DB and uploads
- `runtime.txt` — Python runtime pin

Quick steps to push to GitHub and deploy to Railway

1) Initialize git (if not already) and push your repository to your GitHub account under `https://github.com/UBANTREW/your-repo-name`:

```bash
git init
git add .
git commit -m "Initial IDS Notice Board commit"
git branch -M main
git remote add origin git@github.com:UBANTREW/your-repo-name.git
git push -u origin main
```

2) On Railway
- Create a new project → Deploy from GitHub
- Choose your repo and connect
- Railway will detect a Python app. Ensure build uses `requirements.txt` and the start command uses the `Procfile`.

3) (Optional) For production durability — add a PostgreSQL plugin in Railway and set `DATABASE_URL` in your Railway project. If you want that workflow I can refactor the app to use SQLAlchemy and `DATABASE_URL`.

Notes
- This app currently uses a local SQLite file by default (`database.db`) — Railway filesystem is ephemeral (files uploaded at runtime or the SQLite file may be lost after restarts). For a production deployment use Railway Postgres and the SQLAlchemy migration.

If you want, I can:
- Refactor to `Flask-SQLAlchemy` and use `DATABASE_URL` (recommended for production).
- Create GitHub Actions to run tests on push.
- Provide step-by-step Railway screenshots and env setup.

Tell me which repository name to push to (or push yourself) and whether you want a production-ready refactor now.
