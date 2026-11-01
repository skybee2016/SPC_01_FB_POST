"""One autopost cycle: generate a post, then publish it. Called by GitHub Actions 3x/day."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def run(script):
    print(f"--> {script}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


if __name__ == "__main__":
    run("generate_post.py")
    run("publish_facebook.py")
