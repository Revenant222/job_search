## Google Sheets Logger Integration Guide

This guide packages everything a teammate needs to wire up Google Sheets API access for both reading and writing data, plus an hourly logger that appends rows to a designated sheet.

---

### 1. Enable Google APIs
- Visit Google Cloud Console and either create or reuse a project.
- Enable both `Google Sheets API` and `Google Drive API` (Drive lets the Sheets client discover files).
- In **APIs & Services → Credentials**, create one of the following:
  - **Service account** (preferred for automation). Download the JSON key (e.g. `service-account.json`) and store securely.
  - **OAuth client** (if a user grants access interactively). Keep the `credentials.json` that Google provides.

---

### 2. Grant Sheet Access
- Open the spreadsheet in Google Sheets.
- Share it with either the service account email (`<name>@<project>.iam.gserviceaccount.com`) or the Google account that will complete the OAuth flow.
- Capture the spreadsheet ID from the URL: `https://docs.google.com/spreadsheets/d/<spreadsheetId>/edit`.

---

### 3. Local Environment Setup
```bash
python -m venv .venv
. .venv/bin/activate            # .venv\Scripts\activate on Windows
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```
- Store the credential JSON in the repo root (or update paths below accordingly).

---

### 4. Auth Helpers (`sheets_client.py`)

**Service account version**
```python
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
CREDS_PATH = Path("service-account.json")

def get_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        CREDS_PATH,
        scopes=SCOPES,
    )
    return build("sheets", "v4", credentials=creds)

service = get_sheets_service()
sheet = service.spreadsheets()
```

**OAuth user flow (swap into the helper if needed)**
```python
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def get_user_creds():
    token_path = Path("token.json")
    if token_path.exists():
        return Credentials.from_authorized_user_file(token_path, SCOPES)

    flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
    creds = flow.run_local_server(port=0)
    token_path.write_text(creds.to_json())
    return creds
```

---

### 5. Reading Values
```python
from sheets_client import sheet

def read_logs(spreadsheet_id, range_name="Logs!A:C"):
    response = sheet.values().get(
        spreadsheetId=spreadsheet_id,
        range=range_name,
    ).execute()
    return response.get("values", [])

if __name__ == "__main__":
    for row in read_logs("<spreadsheet-id>")[-10:]:
        print(row)
```

---

### 6. Appending Rows
```python
from datetime import datetime
from sheets_client import sheet

def append_log(spreadsheet_id, values, range_name="Logs!A:C"):
    sheet.values().append(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption="USER_ENTERED",
        insertDataOption="INSERT_ROWS",
        body={"values": [values]},
    ).execute()

if __name__ == "__main__":
    append_log(
        "<spreadsheet-id>",
        [datetime.utcnow().isoformat(), "logger", "Started hourly job"],
    )
```

---

### 7. Hourly Logger (`hourly_logger.py`)
```python
import random
from datetime import datetime
from sheets_client import append_log

SPREADSHEET_ID = "<spreadsheet-id>"
RANGE = "Logs!A:C"

def build_entry():
    return [
        datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "agent-logger",
        f"Heartbeat {random.randint(1000, 9999)}",
    ]

def run_once():
    append_log(SPREADSHEET_ID, build_entry(), range_name=RANGE)

if __name__ == "__main__":
    run_once()
```

---

### 8. Scheduling the Logger

**Windows Task Scheduler**
1. Create Basic Task → Trigger: Daily → Repeat every 1 hour indefinitely.
2. Action: `Start a program`.
   - Program/script: `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe`
   - Arguments: `-File "F:\Coding\job_search\.venv\Scripts\Activate.ps1"; python F:\Coding\job_search\hourly_logger.py`

**cron (Linux/macOS)**
```
0 * * * * /path/to/.venv/bin/python /path/to/hourly_logger.py >> /var/log/sheets.log 2>&1
```

---

### 9. Testing Checklist
- Run `python hourly_logger.py` manually; confirm a fresh row in the sheet.
- Exercise `read_logs` and `append_log` with intentional failures (bad ID, missing share) to confirm useful errors.
- Monitor API quotas in Cloud Console if multiple agents write frequently; add exponential backoff if needed.

---

### 10. Handoff Notes
- Share the spreadsheet ID, range names, and credential JSON securely.
- Document where the scheduled task lives and how to restart/update it.
- Rotate service-account keys per security policy.


