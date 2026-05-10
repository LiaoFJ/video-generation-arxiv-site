from app.cli import build_publish_plan


def main() -> int:
    _ = build_publish_plan([], limit=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
