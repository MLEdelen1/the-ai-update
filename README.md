# The AI Update Repo

## Windows Runtime Setup

Use the existing Miniconda interpreter directly so the pipeline always uses the same Python on Windows.

```powershell
cd C:\Users\MLEde\.openclaw\workspace\business\the-ai-update-repo

# Optional but recommended: force explicit project root for all scripts
$env:X_MANAGE_PROJECT_ROOT = "C:\Users\MLEde\.openclaw\workspace\business\the-ai-update-repo"

# Optional: provide Gemini key without creating config/gemini_keys.json
$env:GEMINI_API_KEY = "<your-gemini-api-key>"

# Install runtime dependencies in Miniconda base (or your target env)
C:\Miniconda3\python.exe -m pip install --upgrade pip
C:\Miniconda3\python.exe -m pip install requests feedparser markdown yt-dlp

# Run full cycle (auto-posts newly generated articles to X by default)
C:\Miniconda3\python.exe run_full_cycle.py

# Optional: run cycle but skip X posting
C:\Miniconda3\python.exe run_full_cycle.py --skip-x-post
```

If `config\gemini_keys.json` is missing and `GEMINI_API_KEY` is not set, the run still completes with a local fallback article/tweet so site generation and publish steps can continue.

## Post to X on Windows

Run from repo root: `C:\Users\MLEde\.openclaw\workspace\business\the-ai-update-repo`

Setup supports this auth order for X API credentials: environment variables first (`X_API_KEY`, `X_API_SECRET`, `X_ACCESS_TOKEN`, `X_ACCESS_SECRET`), then local file `~/.clawdbot/secrets/x-api.json`. Cookie mode uses `config/x_cookies.json`.

Readiness test (single command, pass/fail with reasons):

```powershell
C:\Miniconda3\python.exe scripts\x_readiness_check.py
```

Post command (auto-uses API when creds are available, else cookie mode):

```powershell
C:\Miniconda3\python.exe scripts\post_to_x.py
```

Article autopost/backfill commands (idempotent URL dedupe tracked in `data/posted/x_posted_articles.json`; each post includes homepage + article URL + hashtags):

```powershell
# Post only newly created articles in the current cycle (used by run_full_cycle.py automatically)
C:\Miniconda3\python.exe scripts\x_article_poster.py post-new --since <epoch_seconds> --limit 8 --sleep 1.5

# Backfill recent unposted article backlog now
C:\Miniconda3\python.exe scripts\x_article_poster.py backfill --limit 15 --sleep 2
```

Logs are written inside this repo under `logs/`.
