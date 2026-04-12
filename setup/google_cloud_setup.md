# Google Cloud Console — OAuth Setup Guide

Complete these steps once before running `setup/init_sheet.py`.

---

## Step 1 — Create a Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click the **project dropdown** (top-left, next to "Google Cloud").
3. Click **"New Project"**.
4. Name it: `MacroTracker` (or anything you like).
5. Click **"Create"**.
6. Wait ~30 seconds, then click the notification bell → **"Select Project"**.

---

## Step 2 — Enable APIs

1. In the left sidebar, click **"APIs & Services"** → **"Library"**.
2. Search for **"Google Sheets API"** → click it → click **"Enable"**.
3. Go back to Library.
4. Search for **"Google Drive API"** → click it → click **"Enable"**.

---

## Step 3 — Configure the OAuth Consent Screen

1. In the sidebar: **"APIs & Services"** → **"OAuth consent screen"**.
2. Choose **"External"** → click **"Create"**.
3. Fill in required fields:
   - App name: `MacroTracker`
   - User support email: your Gmail address
   - Developer contact email: your Gmail address
4. Click **"Save and Continue"** through the remaining steps (Scopes, Test Users).
   - On the **Scopes** page: click **"Save and Continue"** without adding any scopes
     (the app will request them at runtime).
   - On the **Test users** page: click **"+ Add Users"** and add your own Gmail address.
   - Click **"Save and Continue"**, then **"Back to Dashboard"**.

---

## Step 4 — Create OAuth 2.0 Credentials

1. In the sidebar: **"APIs & Services"** → **"Credentials"**.
2. Click **"+ Create Credentials"** → **"OAuth client ID"**.
3. Application type: **"Desktop app"**.
4. Name: `MacroTracker Desktop`.
5. Click **"Create"**.
6. In the popup, click **"Download JSON"**.
7. Save the file as `credentials.json`.

---

## Step 5 — Place credentials.json

```bash
mkdir -p ~/.macrotracker
mv ~/Downloads/credentials.json ~/.macrotracker/credentials.json
```

Verify it's there:
```bash
ls -la ~/.macrotracker/
# Should show: credentials.json
```

---

## Step 6 — Run the Sheet Initializer

```bash
cd ~/Macrotracker
python3 setup/init_sheet.py
```

- A browser window will open asking you to log in with your Google account.
- Click **"Continue"** through the "unverified app" warning (this is expected for personal apps).
- Grant the requested permissions.
- The browser will show "The authentication flow has completed."
- Return to the terminal — setup will continue automatically.

---

## Step 7 — Verify

```bash
macros today
# Should show: Today: YYYY-MM-DD (Standard Day) with all zeros
```

---

## Troubleshooting

**"Access blocked: This app's request is invalid"**
→ Make sure you added your Gmail to Test Users in Step 3.

**"credentials.json not found"**
→ Check the file is at `~/.macrotracker/credentials.json`.

**"redirect_uri_mismatch"**
→ Make sure you chose "Desktop app" (not Web application) in Step 4.

**Token expired after long absence**
→ Delete `~/.macrotracker/token.json` and re-run any `macros` command to re-authenticate.
