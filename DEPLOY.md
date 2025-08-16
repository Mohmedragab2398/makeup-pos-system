# 🚀 Streamlit Cloud Deployment

## Quick Steps:

1. **Go to**: https://share.streamlit.io
2. **Sign in** with GitHub
3. **Click "New app"**
4. **Select repo**: `makeup-pos-system`
5. **Set path**: `app.py`
6. **Click "Deploy!"**

## 🔑 Add Secrets:

In Streamlit Cloud → App Settings → Secrets:

```toml
SPREADSHEET_ID = "1lR4bvgiUcw_6phvWb9-gDCZSdghVxlK-zXacb84xpws"

[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
client_email = "your-service-account@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
```

## 🎯 App Password: `yalla2024`
