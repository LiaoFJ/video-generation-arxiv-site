# Local Run Guide

## Start the website

Run `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

## Run the daily publish job

Run `python scripts/run_daily.py`

Required environment variables for the live pipeline:

- `OPENAI_API_KEY`: OpenAI API key used for Chinese summaries
- `RANKING_URL_TEMPLATE`: optional override for the ranking page template. If omitted, the app uses `https://huggingface.co/papers?date={date}` by default.

Example:

```powershell
$env:OPENAI_API_KEY="sk-..."
python scripts/run_daily.py
```

## Windows test environment

If `pytest` hits a temp-directory permission error on Windows, set `TMP` and `TEMP` to a writable folder inside the worktree before running tests.

## Windows Task Scheduler

Schedule `python scripts/run_daily.py` once per day after the expected arXiv traffic data is available.
