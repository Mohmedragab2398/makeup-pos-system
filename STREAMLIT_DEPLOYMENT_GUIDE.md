# Streamlit Cloud Deployment Guide

## Quick Fix for Current Issue

The `gspread` import error is likely due to missing dependencies. Follow these steps:

### 1. Updated Requirements
Your `requirements.txt` has been updated with more specific versions:
```
streamlit>=1.28.0
gspread>=5.12.4
google-auth>=2.30.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
pandas>=2.0.0
pytz>=2023.3
numpy>=1.24.0
requests>=2.31.0
```

### 2. Deployment Steps

1. **Commit and Push Changes**:
   ```bash
   git add .
   git commit -m "Fix gspread dependency issues for Streamlit deployment"
   git push origin main
   ```

2. **Streamlit Cloud Setup**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository: `https://github.com/Mohmedragab2398/makeup-pos-system.git`
   - Set main file path: `app.py`
   - Set Python version: `3.9` or `3.10`

3. **Configure Secrets**:
   In Streamlit Cloud, add these secrets:
   ```toml
   # Streamlit secrets
   SPREADSHEET_ID = "your_google_sheets_id_here"
   
   [gcp_service_account]
   type = "service_account"
   project_id = "your_project_id"
   private_key_id = "your_private_key_id"
   private_key = "-----BEGIN PRIVATE KEY-----\nyour_private_key_here\n-----END PRIVATE KEY-----"
   client_email = "your_service_account_email"
   client_id = "your_client_id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "your_cert_url"
   ```

### 3. Troubleshooting

If you still get import errors:

1. **Check Python Version**: Ensure you're using Python 3.9 or 3.10
2. **Clear Cache**: In Streamlit Cloud, try "Reboot app"
3. **Check Logs**: Look at the deployment logs for specific error messages

### 4. Local Testing

Before deploying, test locally:
```bash
python check_dependencies.py
streamlit run app.py
```

### 5. Common Issues

- **Service Account**: Make sure your Google Service Account has access to the spreadsheet
- **Spreadsheet ID**: Verify the SPREADSHEET_ID is correct
- **Permissions**: Ensure the service account has Editor permissions on the Google Sheet

## Support

If you continue having issues:
1. Check the Streamlit Cloud logs
2. Verify all secrets are properly configured
3. Ensure your Google Sheets setup is correct