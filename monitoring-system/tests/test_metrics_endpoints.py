import pytest
import requests
import re
import time
from typing import List, Dict, Any

class TestMetricsEndpoints:
    """Test suite for metrics endpoints across all services"""
    
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def required_metrics(self):
        return {
            'http_requests_total': 'counter',
            'http_request_duration_seconds_bucket': 'histogram',
            'process_memory_usage_bytes': 'gauge',
            'process_cpu_seconds_total': 'counter',
            'service_uptime_seconds': 'gauge'
        }
    
    def test_metrics_endpoint_availability(self, services_config):
        """Test metrics endpoint availability"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/metrics", timeout=10)
            
            assert response.status_code == 200, f"Service {service_name} metrics endpoint failed with status {response.status_code}"
            assert response.headers['Content-Type'] == 'text/plain; charset=utf-8', f"Service {service_name} metrics should return text/plain"
    
    def test_metrics_format_validation(self, services_config):
        """Test metrics format validation"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/metrics", timeout=10)
            metrics_text = response.text
            
            # Split into lines and validate format
            lines = metrics_text.strip().split('\n')
            metric_lines = [line for line in lines if line and not line.startswith('#')]
            
            for line in metric_lines:
                # Basic Prometheus metric format validation
                pattern = r'^[a-zA-Z_:][a-zA-Z0-9_:]*(\{[^}]*\})?\s+[0-9]+(\.[0-9]+)?$'
                assert re.match(pattern, line), f"Service {service_name} invalid metric line format: {line}"
    
    def test_required_metrics_present(self, services_config, required_metrics):
        """Test that all required metrics are present"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/metrics", timeout=10)
            metrics_text = response.text
            
            # Extract metric names
            metric_names = set()
            for line in metrics_text.split('\n'):
                if line and not line.startswith('#') and ' ' in line:
                    metric_name = line.split(' ')[0].split('{')[0]
                    metric_names.add(metric_name)
            
            # Check that all required metrics are present
            for metric_name in required_metrics.keys():
                assert metric_name in metric_names, f"Service {service_name} missing required metric: {metric_name}"
    
    def test_metrics_values_reasonable(self, services_config):
        """Test that metric values are reasonable"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/metrics", timeout=10)
            metrics_text = response.text
            
            # Parse and validate specific metrics
            for line in metrics_text.split('\n'):
                if line and not line.startswith('#') and ' ' in line:
                    parts = line.split(' ')
                    if len(parts) >= 2:
                        metric_name = parts[0].split('{')[0]
                        try:
                            value = float(parts[-1])
                            
                            # Validate specific metrics
                            if metric_name == 'process_memory_usage_bytes':
                                assert value > 0, f"Service {service_name} memory usage should be positive"
                                assert value < 10 * 1024 * 1024 * 1024, f"Service {service_name} memory usage too high: {value}"
                            elif metric_name == 'http_requests_total':
                                assert value >= 0, f"Service {service_name} request count should be non-negative"
                            elif metric_name == 'service_uptime_seconds':
                                assert value >= 0, f"Service {service_name} uptime should be non-negative"
                        except ValueError:
                            # Skip lines that don't have numeric values
                            pass
    
    def test_metrics_response_time(self, services_config):
        """Test metrics endpoint response times"""
        for service_name, base_url in services_config.items():
            import time
            start_time = time.time()
            response = requests.get(f"{base_url}/metrics", timeout=10)
            response_time = time.time() - start_time
            
            assert response_time < 5.0, f"Service {service_name} metrics endpoint too slow: {response_time:.2f}s"
    
    def test_metrics_histogram_buckets(self, services_config):
        """Test that histogram metrics have proper bucket structure"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/metrics", timeout=10)
            metrics_text = response.text
            
            # Check for histogram buckets
            histogram_metrics = {}
            for line in metrics_text.split('\n'):
                if '_bucket' in line and 'le=' in line:
                    metric_name = line.split('_bucket')[0]
                    if metric_name not in histogram_metrics:
                        histogram_metrics[metric_name] = []
                    histogram_metrics[metric_name].append(line)
            
            # Validate histogram structure
            for metric_name, bucket_lines in histogram_metrics.items():
                assert len(bucket_lines) > 1, f"Service {service_name} histogram {metric_name} should have multiple buckets"
                
                # Check for +Inf bucket
                inf_bucket = any('le="+Inf"' in line for line in bucket_lines)
                assert inf_bucket, f"Service {service_name} histogram {metric_name} missing +Inf bucket"
    
    def test_metrics_counter_monotonicity(self, services_config):
        """Test that counter metrics are non-decreasing"""
        for service_name, base_url in services_config.items():
            # Get metrics twice to check monotonicity
            response1 = requests.get(f"{base_url}/metrics", timeout=10)
            time.sleep(1)
            response2 = requests.get(f"{base_url}/metrics", timeout=10)
            
            # Parse counter values
            counters1 = self._parse_counters(response1.text)
            counters2 = self._parse_counters(response2.text)
            
            # Check that counters are non-decreasing
            for metric_name in counters1:
                if metric_name in counters2:
                    assert counters2[metric_name] >= counters1[metric_name], f"Service {service_name} counter {metric_name} decreased"
    
    def _parse_counters(self, metrics_text: str) -> Dict[str, float]:
        """Parse counter metrics from Prometheus format"""
        counters = {}
        for line in metrics_text.split('\n'):
            if line and not line.startswith('#') and ' ' in line and '_total' in line:
                parts = line.split(' ')
                if len(parts) >= 2:
                    metric_name = parts[0].split('{')[0]
                    try:
                        value = float(parts[-1])
                        counters[metric_name] = value
                    except ValueError:
                        pass
        return counters
