"""Generate one Facebook post (copy + image) for Senior Peace Care using OpenAI.

Output is saved to posts/<UTC timestamp>/ with:
  post.json   - headline, caption, hashtags, cta, image_prompt, post_type
  image.png   - the creative
"""
import base64
import json
import os
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).resolve().parent.parent
SETTINGS = json.loads((ROOT / "config" / "settings.json").read_text())
HISTORY_FILE = ROOT / "posts" / "history.json"


def load_history():
    if HISTORY_FILE.exists():
        return json.loads(HISTORY_FILE.read_text())
    return []


def pick_post_type(history):
    """Rotate post types so the page does not repeat the same format back to back."""
    types = SETTINGS["content"]["post_types"]
    recent = [h.get("post_type") for h in history[-len(types):]]
    candidates = [t for t in types if t not in recent] or types
    return random.choice(candidates)


def build_prompt(post_type, recent_headlines):
    b = SETTINGS["brand"]
    cta_lines = "\n".join(SETTINGS["content"]["cta_options"]).format(tfn=b["tfn"], website=b["website"])
    return f"""You write Facebook posts for {b['name']}, a senior concierge service.
Brand tone: {b['tone']}.
Audience: {b['audience']}.
Services to draw from: {', '.join(b['services'])}.
Post type: {post_type}.
Avoid these headlines (already used recently): {recent_headlines or 'none'}.
Never do: {', '.join(SETTINGS['content']['avoid'])}.

Goal of the post: get people to FOLLOW this page and CALL the toll-free number to sign up.
Write a scroll-stopping first line, 2-4 short paragraphs, plain language, no jargon.
End with ONE of these calls to action, filled in exactly, choosing the best fit:
{cta_lines}
Must include the phone number {b['tfn']} and the website {b['website']} somewhere in the caption.

Return ONLY valid JSON with keys:
headline (max 8 words), caption (the full Facebook text including CTA, phone and website),
hashtags (list of 5 relevant hashtags without spaces), image_prompt (a detailed, photo-realistic
or warm illustrated scene description for the creative: no text in the image, no real people's
faces, warm natural light, senior-friendly, uplifting), alt_text (one sentence)."""


def generate_copy(client, post_type, recent_headlines):
    resp = client.chat.completions.create(
        model=SETTINGS["models"]["text"],
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": build_prompt(post_type, recent_headlines)}],
        temperature=0.9,
    )
    return json.loads(resp.choices[0].message.content)


def generate_image(client, image_prompt, out_path):
    result = client.images.generate(
        model=SETTINGS["models"]["image"],
        prompt=image_prompt + " Warm, uplifting, no text, no logos.",
        size=SETTINGS["models"]["image_size"],
    )
    item = result.data[0]
    if getattr(item, "b64_json", None):
        out_path.write_bytes(base64.b64decode(item.b64_json))
    else:
        import requests
        out_path.write_bytes(requests.get(item.url, timeout=120).content)


def main():
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    history = load_history()
    post_type = pick_post_type(history)
    recent = ", ".join(h["headline"] for h in history[-10:])

    copy = generate_copy(client, post_type, recent)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    out_dir = ROOT / "posts" / stamp
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        generate_image(client, copy["image_prompt"], out_dir / "image.png")
        has_image = True
    except Exception as exc:  # image model unavailable on account: fall back to text-only post
        print(f"Image generation failed, posting text only: {exc}")
        has_image = False

    record = {"id": stamp, "post_type": post_type, "created_utc": stamp, "published": False,
              "has_image": has_image, **copy}
    (out_dir / "post.json").write_text(json.dumps(record, indent=2))
    print(json.dumps({"folder": str(out_dir.relative_to(ROOT)), "headline": copy["headline"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
