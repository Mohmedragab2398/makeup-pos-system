#!/usr/bin/env python3
"""
Quick test script to verify all required imports work correctly.
Run this after installing requirements.txt to ensure everything is working.
"""

def test_imports():
    """Test all required imports"""
    try:
        print("Testing imports...")
        
        import streamlit as st
        print("✅ streamlit imported successfully")
        
        import pandas as pd
        print("✅ pandas imported successfully")
        
        import gspread
        print("✅ gspread imported successfully")
        
        from google.oauth2.service_account import Credentials
        print("✅ google.oauth2.service_account imported successfully")
        
        import pytz
        print("✅ pytz imported successfully")
        
        import numpy as np
        print("✅ numpy imported successfully")
        
        import requests
        print("✅ requests imported successfully")
        
        print("\n🎉 All imports successful! The app should work correctly.")
        return True
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Please ensure all dependencies are installed:")
        print("pip install -r requirements.txt")
        return False
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
