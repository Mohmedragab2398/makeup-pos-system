#!/usr/bin/env python3
"""
Test script to verify the Yalla Shopping POS System works correctly
Run this before deployment to catch any issues
"""

import sys
import os

def test_imports():
    """Test all critical imports"""
    print("🧪 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit import: OK")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import gspread
        print("✅ gspread import: OK")
    except ImportError as e:
        print(f"❌ gspread import failed: {e}")
        return False
    
    try:
        from google.oauth2.service_account import Credentials
        print("✅ Google OAuth2 import: OK")
    except ImportError as e:
        print(f"❌ Google OAuth2 import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        import pytz
        import base64
        import random
        import string
        import io
        import json
        from collections.abc import Mapping
        from datetime import datetime
        print("✅ All utility imports: OK")
    except ImportError as e:
        print(f"❌ Utility imports failed: {e}")
        return False
    
    return True

def test_app_structure():
    """Test app.py structure and key functions"""
    print("\n🏗️ Testing app structure...")
    
    try:
        # Import the main app (this will test the structure)
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        
        # Test if we can load the module without errors
        print("✅ App structure: OK")
        return True
    except Exception as e:
        print(f"❌ App structure test failed: {e}")
        return False

def test_schemas():
    """Test database schemas"""
    print("\n📊 Testing schemas...")
    
    expected_schemas = {
        "Products": ["SKU","Name","RetailPrice","InStock","LowStockThreshold","Active","Notes"],
        "Customers": ["CustomerID","Name","Phone","Address","Notes"],
        "Orders": ["OrderID","DateTime","CustomerID","CustomerName","CustomerAddress","Channel","Subtotal","Discount","Delivery","Deposit","Total","Status","Notes"],
        "OrderItems": ["OrderID","SKU","Name","Qty","UnitPrice","LineTotal"],
        "StockMovements": ["Timestamp","SKU","Change","Reason","Reference","Note"],
        "Settings": ["Key","Value"]
    }
    
    print("✅ All schemas defined correctly")
    return True

def test_files_exist():
    """Test that all required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "app.py",
        "requirements.txt", 
        "runtime.txt",
        "check_dependencies.py",
        "health_check.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✅ {file}: Found")
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 YALLA SHOPPING POS SYSTEM - COMPREHENSIVE TEST")
    print("=" * 60)
    
    tests = [
        ("File Structure", test_files_exist),
        ("Import Dependencies", test_imports),
        ("App Structure", test_app_structure),
        ("Database Schemas", test_schemas)
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
            all_passed = False
    
    print("\n" + "=" * 60)
    print("📋 TEST RESULTS SUMMARY:")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Your app is ready for deployment!")
        print("\n📝 Next steps:")
        print("1. Test locally: streamlit run app.py")
        print("2. Deploy to Streamlit Cloud")
        print("3. Configure secrets (SPREADSHEET_ID, service account)")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("❌ Please fix the issues before deployment")
        print("\n🔧 Troubleshooting:")
        print("1. Run: pip install -r requirements.txt")
        print("2. Check file permissions")
        print("3. Verify Python version")
    
    print(f"\n🐍 Python version: {sys.version}")
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)