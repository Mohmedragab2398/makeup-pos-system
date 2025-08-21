#!/usr/bin/env python3
"""
Quick test runner to verify the system is ready
"""

import subprocess
import sys
import os

def run_test(script_name, description):
    """Run a test script and return the result"""
    print(f"\n🧪 Running {description}...")
    print("-" * 50)
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, timeout=30)
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False

def main():
    print("🚀 YALLA SHOPPING POS - QUICK TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("check_dependencies.py", "Dependency Check"),
        ("health_check.py", "Health Check"),
        ("test_app.py", "Comprehensive App Test")
    ]
    
    results = []
    for script, description in tests:
        if os.path.exists(script):
            result = run_test(script, description)
            results.append((description, result))
        else:
            print(f"❌ {script} not found")
            results.append((description, False))
    
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS:")
    print("=" * 60)
    
    all_passed = True
    for description, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {description}")
        if not passed:
            all_passed = False
    
    print("=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED! SYSTEM IS READY!")
        print("✅ You can now deploy to GitHub and Streamlit Cloud")
    else:
        print("⚠️  SOME TESTS FAILED!")
        print("❌ Please fix issues before deployment")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)