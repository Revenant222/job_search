# Google Service Account Setup - Complete Walkthrough

This guide will walk you through setting up a Google Service Account from scratch, step-by-step, with direct links and detailed instructions.

## 📋 Prerequisites

- A Google account (Gmail account works)
- Access to the Google Sheet you want to read from (Amir Satvat's combined jobs workbook at https://docs.google.com/spreadsheets/d/1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE/edit?gid=935305590#gid=935305590 is what this is built to work around)
- Basic familiarity with web browsers

## 🎯 What We're Doing

We're creating a "service account" - a special Google account that can access your Google Sheet automatically without requiring you to log in each time. This is perfect for automated scripts and background jobs.

**Total Time:** ~10-15 minutes

---

## Step 1: Go to Google Cloud Console

**Direct Link:** https://console.cloud.google.com/

1. Open the link above in your browser
2. Sign in with your Google account if prompted
3. You'll see the Google Cloud Console dashboard

**What you'll see:**
- A search bar at the top
- A project selector dropdown (top left, may say "Select a project" or show a project name)
- Various menu options on the left sidebar

---

## Step 2: Create a New Project (or Select Existing)

### Option A: Create a New Project (Recommended for First Time)

1. **Click the project dropdown** at the top left (next to "Google Cloud")
   - It may say "Select a project" or show an existing project name

2. **Click "NEW PROJECT"** button (top right of the dropdown)

3. **Fill in the project details:**
   - **Project name:** Enter something descriptive like `job-search-app` or `my-job-tracker`
   - **Organization:** Leave as default (or select if you have one)
   - **Location:** Leave as default

4. **Click "CREATE"** button

5. **Wait for creation** (usually 10-30 seconds)
   - You'll see a notification: "Project [name] created successfully"

6. **Select your new project** from the dropdown if it's not already selected

### Option B: Use an Existing Project

1. **Click the project dropdown** at the top left
2. **Select your existing project** from the list

**Direct Link to Project Creation:** https://console.cloud.google.com/projectcreate

---

## Step 3: Enable Google Sheets API

**Why this is important:** Even though you'll download a credentials file, the API itself must be enabled separately. The credentials file and the API are two different things.

**Direct Link:** https://console.cloud.google.com/apis/library/sheets.googleapis.com

1. **Open the link above** (or navigate manually: **APIs & Services** > **Library** from the left menu)

2. **Verify your project is selected** (check the project dropdown at the top)

3. **Look for "Google Sheets API"** in the list
   - You can use the search box at the top to find it quickly

4. **Click on "Google Sheets API"** card

5. **Click the blue "ENABLE" button** (top of the page)

6. **Wait for confirmation** (usually instant)
   - You'll see: "API enabled" with a green checkmark
   - The page will refresh and show API details

**Note:** You may see a message like "To call this API from your own applications, you may need to create credentials." This is referring to OAuth credentials for user-based apps. **You can ignore this** - we're creating a service account instead, which is different.

---

## Step 4: Create a Service Account

**Direct Link:** https://console.cloud.google.com/iam-admin/serviceaccounts

1. **Open the link above** (or navigate manually: **IAM & Admin** > **Service Accounts** from the left menu)

2. **Verify your project is selected** (check the project dropdown at the top)

3. **Click the blue "+ CREATE SERVICE ACCOUNT" button** (top of the page)

4. **Fill in Service Account Details:**
   
   **Service account name:**
   - Enter something descriptive like `job-sheet-reader` or `job-search-reader`
   - This is just a label for your reference
   
   **Service account ID:**
   - This auto-fills based on the name (you can change it if needed)
   - Format: `job-sheet-reader` (lowercase, hyphens allowed)
   
   **Service account description (optional):**
   - Enter: `Service account for reading job search data from Google Sheets`
   - This helps you remember what it's for later

5. **Click "CREATE AND CONTINUE"** button

6. **Grant Permissions (Optional):**
   - **You can skip this step!** For basic sheet reading, you don't need to grant any roles here
   - The service account will access sheets via sharing (we'll do that in Step 7)
   - Click "CONTINUE" to skip role assignment

7. **Grant Users Access (Optional):**
   - **You can skip this too!** This is for giving other people access to manage the service account
   - Click "DONE" to finish

**Result:** You'll see your new service account in the list with a green checkmark.

---

## Step 5: Create and Download the JSON Key File

**This is the credentials file your application needs!**

1. **Click on your service account name** in the list (the one you just created)

2. **Click the "KEYS" tab** (top of the page, next to "DETAILS")

3. **Click "ADD KEY"** dropdown button (top right)

4. **Select "Create new key"** from the dropdown

5. **Select "JSON"** as the key type
   - A dialog will appear with two options: JSON and P12
   - **Choose JSON** (it's easier to work with)

6. **Click "CREATE"** button

7. **The JSON file will download automatically**
   - Check your browser's download folder
   - The filename will be something like: `your-project-name-abc123def456.json`
   - **This file contains sensitive credentials - keep it secure!**

8. **Note the Service Account Email Address:**
   - While you're on the service account details page, look for the **"Email"** field
   - It will look like: `job-sheet-reader@your-project-id.iam.gserviceaccount.com`
   - **Copy this email address** - you'll need it in Step 7
   - You can also find it in the downloaded JSON file under `"client_email"`

---

## Step 6: Save the Credentials File in Your Project

1. **Rename the downloaded file** to: `service_account_credentials.json`
   - The original name is long and hard to remember
   - Make sure it ends with `.json`

2. **Move the file** to your project's `config/` folder:
   ```
   job_search/
   └── config/
       └── service_account_credentials.json  ← Put it here
   ```

3. **Verify the file structure:**
   - Open the JSON file in a text editor to confirm it looks correct
   - It should have fields like: `type`, `project_id`, `private_key`, `client_email`, etc.
   - Compare it with `config/service_account_credentials_template.json` to verify structure

**Security Reminder:** 
- This file contains sensitive keys
- Never commit it to Git (it's already in `.gitignore`)
- Don't share it publicly
- If it's ever compromised, delete the key in Google Cloud Console and create a new one

---

## Step 7: Share Your Google Sheet with the Service Account

**This is the critical step!** The service account needs explicit permission to access your specific sheet.

**Direct Link to Google Sheets:** https://sheets.google.com

1. **Open your Google Sheet** (the one containing your job data)

2. **Click the "Share" button** (top right corner, blue button)

3. **In the "Add people and groups" field:**
   - **Paste the service account email address** you copied in Step 5
   - Format: `your-service-account@your-project-id.iam.gserviceaccount.com`
   - Example: `job-sheet-reader@my-project-12345.iam.gserviceaccount.com`

4. **Set the permission level:**
   - **Click the dropdown** next to the email field (it may say "Editor" by default)
   - **Select "Viewer"** (for read-only access)
   - This is sufficient for reading data from the sheet

5. **Uncheck "Notify people"** checkbox
   - Service accounts don't have email addresses, so notifications won't work
   - This prevents an error message

6. **Click "Share"** button (bottom right)

7. **Verify the share:**
   - You should see the service account email appear in the "People with access" list
   - It should show "Viewer" permission
   - You can close the share dialog

**Important Notes:**
- The service account email must match **exactly** (including the `.iam.gserviceaccount.com` part)
- If you get "User not found" error, double-check the email address
- The service account will appear in the share list even though it's not a "real" user

---

## Step 8: Configure Your Application

Now you need to tell your application to use the service account.

1. **Create or edit your `.env` file** in the project root:
   ```
   job_search/
   └── .env  ← Create or edit this file
   ```

2. **Add these lines to your `.env` file:**
   ```env
   # Use service account instead of OAuth
   GOOGLE_USE_SERVICE_ACCOUNT=true
   GOOGLE_SERVICE_ACCOUNT_PATH=config/service_account_credentials.json
   
   # For read-only access (recommended)
   GOOGLE_SHEETS_SCOPES=https://www.googleapis.com/auth/spreadsheets.readonly
   
   # Your Google Sheet ID (found in the sheet URL)
   GOOGLE_SHEET_ID=your-sheet-id-here
   
   # Sheet range to read (adjust as needed)
   GOOGLE_SHEET_RANGE=New Workbook!A8:Q
   ```

3. **Find your Google Sheet ID:**
   - Open your Google Sheet
   - Look at the URL in your browser
   - It will look like: `https://docs.google.com/spreadsheets/d/1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE/edit`
   - The Sheet ID is the long string between `/d/` and `/edit`
   - In this example: `1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE`
   - Copy this and paste it as `GOOGLE_SHEET_ID` in your `.env` file
   - - For Amir Satvat's Combined Job Workbook, the Google Sheet Id is **'1ZOJpVS3CcnrkwhpRgkP7tzf3wc4OWQj-uoWFfv4oHZE'**

4. **Save the `.env` file**

---

## Step 9: Test Your Setup

Let's verify everything works!

1. **Open a terminal/command prompt** in your project directory

2. **Activate your virtual environment:**
   ```bash
   # Windows PowerShell
   .venv\Scripts\Activate.ps1
   
   # Windows Command Prompt
   .venv\Scripts\activate.bat
   
   # Linux/Mac
   source .venv/bin/activate
   ```

3. **Run the test script:**
   ```bash
   python scripts/tests/test_service_account.py
   ```

4. **What to expect:**
   - ✅ **Success:** You'll see "All tests passed!" and details about your sheet
   - ❌ **Error:** Check the error message and refer to Troubleshooting below

---

## ✅ Verification Checklist

Before considering setup complete, verify:

- [ ] Service account created in Google Cloud Console
- [ ] Google Sheets API enabled for your project
- [ ] JSON key file downloaded and saved as `config/service_account_credentials.json`
- [ ] Google Sheet shared with service account email (Viewer permission)
- [ ] `.env` file configured with `GOOGLE_USE_SERVICE_ACCOUNT=true`
- [ ] Test script runs successfully

---

## 🔧 Troubleshooting

### Error: "Access Denied" or "Permission Denied"

**Cause:** The sheet isn't shared with the service account, or the email address is wrong.

**Solution:**
1. Double-check the service account email address in the JSON file (`client_email` field)
2. Verify the sheet is shared with that exact email address
3. Make sure the permission is set to at least "Viewer"
4. Try removing and re-adding the service account to the sheet share list

### Error: "API not enabled"

**Cause:** Google Sheets API isn't enabled for your project.

**Solution:**
1. Go to: https://console.cloud.google.com/apis/library/sheets.googleapis.com
2. Make sure your project is selected (check dropdown at top)
3. Click "ENABLE" if it's not already enabled
4. Wait a few seconds and try again

### Error: "The caller does not have permission"

**Cause:** Usually means the sheet isn't shared with the service account.

**Solution:**
1. Verify the service account email matches exactly (copy-paste from JSON file)
2. Check that the sheet is shared (open Share dialog and confirm email is listed)
3. Ensure permission is "Viewer" or higher

### Error: "File not found" or "Credentials file not found"

**Cause:** The path to the credentials file is wrong.

**Solution:**
1. Verify the file exists at: `config/service_account_credentials.json`
2. Check your `.env` file has: `GOOGLE_SERVICE_ACCOUNT_PATH=config/service_account_credentials.json`
3. Make sure you're running scripts from the project root directory

### Error: "Invalid credentials" or "Malformed JSON"

**Cause:** The JSON file is corrupted or incomplete.

**Solution:**
1. Re-download the key file from Google Cloud Console (delete the old one first)
2. Make sure the entire file was downloaded (check file size)
3. Verify the JSON is valid (use a JSON validator online)
4. Compare with the template file structure

---

## 📚 Additional Resources

- **Google Cloud Console:** https://console.cloud.google.com/
- **Google Sheets API Documentation:** https://developers.google.com/sheets/api
- **Service Accounts Overview:** https://cloud.google.com/iam/docs/service-accounts
- **Project Setup Guide:** See `docs/SETUP_GUIDE.md` in this repository

---

## 🔒 Security Best Practices

1. **Never commit credentials:** The `.gitignore` file already excludes `config/service_account_credentials.json` and `.env` files
2. **Use read-only scopes:** We're using `spreadsheets.readonly` - only change this if you need write access
3. **Limit sheet access:** Only share the specific sheets the service account needs, not your entire Drive
4. **Rotate keys periodically:** Create new keys every 6-12 months and delete old ones
5. **Use separate service accounts:** Create different accounts for different projects/environments

---

## 🎉 You're Done!

If you've completed all steps and the test script passes, your Google Service Account is set up correctly! Your application can now read data from your Google Sheet automatically.

**Next Steps:**
- Run your application: `python scripts/batch/run_app.bat` or `streamlit run src/streamlit_app.py`
- Test delta analysis: `python scripts/tests/test_delta_analysis.py`
- Review the main documentation: `docs/SETUP_GUIDE.md`

---

## 📝 Quick Reference

**Service Account Email Format:**
```
service-account-name@project-id.iam.gserviceaccount.com
```

**Google Sheet ID Location:**
```
https://docs.google.com/spreadsheets/d/SHEET_ID_HERE/edit
```

**Required Files:**
- `config/service_account_credentials.json` (your downloaded key file)
- `.env` (configuration file)

**Required Google Cloud Setup:**
- Project created
- Google Sheets API enabled
- Service account created
- JSON key downloaded
- Sheet shared with service account email

---

**Questions or Issues?** Check the troubleshooting section above or review the detailed technical documentation in `.cursor/docs/service_account_setup.md`.

