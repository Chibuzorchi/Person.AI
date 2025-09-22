import pytest
import requests
import time
from typing import Dict, Any

# Mark as Tier 3 Secondary and Integration
pytestmark = [pytest.mark.tier3_secondary, pytest.mark.integration]

class TestHealthEndpoints:
    """Test suite for health endpoints across all services"""
    
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    def test_all_services_healthy(self, services_config):
        """Test that all services are healthy"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/health", timeout=10)
            
            assert response.status_code in [200, 503], f"Service {service_name} health check failed with status {response.status_code}"
            
            health_data = response.json()
            assert 'status' in health_data, f"Service {service_name} missing status field"
            assert 'uptime' in health_data, f"Service {service_name} missing uptime field"
            assert 'version' in health_data, f"Service {service_name} missing version field"
            assert 'timestamp' in health_data, f"Service {service_name} missing timestamp field"
    
    def test_health_response_structure(self, services_config):
        """Test health response structure validation"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/health", timeout=10)
            health_data = response.json()
            
            # Validate required fields
            required_fields = ['status', 'service', 'version', 'uptime', 'timestamp', 'dependencies', 'system']
            for field in required_fields:
                assert field in health_data, f"Service {service_name} missing required field: {field}"
            
            # Validate field types
            assert isinstance(health_data['uptime'], (int, float)), f"Service {service_name} uptime should be numeric"
            assert isinstance(health_data['version'], str), f"Service {service_name} version should be string"
            assert health_data['status'] in ['healthy', 'unhealthy', 'degraded'], f"Service {service_name} invalid status"
            
            # Validate dependencies structure
            dependencies = health_data['dependencies']
            assert isinstance(dependencies, dict), f"Service {service_name} dependencies should be dict"
            
            # Validate system metrics
            system = health_data['system']
            assert 'memory_usage_percent' in system, f"Service {service_name} missing memory usage"
            assert 'cpu_usage_percent' in system, f"Service {service_name} missing CPU usage"
            assert 'disk_usage_percent' in system, f"Service {service_name} missing disk usage"
    
    def test_health_response_time(self, services_config):
        """Test health endpoint response times"""
        for service_name, base_url in services_config.items():
            start_time = time.time()
            response = requests.get(f"{base_url}/health", timeout=10)
            response_time = time.time() - start_time
            
            assert response_time < 2.0, f"Service {service_name} health check too slow: {response_time:.2f}s"
    
    def test_health_endpoint_availability(self, services_config):
        """Test health endpoint availability"""
        for service_name, base_url in services_config.items():
            try:
                response = requests.get(f"{base_url}/health", timeout=10)
                assert response.status_code in [200, 503], f"Service {service_name} health endpoint not available"
            except requests.exceptions.RequestException as e:
                pytest.fail(f"Service {service_name} health endpoint not accessible: {e}")
    
    def test_health_dependencies_check(self, services_config):
        """Test that health endpoints include dependency checks"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/health", timeout=10)
            health_data = response.json()
            
            dependencies = health_data['dependencies']
            assert len(dependencies) > 0, f"Service {service_name} should have dependencies"
            
            # Check that dependencies have boolean values
            for dep_name, dep_status in dependencies.items():
                assert isinstance(dep_status, bool), f"Service {service_name} dependency {dep_name} should be boolean"
    
    def test_health_system_metrics(self, services_config):
        """Test that health endpoints include system metrics"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/health", timeout=10)
            health_data = response.json()
            
            system = health_data['system']
            
            # Validate memory usage
            memory_usage = system['memory_usage_percent']
            assert 0 <= memory_usage <= 100, f"Service {service_name} memory usage should be 0-100%"
            
            # Validate CPU usage
            cpu_usage = system['cpu_usage_percent']
            assert 0 <= cpu_usage <= 100, f"Service {service_name} CPU usage should be 0-100%"
            
            # Validate disk usage
            disk_usage = system['disk_usage_percent']
            assert 0 <= disk_usage <= 100, f"Service {service_name} disk usage should be 0-100%"
