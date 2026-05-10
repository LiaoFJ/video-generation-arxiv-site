from app.cli import run_live_daily_job
from app.config import Settings


def main() -> int:
    settings = Settings()
    processed_count = run_live_daily_job(settings)
    print(f"Published {processed_count} paper(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
