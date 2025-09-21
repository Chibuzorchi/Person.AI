#!/usr/bin/env python3
"""
CI Test Runner - Runs tests in CI-friendly way
Handles Docker services and fallbacks gracefully
"""
import os
import sys
import subprocess
import time
import requests
from pathlib import Path

def run_command(cmd, cwd=None, timeout=300):
    """Run a command and return success status"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd, 
            timeout=timeout,
            capture_output=True, 
            text=True
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)

def check_service_health(url, timeout=10):
    """Check if a service is healthy"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def test_component(component_name):
    """Test a single component"""
    print(f"\n🧪 Testing {component_name}")
    print("=" * 50)
    
    component_path = Path(component_name)
    if not component_path.exists():
        print(f"❌ Component {component_name} not found")
        return False
    
    # Check if Docker Compose is available
    docker_available, _, _ = run_command("docker-compose --version")
    
    if docker_available and (component_path / "docker-compose.yml").exists():
        print(f"🐳 Testing {component_name} with Docker...")
        
        # Start Docker services
        success, stdout, stderr = run_command("docker-compose up -d", cwd=component_path)
        if not success:
            print(f"❌ Failed to start Docker services: {stderr}")
            return False
        
        # Wait for services to be ready
        print("⏳ Waiting for services to be ready...")
        time.sleep(30)
        
        # Check service health
        if component_name == "test-data-seeding":
            if not check_service_health("http://localhost:5002/health"):
                print("⚠️  QuickBooks service not healthy, running standalone tests")
                success, stdout, stderr = run_command(
                    "python3 -m pytest tests/test_api_mocks_standalone.py tests/test_data_generation.py -v",
                    cwd=component_path
                )
            else:
                success, stdout, stderr = run_command(
                    "python3 -m pytest tests/ -v",
                    cwd=component_path
                )
        else:
            success, stdout, stderr = run_command(
                "python3 -m pytest tests/ -v",
                cwd=component_path
            )
        
        # Stop Docker services
        run_command("docker-compose down", cwd=component_path)
        
    else:
        print(f"🐍 Testing {component_name} without Docker...")
        
        # Install dependencies
        if (component_path / "requirements.txt").exists():
            run_command("pip install -r requirements.txt", cwd=component_path)
        
        # Run tests
        if component_name == "test-data-seeding":
            success, stdout, stderr = run_command(
                "python3 -m pytest tests/test_api_mocks_standalone.py tests/test_data_generation.py -v",
                cwd=component_path
            )
        else:
            success, stdout, stderr = run_command(
                "python3 -m pytest tests/ -v",
                cwd=component_path
            )
    
    if success:
        print(f"✅ {component_name} tests passed")
        print(stdout)
    else:
        print(f"❌ {component_name} tests failed")
        print(f"STDOUT: {stdout}")
        print(f"STDERR: {stderr}")
    
    return success

def main():
    """Main test runner"""
    print("🚀 CI Test Runner")
    print("=" * 50)
    
    # Components to test
    components = [
        "slack-mock",
        "test-data-seeding", 
        "e2e-testing",
        "monitoring-system",
        "bubble-frontend-mock",
        "contract-testing"
    ]
    
    results = {}
    
    for component in components:
        results[component] = test_component(component)
    
    # Summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for component, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{component}: {status}")
    
    print(f"\nOverall: {passed}/{total} components passed")
    
    if passed == total:
        print("🎉 All tests passed!")
        sys.exit(0)
    else:
        print("💥 Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
