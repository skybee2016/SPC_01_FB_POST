"""One autopost cycle: generate a post, then publish it. Called by GitHub Actions 3x/day."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEHOLDER = "REPLACE_WITH_TOLL_FREE_NUMBER"


def run(script):
    print(f"--> {script}")
    subprocess.run([sys.executable, str(ROOT / "scripts" / script)], check=True)


def tfn_is_set():
    settings = json.loads((ROOT / "config" / "settings.json").read_text())
    return settings["brand"]["tfn"] != PLACEHOLDER


if __name__ == "__main__":
    run("generate_post.py")
    if not tfn_is_set():
        print("SAFETY STOP: toll-free number is still the placeholder. Post generated but NOT published.")
        sys.exit(0)
    run("publish_facebook.py")
