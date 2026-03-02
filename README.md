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

# Run full cycle
C:\Miniconda3\python.exe run_full_cycle.py
```

If `config\gemini_keys.json` is missing and `GEMINI_API_KEY` is not set, the run still completes with a local fallback article/tweet so site generation and publish steps can continue.
