# Facebook setup: auto-post to the Senior Peace Care Page

## Important first: which Page?
The link you sent (`facebook.com/profile.php?id=61595030999670`) is a **personal profile** URL. The Graph API can only publish to a **Facebook Page**. Before continuing:
1. Go to facebook.com/pages/create and create a Page named **Senior Peace Care** (or use your existing business Page).
2. Note its Page ID: Page > About > Page ID (or Page Settings > Page transparency).
3. Send me that Page ID and the Page URL, and I will fill them into `config/settings.json`.

## A. Create the Meta app
1. Go to https://developers.facebook.com > My Apps > Create App.
2. Use case: **Other** > type **Business**. Name it `SPC Autopost`.
3. In the app dashboard, add the **Facebook Login for Business** product (needed to get tokens).
4. App settings > Basic: copy the **App ID** and **App Secret** (keep them private).

## B. Permissions
Request these for the Page:
- `pages_show_list`
- `pages_read_engagement`
- `pages_manage_posts`

Note: while the app is in Development mode, only accounts with a role on the app (admin, developer, tester) can use these permissions. That is fine for posting to your own Page. For a fully public app you will need **App Review** from Meta, which requires a privacy policy URL and a screencast of the flow.

## C. Get a long-lived Page access token
1. Open https://developers.facebook.com/tools/explorer
2. Select your app. Click **Generate Access Token** and grant the three permissions above, choosing the Senior Peace Care Page.
3. Exchange the short-lived user token for a long-lived one:
   `GET https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=APP_ID&client_secret=APP_SECRET&fb_exchange_token=SHORT_TOKEN`
4. Get the Page token (it does not expire if derived from a long-lived user token):
   `GET https://graph.facebook.com/v21.0/me/accounts?access_token=LONG_USER_TOKEN`
   Copy the `access_token` for the Senior Peace Care Page. That is `FB_PAGE_ACCESS_TOKEN`.
5. Verify: `GET https://graph.facebook.com/v21.0/PAGE_ID?fields=name&access_token=PAGE_TOKEN` should return the Page name.

## D. Add secrets to GitHub
Repo `skybee2016/SPC_01_FB_POST` > Settings > Secrets and variables > Actions > New repository secret:
- `OPENAI_API_KEY`
- `FB_PAGE_ID`
- `FB_PAGE_ACCESS_TOKEN`

## E. Turn it on
1. Push this folder to the repo (main branch).
2. Actions tab > "Senior Peace Care autopost" > Run workflow once to test.
3. After a successful run you should see a new photo post on the Page and a new folder under `posts/`.
4. After that the schedule runs automatically at 05:30, 13:30 and 21:30 IST.

## Notes and limits
- GitHub scheduled workflows can run a few minutes late, and are paused after 60 days of no repo activity. The bot commits to the repo each run, which keeps it active.
- Keep the Page token secret. If it is ever exposed, regenerate it in the Graph API Explorer and update the secret.
- Meta may change API versions. The script uses v21.0; bump `GRAPH` in `publish_facebook.py` when needed.
- Every post is archived in `posts/` (copy, image, Facebook post ID), so you can audit or reuse content.
