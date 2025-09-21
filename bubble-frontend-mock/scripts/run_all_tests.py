#!/usr/bin/env python3
"""
Comprehensive Bubble Frontend Test Runner
Runs all test suites for the mock Person.ai frontend
"""

import subprocess
import sys
import time
import requests
from pathlib import Path

class BubbleTestRunner:
    def __init__(self):
        self.frontend_url = "http://localhost:8081"
        self.api_url = "http://localhost:5001/api"
        self.results = {
            "api_tests": {"success": False, "details": ""},
            "ui_tests": {"success": False, "details": ""},
            "visual_tests": {"success": False, "details": ""},
            "integration_tests": {"success": False, "details": ""},
            "overall_success": False
        }
    
    def wait_for_services(self, timeout=120):
        """Wait for frontend and API services to be ready"""
        print("⏳ Waiting for services to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                # Check API
                api_response = requests.get(f"{self.api_url}/health", timeout=5)
                if api_response.status_code == 200:
                    print("✅ API is ready")
                    
                    # Check Frontend
                    frontend_response = requests.get(self.frontend_url, timeout=5)
                    if frontend_response.status_code == 200:
                        print("✅ Frontend is ready")
                        return True
                        
            except requests.exceptions.RequestException:
                pass
            
            time.sleep(2)
        
        print("❌ Services not ready after timeout")
        return False
    
    def run_api_tests(self):
        """Run API tests"""
        print("\n🔧 Running API Tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/test_bubble_api.py", 
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd="/app")
            
            self.results["api_tests"]["success"] = result.returncode == 0
            self.results["api_tests"]["details"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ API Tests Passed")
            else:
                print("❌ API Tests Failed")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            self.results["api_tests"]["success"] = False
            self.results["api_tests"]["details"] = str(e)
            print(f"❌ API Tests Error: {e}")
    
    def run_ui_tests(self):
        """Run UI tests"""
        print("\n🖥️  Running UI Tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/test_bubble_ui.py", 
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd="/app")
            
            self.results["ui_tests"]["success"] = result.returncode == 0
            self.results["ui_tests"]["details"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ UI Tests Passed")
            else:
                print("❌ UI Tests Failed")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            self.results["ui_tests"]["success"] = False
            self.results["ui_tests"]["details"] = str(e)
            print(f"❌ UI Tests Error: {e}")
    
    def run_visual_tests(self):
        """Run visual regression tests"""
        print("\n🎨 Running Visual Regression Tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/test_visual_regression.py", 
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd="/app")
            
            self.results["visual_tests"]["success"] = result.returncode == 0
            self.results["visual_tests"]["details"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ Visual Tests Passed")
            else:
                print("❌ Visual Tests Failed")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            self.results["visual_tests"]["success"] = False
            self.results["visual_tests"]["details"] = str(e)
            print(f"❌ Visual Tests Error: {e}")
    
    def run_integration_tests(self):
        """Run integration workflow tests"""
        print("\n🔗 Running Integration Tests...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                "tests/test_integration_workflows.py", 
                "-v", "--tb=short"
            ], capture_output=True, text=True, cwd="/app")
            
            self.results["integration_tests"]["success"] = result.returncode == 0
            self.results["integration_tests"]["details"] = result.stdout + result.stderr
            
            if result.returncode == 0:
                print("✅ Integration Tests Passed")
            else:
                print("❌ Integration Tests Failed")
                print(result.stdout)
                print(result.stderr)
                
        except Exception as e:
            self.results["integration_tests"]["success"] = False
            self.results["integration_tests"]["details"] = str(e)
            print(f"❌ Integration Tests Error: {e}")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*60)
        print("📊 Bubble Frontend Test Summary")
        print("="*60)
        
        total_tests = len(self.results) - 1  # Exclude overall_success
        passed_tests = sum(1 for key, result in self.results.items() 
                          if key != "overall_success" and result["success"])
        
        print(f"API Tests: {'✅ PASS' if self.results['api_tests']['success'] else '❌ FAIL'}")
        print(f"UI Tests: {'✅ PASS' if self.results['ui_tests']['success'] else '❌ FAIL'}")
        print(f"Visual Tests: {'✅ PASS' if self.results['visual_tests']['success'] else '❌ FAIL'}")
        print(f"Integration Tests: {'✅ PASS' if self.results['integration_tests']['success'] else '❌ FAIL'}")
        
        print(f"\nOverall Result: {passed_tests}/{total_tests} test suites passed")
        
        if passed_tests == total_tests:
            print("🎉 All tests passed! The mock Bubble frontend is working correctly.")
            self.results["overall_success"] = True
        else:
            print("⚠️  Some tests failed. Check the details above.")
            self.results["overall_success"] = False
    
    def save_results(self):
        """Save test results to file"""
        try:
            import json
            results_file = Path("/app/output/bubble_test_results.json")
            results_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(results_file, 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n📝 Results saved to: {results_file}")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")
    
    def run_all_tests(self):
        """Run all test suites"""
        print("🚀 Person.ai Bubble Frontend Test Runner")
        print("="*60)
        
        # Wait for services
        if not self.wait_for_services():
            print("❌ Services not ready, exiting")
            return False
        
        # Run all test suites
        self.run_api_tests()
        self.run_ui_tests()
        self.run_visual_tests()
        self.run_integration_tests()
        
        # Print summary and save results
        self.print_summary()
        self.save_results()
        
        return self.results["overall_success"]

def main():
    """Main function"""
    runner = BubbleTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
