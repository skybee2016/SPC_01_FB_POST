# SPC_01_FB_POST: Senior Peace Care Facebook autopost

Fully automatic: GitHub Actions runs 3 times a day (every 8 hours). Each run:
1. OpenAI writes a post (headline, caption with the toll-free number and website, hashtags, CTA to follow and call).
2. OpenAI creates a matching image creative.
3. The post is published to the Senior Peace Care Facebook Page via the Graph API.
4. Everything is archived in `posts/` and committed back to this repo.

## Structure
```
config/settings.json          brand, TFN, page ID, schedule, models, post types, CTAs
scripts/generate_post.py      OpenAI copy + image generation
scripts/publish_facebook.py   Graph API publish to the Page
scripts/run_autopost.py       one full cycle (generate then publish)
posts/                        archive: one folder per post (post.json + image.png), history.json
.github/workflows/autopost.yml  schedule: 0 0,8,16 * * * UTC
docs/FACEBOOK_SETUP.md        step-by-step Meta developer and token setup
.env.example                  required secrets
```

## Before first run
1. Replace `REPLACE_WITH_TOLL_FREE_NUMBER`, `facebook_page_id` and `page_url` in `config/settings.json`.
2. Follow `docs/FACEBOOK_SETUP.md` to create the Page, Meta app and tokens.
3. Add `OPENAI_API_KEY`, `FB_PAGE_ID`, `FB_PAGE_ACCESS_TOKEN` as repo secrets.

## Local test
```bash
pip install -r requirements.txt
export OPENAI_API_KEY=... FB_PAGE_ID=... FB_PAGE_ACCESS_TOKEN=...
python scripts/generate_post.py   # creates a folder under posts/ without publishing
python scripts/publish_facebook.py
```

## Quality guardrails
Posts avoid medical claims, guarantees, fake testimonials and unconfirmed pricing (see `content.avoid` in settings). Post types rotate so the feed does not repeat one format. Recent headlines are passed to the model to avoid repetition.
