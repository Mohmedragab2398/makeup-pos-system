#!/usr/bin/env python3
"""
Dependency checker for Streamlit deployment
Run this script to verify all dependencies are properly installed
"""

import sys
import importlib

def check_dependency(module_name, package_name=None):
    """Check if a module can be imported"""
    try:
        importlib.import_module(module_name)
        print(f"✅ {module_name} - OK")
        return True
    except ImportError as e:
        package = package_name or module_name
        print(f"❌ {module_name} - FAILED: {e}")
        print(f"   Try: pip install {package}")
        return False

def main():
    print("🔍 Checking dependencies for Yalla Shopping POS System...")
    print("=" * 50)
    
    dependencies = [
        ("streamlit", "streamlit>=1.28.0"),
        ("gspread", "gspread>=5.12.4"),
        ("google.auth", "google-auth>=2.30.0"),
        ("google.oauth2.service_account", "google-auth>=2.30.0"),
        ("google_auth_oauthlib", "google-auth-oauthlib>=1.0.0"),
        ("google_auth_httplib2", "google-auth-httplib2>=0.2.0"),
        ("pandas", "pandas>=2.0.0"),
        ("pytz", "pytz>=2023.3"),
        ("numpy", "numpy>=1.24.0"),
        ("requests", "requests>=2.31.0"),
        ("cachetools", "cachetools>=5.3.1"),
    ]
    
    all_good = True
    for module, package in dependencies:
        if not check_dependency(module, package):
            all_good = False
    
    print("=" * 50)
    if all_good:
        print("🎉 All dependencies are properly installed!")
        print("✅ Your app should work correctly on Streamlit Cloud")
    else:
        print("⚠️  Some dependencies are missing or incompatible")
        print("📝 Please install the missing packages and try again")
        print("\n💡 Quick fix - run this command:")
        print("pip install -r requirements.txt")
    
    print(f"\n🐍 Python version: {sys.version}")

if __name__ == "__main__":
    main()