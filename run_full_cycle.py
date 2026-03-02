import argparse
import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Run end-to-end multi-article production pipeline.")
    parser.add_argument("--max-count", type=int, default=8, help="Maximum articles to generate in one run")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker count")
    args = parser.parse_args()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "multi_article_pipeline.py"),
        "--max-count",
        str(args.max_count),
        "--workers",
        str(args.workers),
    ]
    subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT))


if __name__ == "__main__":
    main()
