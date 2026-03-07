import argparse
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description="Run end-to-end multi-article production pipeline.")
    parser.add_argument("--max-count", type=int, default=8, help="Maximum articles to generate in one run")
    parser.add_argument("--workers", type=int, default=4, help="Parallel worker count")
    parser.add_argument("--skip-x-post", action="store_true", help="Skip automatic X posting step")
    parser.add_argument("--x-sleep", type=float, default=1.5, help="Seconds between X posts")
    args = parser.parse_args()

    start_ts = time.time()

    cmd = [
        sys.executable,
        str(PROJECT_ROOT / "multi_article_pipeline.py"),
        "--max-count",
        str(args.max_count),
        "--workers",
        str(args.workers),
    ]
    subprocess.run(cmd, check=True, cwd=str(PROJECT_ROOT))

    if not args.skip_x_post:
        x_cmd = [
            sys.executable,
            str(PROJECT_ROOT / "scripts" / "x_article_poster.py"),
            "post-new",
            "--since",
            str(start_ts - 2),
            "--limit",
            str(args.max_count),
            "--sleep",
            str(args.x_sleep),
        ]
        try:
            subprocess.run(x_cmd, check=False, cwd=str(PROJECT_ROOT))
        except Exception as exc:
            print(f"WARN: automatic X posting step failed safely: {exc}")


    print("Committing and pushing changes to GitHub for Cloudflare deployment...")
    try:
        subprocess.run(["git", "add", "."], check=True, cwd=str(PROJECT_ROOT))
        subprocess.run(["git", "commit", "-m", "Automated daily update: articles and SEO fixes"], check=False, cwd=str(PROJECT_ROOT))
        subprocess.run(["git", "push", "origin", "main"], check=True, cwd=str(PROJECT_ROOT))
        print("Successfully deployed to Cloudflare via GitHub.")
    except Exception as exc:
        print(f"WARN: automatic git deployment failed: {exc}")

if __name__ == "__main__":
    main()
