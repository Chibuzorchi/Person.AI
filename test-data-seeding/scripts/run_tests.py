#!/usr/bin/env python3
"""
Test runner script
"""
import subprocess
import sys
import time
import requests

def wait_for_services():
    """Wait for services to be ready"""
    print("⏳ Waiting for services to be ready...")
    
    services = [
        ("QuickBooks Mock", "http://localhost:5000/health"),
        ("Salesforce Mock", "http://localhost:5001/health")
    ]
    
    for service_name, url in services:
        max_retries = 24  # 2 minutes
        for i in range(max_retries):
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    print(f"   ✅ {service_name} is ready")
                    break
            except:
                pass
            
            if i == max_retries - 1:
                print(f"   ❌ {service_name} failed to start")
                return False
            
            time.sleep(5)
    
    return True

def run_tests():
    """Run all tests"""
    print("🧪 Running test suite...")
    
    # Run data generation tests
    print("\n📊 Running data generation tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_data_generation.py", 
        "-v", "--tb=short"
    ], cwd="/app")
    
    if result.returncode != 0:
        print("❌ Data generation tests failed")
        return False
    
    # Run API mock tests
    print("\n🔌 Running API mock tests...")
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/test_api_mocks.py", 
        "-v", "--tb=short"
    ], cwd="/app")
    
    if result.returncode != 0:
        print("❌ API mock tests failed")
        return False
    
    print("\n✅ All tests passed!")
    return True

def main():
    """Main test runner"""
    print("🚀 Test Data Seeding - Test Runner")
    print("=" * 50)
    
    # Wait for services
    if not wait_for_services():
        print("❌ Services not ready, exiting")
        sys.exit(1)
    
    # Run tests
    if not run_tests():
        print("❌ Tests failed, exiting")
        sys.exit(1)
    
    print("\n🎉 All tests completed successfully!")

if __name__ == '__main__':
    main()
