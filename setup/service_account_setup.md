# Cloud Deployment Setup — Service Account + Railway

This replaces the OAuth flow for cloud/phone use. Your desktop no longer needs to be on.

---

## Step 1 — Create a Service Account in Google Cloud Console

1. Go to: https://console.cloud.google.com/ → select your **MacroTracker** project
2. Sidebar → **"IAM & Admin"** → **"Service Accounts"**
3. Click **"+ Create Service Account"**
   - Name: `macro-tracker`
   - Click **"Create and Continue"** → **"Done"** (no roles needed)
4. Click the new service account email to open it
5. Go to the **"Keys"** tab → **"Add Key"** → **"Create new key"** → **JSON** → **"Create"**
6. A `.json` file downloads — keep it safe, treat it like a password

---

## Step 2 — Share Your Google Sheet with the Service Account

1. Open your Macro Tracker Google Sheet
2. Click **"Share"** (top right)
3. Paste the service account email (looks like `macro-tracker@your-project.iam.gserviceaccount.com`)
4. Set permission to **"Editor"**
5. Click **"Send"** (ignore the warning about sharing with a non-Google account)

---

## Step 3 — Deploy to Railway

1. Push this repo to GitHub if you haven't already:
   ```bash
   cd ~/Macrotracker
   git add .
   git commit -m "add cloud deployment"
   git push
   ```

2. Go to https://railway.app → **"New Project"** → **"Deploy from GitHub repo"** → select your repo

3. Once deployed, go to your service → **"Variables"** tab and add:

   | Variable | Value |
   |---|---|
   | `MCP_TRANSPORT` | `http` |
   | `SPREADSHEET_ID` | `1un97GuVyZSGzkq4AC-stLyxh_GR2Iw6bpuRJPxZyzvQ` |
   | `GOOGLE_SERVICE_ACCOUNT_JSON` | *(paste the entire contents of the downloaded JSON file)* |

4. Railway will redeploy automatically. Check the **"Deployments"** tab — it should show a green checkmark.

5. Go to **"Settings"** → **"Networking"** → enable **"Public Networking"** and note your URL
   (looks like `https://macro-tracker-production-xxxx.up.railway.app`)

---

## Step 4 — Connect to Claude.ai on Your Phone

1. Open the Claude app → **Settings** → **"Claude Code"** → **"MCP Servers"** → **"Add server"**
2. Enter your Railway URL + `/mcp`:
   ```
   https://macro-tracker-production-xxxx.up.railway.app/mcp
   ```
3. Name it `macro-tracker`
4. Save — Claude will connect and the tools will appear

---

## Step 5 — Verify

In Claude (phone or desktop), say:
> "Show me my macro totals for today"

Claude should call `get_today_totals` and show your sheet data.

---

## Notes

- Railway's free tier gives 500 hours/month — enough for always-on
- The service URL is your only "password" — don't share it publicly
- High-activity days are now stored in the Google Sheet Config tab instead of your local config file
- Your local desktop setup continues to work unchanged (OAuth token still valid)
