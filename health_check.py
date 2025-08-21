#!/usr/bin/env python3
"""
Health check script for the Streamlit app
Run this to verify all dependencies are properly installed
"""

def check_imports():
    """Check if all required packages can be imported"""
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import gspread
        print("✅ gspread imported successfully")
    except ImportError as e:
        print(f"❌ gspread import failed: {e}")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ google.oauth2.service_account imported successfully")
    except ImportError as e:
        print(f"❌ google.oauth2.service_account import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✅ pandas imported successfully")
    except ImportError as e:
        print(f"❌ pandas import failed: {e}")
        return False
    
    try:
        import pytz
        print("✅ pytz imported successfully")
    except ImportError as e:
        print(f"❌ pytz import failed: {e}")
        return False
    
    return True

def check_versions():
    """Check package versions"""
    import streamlit as st
    import gspread
    import google.auth
    import pandas as pd
    import pytz
    import numpy as np
    
    print(f"📦 Streamlit version: {st.__version__}")
    print(f"📦 gspread version: {gspread.__version__}")
    print(f"📦 google-auth version: {google.auth.__version__}")
    print(f"📦 pandas version: {pd.__version__}")
    print(f"📦 pytz version: {pytz.__version__}")
    print(f"📦 numpy version: {np.__version__}")

if __name__ == "__main__":
    print("🔍 Checking imports...")
    if check_imports():
        print("\n🔍 Checking versions...")
        check_versions()
        print("\n✅ All checks passed! Your environment is ready.")
    else:
        print("\n❌ Some imports failed. Please install missing packages:")
        print("pip install -r requirements.txt")