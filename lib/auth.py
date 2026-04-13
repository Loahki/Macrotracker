"""Google Sheets authentication for Macro Tracker.

Priority order:
1. GOOGLE_SERVICE_ACCOUNT_JSON env var (explicit SA key, e.g. Render/Railway)
2. Application Default Credentials (Cloud Run — uses attached service account)
3. OAuth token file (local desktop)
"""

import json
import os

import gspread
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from lib.config import CONFIG_DIR, CREDS_FILE, TOKEN_FILE

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.file',
]


def get_client() -> gspread.Client:
    """Authenticate with Google and return an authorised gspread client."""

    # 1. Explicit service account JSON env var
    sa_json = os.environ.get('GOOGLE_SERVICE_ACCOUNT_JSON')
    if sa_json:
        from google.oauth2.service_account import Credentials as SACredentials
        info = json.loads(sa_json)
        creds = SACredentials.from_service_account_info(info, scopes=SCOPES)
        return gspread.authorize(creds)

    # 2. Application Default Credentials (Cloud Run attaches the SA automatically)
    if not os.path.exists(TOKEN_FILE):
        try:
            import google.auth
            creds, _ = google.auth.default(scopes=SCOPES)
            return gspread.authorize(creds)
        except Exception:
            pass  # Not on GCP — fall through to local OAuth

    # 3. Local OAuth token file
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CREDS_FILE):
                raise FileNotFoundError(
                    f"\ncredentials.json not found at: {CREDS_FILE}\n\n"
                    "Complete Google Cloud Console setup first:\n"
                    "  See: setup/google_cloud_setup.md\n"
                    f"  Then copy your credentials.json to: {CREDS_FILE}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return gspread.authorize(creds)
