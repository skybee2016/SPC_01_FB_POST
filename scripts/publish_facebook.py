"""Publish the newest unpublished post to the Facebook Page via the Graph API.

Uses POST /{page-id}/photos with the image and caption, so the creative is posted
as a photo post. Marks the post as published in its post.json and in posts/history.json.
"""
import json
import os
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v21.0"
HISTORY_FILE = ROOT / "posts" / "history.json"


def next_unpublished():
    folders = sorted(p for p in (ROOT / "posts").iterdir() if p.is_dir())
    for folder in folders:
        meta = folder / "post.json"
        if meta.exists() and not json.loads(meta.read_text()).get("published"):
            return folder
    return None


def publish(folder):
    page_id = os.environ["FB_PAGE_ID"]
    token = os.environ["FB_PAGE_ACCESS_TOKEN"]
    meta_path = folder / "post.json"
    meta = json.loads(meta_path.read_text())

    message = meta["caption"]
    if meta.get("hashtags"):
        message += "\n\n" + " ".join("#" + h.lstrip("#") for h in meta["hashtags"])

    if meta.get("has_image", True) and (folder / "image.png").exists():
        with open(folder / "image.png", "rb") as img:
            resp = requests.post(
                f"{GRAPH}/{page_id}/photos",
                data={"message": message, "access_token": token, "published": "true"},
                files={"source": img},
                timeout=120,
            )
    else:
        resp = requests.post(
            f"{GRAPH}/{page_id}/feed",
            data={"message": message, "access_token": token},
            timeout=120,
        )
    body = resp.json()
    if resp.status_code != 200 or "error" in body:
        raise RuntimeError(f"Facebook publish failed: {body}")

    meta.update({"published": True, "facebook_post_id": body.get("post_id") or body.get("id")})
    meta_path.write_text(json.dumps(meta, indent=2))

    history = json.loads(HISTORY_FILE.read_text()) if HISTORY_FILE.exists() else []
    history.append({"id": meta["id"], "headline": meta["headline"], "post_type": meta["post_type"],
                    "facebook_post_id": meta["facebook_post_id"]})
    HISTORY_FILE.write_text(json.dumps(history, indent=2))
    return meta["facebook_post_id"]


def main():
    folder = next_unpublished()
    if folder is None:
        print("Nothing to publish.")
        return 0
    post_id = publish(folder)
    print(f"Published {folder.name} as Facebook post {post_id}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
