#!/usr/bin/env python3
"""
Deployment verification script - Run this to ensure everything is ready
"""

import os
import sys

def check_file_contents():
    """Verify critical files have correct content"""
    print("🔍 Verifying deployment files...")
    
    # Check requirements.txt
    try:
        with open('requirements.txt', 'r') as f:
            requirements = f.read()
            
        required_packages = [
            'gspread==5.12.4',
            'google-auth==2.30.0', 
            'google-auth-oauthlib==1.0.0',
            'google-auth-httplib2==0.2.0',
            'cachetools==5.3.1'
        ]
        
        missing = []
        for package in required_packages:
            if package not in requirements:
                missing.append(package)
        
        if missing:
            print(f"❌ Missing packages in requirements.txt: {missing}")
            return False
        else:
            print("✅ requirements.txt has all required packages")
            
    except FileNotFoundError:
        print("❌ requirements.txt not found")
        return False
    
    # Check runtime.txt
    try:
        with open('runtime.txt', 'r') as f:
            runtime = f.read().strip()
            
        if runtime == 'python-3.11.9':
            print("✅ runtime.txt is correct")
        else:
            print(f"❌ runtime.txt should be 'python-3.11.9', found: '{runtime}'")
            return False
            
    except FileNotFoundError:
        print("❌ runtime.txt not found")
        return False
    
    # Check app.py exists
    if os.path.exists('app.py'):
        print("✅ app.py exists")
    else:
        print("❌ app.py not found")
        return False
    
    return True

def check_git_status():
    """Check if files are committed to git"""
    print("\n🔍 Checking git status...")
    
    try:
        import subprocess
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            if result.stdout.strip():
                print("⚠️  Uncommitted changes found:")
                print(result.stdout)
                print("💡 Run: git add . && git commit -m 'Fix deployment' && git push")
                return False
            else:
                print("✅ All files are committed")
                return True
        else:
            print("❌ Git status check failed")
            return False
            
    except Exception as e:
        print(f"⚠️  Could not check git status: {e}")
        return True  # Don't fail if git is not available

def main():
    print("🚀 STREAMLIT CLOUD DEPLOYMENT VERIFICATION")
    print("=" * 50)
    
    checks = [
        ("File Contents", check_file_contents),
        ("Git Status", check_git_status)
    ]
    
    all_passed = True
    for check_name, check_func in checks:
        try:
            result = check_func()
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ {check_name} failed: {e}")
            all_passed = False
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED!")
        print("✅ Your deployment is ready for Streamlit Cloud")
        print("\n📋 Next steps:")
        print("1. Clear Streamlit Cloud cache")
        print("2. Reboot your app")
        print("3. Check deployment logs")
    else:
        print("⚠️  SOME CHECKS FAILED!")
        print("❌ Fix the issues above before deploying")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)