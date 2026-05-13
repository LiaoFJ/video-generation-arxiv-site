# Local Run Guide

## Start the website

Run `uvicorn app.main:app --reload --host 127.0.0.1 --port 8000`

The website now requires login. Configure the local single-user credentials in `.env`:

- `APP_USERNAME`
- `APP_PASSWORD`

## Run the daily publish job

Run `python scripts/run_daily.py`

Required environment variables for the live pipeline:

- `OPENAI_API_KEY`: provider API key used for Chinese summaries. The current default setup targets a DeepSeek-compatible endpoint.
- `APP_USERNAME`: local site login username
- `APP_PASSWORD`: local site login password
- `RANKING_URL_TEMPLATE`: optional override for the ranking page template. If omitted, the app uses `https://huggingface.co/papers?date={date}` by default.

Example:

```powershell
$env:OPENAI_API_KEY="sk-..."
python scripts/run_daily.py
```

## Windows test environment

If `pytest` hits a temp-directory permission error on Windows, set `TMP` and `TEMP` to a writable folder inside the worktree before running tests.

## Windows Task Scheduler

The local machine is configured to run the daily publish job at `10:00` every morning using the task name `VideoGenerationArxivDaily`.
