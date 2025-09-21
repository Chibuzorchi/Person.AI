#!/usr/bin/env python3
"""
Run All Standalone Tests Script
Runs tests from each component directory to avoid import path issues
"""
import subprocess
import sys
import os
from pathlib import Path

def run_component_tests(component_dir, test_files):
    """Run tests for a specific component"""
    print(f"\n🧪 Testing {component_dir}...")
    print("=" * 50)
    
    os.chdir(component_dir)
    
    # Set CI environment variable
    env = os.environ.copy()
    env['CI'] = 'true'
    
    # Build the pytest command
    cmd = [sys.executable, '-m', 'pytest'] + test_files + ['-v', '--tb=short']
    
    try:
        result = subprocess.run(cmd, env=env, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False
    finally:
        # Return to root directory
        os.chdir('..')

def main():
    """Run all standalone tests"""
    print("🚀 Running All Standalone Tests")
    print("=" * 60)
    
    # Store the original directory
    original_dir = os.getcwd()
    
    # Test components and their standalone test files
    components = {
        'slack-mock': ['tests/test_slack_standalone.py'],
        'test-data-seeding': ['tests/test_api_mocks_standalone.py', 'tests/test_data_generation.py'],
        'e2e-testing': ['tests/test_e2e_standalone.py'],
        'monitoring-system': ['tests/test_monitoring_standalone.py'],
        'bubble-frontend-mock': ['tests/test_bubble_standalone.py'],
        'contract-testing': ['tests/test_contract_standalone.py']
    }
    
    results = {}
    
    for component, test_files in components.items():
        if os.path.exists(component):
            success = run_component_tests(component, test_files)
            results[component] = success
        else:
            print(f"⚠️ Component {component} not found, skipping...")
            results[component] = False
    
    # Return to original directory
    os.chdir(original_dir)
    
    # Print summary
    print("\n📊 Test Results Summary")
    print("=" * 50)
    
    total_components = len(results)
    successful_components = sum(1 for success in results.values() if success)
    
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{component:25} {status}")
    
    print(f"\n🎯 Overall: {successful_components}/{total_components} components passed")
    
    if successful_components == total_components:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️ Some tests failed or were skipped")
        return 1

if __name__ == "__main__":
    exit(main())
