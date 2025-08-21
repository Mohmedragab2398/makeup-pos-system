#!/bin/bash

# Script to commit and push the deployment fixes

echo "🔧 Committing deployment fixes..."

# Add all changed files
git add .

# Commit with descriptive message
git commit -m "Fix Streamlit deployment issues

- Update runtime.txt to python-3.11.9
- Update requirements.txt with compatible versions
- Replace deprecated st.experimental_rerun() with st.rerun()
- Improve import error handling
- Add health check script
- Add deployment documentation"

# Push to main branch
echo "📤 Pushing to GitHub..."
git push origin main

echo "✅ Changes pushed successfully!"
echo "🚀 Your Streamlit app should now deploy without the gspread import error."