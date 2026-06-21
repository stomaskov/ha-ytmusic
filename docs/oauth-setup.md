# ytmusic — OAuth client setup (one-time)

> ## ⚠️ OAuth is currently BROKEN upstream (verified 2026-06-20) — use the Cookie method instead
> On ytmusicapi 1.12.1, the TV-client OAuth flow completes (Google authorizes and returns a
> valid token), but **every** authenticated YouTube Music call then fails with
> `HTTP 400 — Request contains an invalid argument`. This is an upstream ytmusicapi/YouTube
> issue, not something the integration can fix. **Set the integration up with the Cookie auth
> method** (verified working — returns the full library). Keep this guide for when/if ytmusicapi's
> OAuth path starts working again; the OAuth client you create here is reusable. The rest of this
> document assumes OAuth works.

The `ytmusic` integration's **OAuth** auth method needs a Google OAuth client of type
**"TVs and Limited Input devices"** (client_id + client_secret). This is a free, one-time
~5-minute setup in the Google Cloud Console. You create the client once; the integration
then uses a device-code flow to get a durable, auto-refreshing token.

> Prefer OAuth over the cookie method: cookies expire and need periodic re-pasting; an
> OAuth refresh token keeps working until you revoke it (see the **7-day caveat** below — it
> matters).

Do this with the **same Google account that has your YouTube Music library / subscriptions.**

---

## 1. Create (or pick) a Google Cloud project

1. Go to <https://console.cloud.google.com/>.
2. Top bar → project dropdown → **New Project** (name it e.g. `ha-ytmusic`) → **Create**.
   (Or reuse an existing project.) Make sure that project is selected.

## 2. Enable the YouTube Data API v3

The OAuth client won't work unless this API is enabled on the project (a disabled API is the
usual cause of an `invalid_client` / "YouTube Data API is not enabled" error later).

1. Left menu → **APIs & Services → Library**.
2. Search **"YouTube Data API v3"** → open it → **Enable**.

## 3. Configure the OAuth consent screen

(In the current console this lives under **APIs & Services → OAuth consent screen**, a.k.a.
**Google Auth Platform**.)

1. If prompted to "Get started" / configure: set
   - **User type / Audience: External**
   - **App name:** anything (e.g. `HA YouTube Music`)
   - **User support email:** your email
   - **Developer contact email:** your email
   - Save.
2. **Scopes:** you don't have to add any here for the device flow (the integration requests
   `https://www.googleapis.com/auth/youtube` at authorization time). If a scopes step insists,
   add `.../auth/youtube` and continue.
3. **Test users:** if your app stays in **Testing** status, add your own Google account under
   **Audience → Test users** (only listed test users can authorize while in Testing).

### ⚠️ 7-day refresh-token caveat (important — read this)

While the consent screen's **publishing status is "Testing", Google expires the OAuth
**refresh token after 7 days** — you'd have to re-authorize the integration every week,
defeating the point of OAuth.

**To get a long-lived token, Publish the app — via the Audience tab, NOT the Branding page:**

- Left nav → **Audience** → **Publish app** → confirm the "push to production?" dialog (moves
  from *Testing* to *In production*).
- ⚠️ **Do NOT fill in the Branding page** (Application home page / privacy policy / terms of
  service / Authorized domains). Those fields exist only for **verification** (showing your logo
  + removing the warning) and are *not* required to publish. If you try to *save* the Branding
  page it will block you demanding an authorized domain — just navigate away from it; publishing
  happens on the **Audience** tab and needs none of those.
- After publishing it shows as **"unverified"** — fine for personal use (you're well under the
  100-user cap). During the device authorization step (§5) you'll see a *"Google hasn't verified
  this app"* screen; click **Advanced → Go to `<app name>` (unsafe)** and continue. (Once only.)
- In production status, the refresh token does **not** expire on a 7-day timer (it can still be
  revoked manually, or lapse after ~6 months of non-use).
- *If* the Publish dialog itself asks for a privacy-policy URL (some accounts do), point it at
  any public page you control (a GitHub repo README / public Gist) and set the authorized domain
  to that page's domain (e.g. `github.com`). Usually it doesn't ask.

If you'd rather not publish: stay in **Testing** (OAuth still works — you'll just re-authorize
the integration ~weekly via its built-in reauth flow), or use the **Cookie** auth method and
skip Google Cloud entirely.

## 4. Create the OAuth client (TVs and Limited Input devices)

1. Left menu → **APIs & Services → Credentials**.
2. **+ Create Credentials → OAuth client ID**.
3. **Application type → "TVs and Limited Input devices"**.
   (If you don't see it, the consent screen from §3 isn't configured yet — finish that first.)
4. **Name:** e.g. `HA ytmusic`. → **Create**.
5. A dialog shows your **Client ID** and **Client secret**. Copy both (you can re-open them
   later from the Credentials list).

## 5. Add the integration in Home Assistant

1. **Settings → Devices & Services → Add Integration → "YouTube Music"**.
2. Choose **OAuth**.
3. Paste the **Client ID** and **Client secret** from §4.
4. The next screen shows a URL (`https://www.google.com/device` or similar) and a short
   **user code**. On any device:
   - Visit the URL, sign in with **the Google account that has your YouTube Music**, enter the
     code.
   - If you published the app (§3), click through the "unverified app" → **Advanced → Go to …
     (unsafe)** warning.
   - Grant access.
5. Back in HA, submit to finish. HA validates the token with a real API call before creating
   the entry, then (first time only) installs `ytmusicapi` + `yt-dlp` — this can take a minute.
6. (Optional) When asked for a **stream cookie**, you can paste a `music.youtube.com` cookie to
   make yt-dlp playback bulletproof, or skip it.

## 6. After setup

- Set your **default speaker** in the integration's **Options** (Configure), plus result limit
  and radio/autoplay.
- Walk `docs/superpowers/SMOKE-CHECKLIST.md` to verify search → play → queue → radio.

---

## Troubleshooting

- **`invalid_client` / "YouTube Data API is not enabled"** → §2 wasn't done (or done on a
  different project than the OAuth client). Enable YouTube Data API v3 on the *same* project.
- **`unauthorized_client` / token refresh errors** → client_id/secret mismatch, or the client
  type isn't "TVs and Limited Input devices". Re-create the client (§4).
- **Auth stops working after ~1 week** → the app is still in **Testing** status; publish it
  (§3) and re-add the integration to get a non-expiring refresh token.
- **"unverified app" warning during authorization** → expected for a personal unverified app;
  **Advanced → Go to … (unsafe)** is safe here (it's *your* app and *your* account).
- **Wrong library shows up** → you authorized with a different Google account; remove the entry
  and re-add, signing in with the account that owns your YouTube Music.

## Security note

The client_id/secret and the resulting token are stored only in HA's config entry
(`.storage/core.config_entries`). Don't paste them into this repo, chat, or any file. They
grant access to your YouTube account — treat them as secrets and revoke the OAuth client in the
Cloud Console if they leak.
