#!/usr/bin/env python3
"""
Comprehensive monitoring system test runner
Tests health, metrics, and audit endpoints across all Person.ai services
"""

import requests
import time
import json
from datetime import datetime
from typing import Dict, List, Any

class MonitoringTestRunner:
    def __init__(self, services_config: Dict[str, str]):
        self.services = services_config
        self.results = {
            'health': {},
            'metrics': {},
            'audit': {},
            'overall_success': True,
            'test_duration': 0,
            'timestamp': datetime.now().isoformat()
        }
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all monitoring tests"""
        start_time = time.time()
        
        print("🚀 Person.ai Monitoring System Test Runner")
        print("=" * 50)
        
        # Test health endpoints
        print("\n🔍 Testing Health Endpoints...")
        self._test_health_endpoints()
        
        # Test metrics endpoints
        print("\n📊 Testing Metrics Endpoints...")
        self._test_metrics_endpoints()
        
        # Test audit endpoints
        print("\n📝 Testing Audit Endpoints...")
        self._test_audit_endpoints()
        
        # Calculate overall results
        self.results['test_duration'] = time.time() - start_time
        self.results['overall_success'] = all(
            all(service_result.get('success', False) for service_result in category_results.values())
            for category_results in [self.results['health'], self.results['metrics'], self.results['audit']]
        )
        
        # Print summary
        self._print_summary()
        
        return self.results
    
    def _test_health_endpoints(self):
        """Test health endpoints for all services"""
        for service_name, base_url in self.services.items():
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/health", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code in [200, 503]:
                    health_data = response.json()
                    success = self._validate_health_response(health_data, service_name)
                    
                    self.results['health'][service_name] = {
                        'success': success,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'status': health_data.get('status', 'unknown'),
                        'uptime': health_data.get('uptime', 0),
                        'dependencies': health_data.get('dependencies', {}),
                        'error': None
                    }
                    
                    status_icon = "✅" if success else "❌"
                    print(f"  {status_icon} {service_name}: {health_data.get('status', 'unknown')} ({response_time:.2f}s)")
                else:
                    self.results['health'][service_name] = {
                        'success': False,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'error': f"HTTP {response.status_code}"
                    }
                    print(f"  ❌ {service_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                self.results['health'][service_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {service_name}: {str(e)}")
    
    def _test_metrics_endpoints(self):
        """Test metrics endpoints for all services"""
        for service_name, base_url in self.services.items():
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/metrics", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    metrics_text = response.text
                    success = self._validate_metrics_response(metrics_text, service_name)
                    
                    self.results['metrics'][service_name] = {
                        'success': success,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'metrics_count': len([line for line in metrics_text.split('\n') if line and not line.startswith('#')]),
                        'error': None
                    }
                    
                    status_icon = "✅" if success else "❌"
                    print(f"  {status_icon} {service_name}: {self.results['metrics'][service_name]['metrics_count']} metrics ({response_time:.2f}s)")
                else:
                    self.results['metrics'][service_name] = {
                        'success': False,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'error': f"HTTP {response.status_code}"
                    }
                    print(f"  ❌ {service_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                self.results['metrics'][service_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {service_name}: {str(e)}")
    
    def _test_audit_endpoints(self):
        """Test audit endpoints for all services"""
        for service_name, base_url in self.services.items():
            try:
                start_time = time.time()
                response = requests.get(f"{base_url}/audit", timeout=10)
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    audit_data = response.json()
                    success = self._validate_audit_response(audit_data, service_name)
                    
                    self.results['audit'][service_name] = {
                        'success': success,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'total_events': audit_data.get('total_events', 0),
                        'returned_events': audit_data.get('returned_events', 0),
                        'error': None
                    }
                    
                    status_icon = "✅" if success else "❌"
                    print(f"  {status_icon} {service_name}: {audit_data.get('total_events', 0)} events ({response_time:.2f}s)")
                else:
                    self.results['audit'][service_name] = {
                        'success': False,
                        'status_code': response.status_code,
                        'response_time': response_time,
                        'error': f"HTTP {response.status_code}"
                    }
                    print(f"  ❌ {service_name}: HTTP {response.status_code} ({response_time:.2f}s)")
                    
            except Exception as e:
                self.results['audit'][service_name] = {
                    'success': False,
                    'error': str(e)
                }
                print(f"  ❌ {service_name}: {str(e)}")
    
    def _validate_health_response(self, health_data: Dict[str, Any], service_name: str) -> bool:
        """Validate health response structure"""
        try:
            required_fields = ['status', 'service', 'version', 'uptime', 'timestamp', 'dependencies', 'system']
            for field in required_fields:
                if field not in health_data:
                    return False
            
            # Validate field types
            if not isinstance(health_data['uptime'], (int, float)):
                return False
            if not isinstance(health_data['version'], str):
                return False
            if health_data['status'] not in ['healthy', 'unhealthy', 'degraded']:
                return False
            
            return True
        except Exception:
            return False
    
    def _validate_metrics_response(self, metrics_text: str, service_name: str) -> bool:
        """Validate metrics response format"""
        try:
            lines = metrics_text.strip().split('\n')
            metric_lines = [line for line in lines if line and not line.startswith('#')]
            
            if len(metric_lines) == 0:
                return False
            
            # Check for required metrics
            required_metrics = ['http_requests_total', 'service_uptime_seconds']
            metric_names = set()
            for line in metric_lines:
                if ' ' in line:
                    metric_name = line.split(' ')[0].split('{')[0]
                    metric_names.add(metric_name)
            
            for required_metric in required_metrics:
                if required_metric not in metric_names:
                    return False
            
            return True
        except Exception:
            return False
    
    def _validate_audit_response(self, audit_data: Dict[str, Any], service_name: str) -> bool:
        """Validate audit response structure"""
        try:
            required_fields = ['service', 'total_events', 'returned_events', 'events']
            for field in required_fields:
                if field not in audit_data:
                    return False
            
            if not isinstance(audit_data['events'], list):
                return False
            
            return True
        except Exception:
            return False
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 50)
        print("📊 Monitoring Test Summary")
        print("=" * 50)
        
        # Health summary
        health_success = sum(1 for result in self.results['health'].values() if result.get('success', False))
        health_total = len(self.results['health'])
        print(f"Health Endpoints: {health_success}/{health_total} services")
        
        # Metrics summary
        metrics_success = sum(1 for result in self.results['metrics'].values() if result.get('success', False))
        metrics_total = len(self.results['metrics'])
        print(f"Metrics Endpoints: {metrics_success}/{metrics_total} services")
        
        # Audit summary
        audit_success = sum(1 for result in self.results['audit'].values() if result.get('success', False))
        audit_total = len(self.results['audit'])
        print(f"Audit Endpoints: {audit_success}/{audit_total} services")
        
        # Overall result
        overall_icon = "✅" if self.results['overall_success'] else "❌"
        print(f"\nOverall Result: {overall_icon} {'PASS' if self.results['overall_success'] else 'FAIL'}")
        print(f"Test Duration: {self.results['test_duration']:.2f} seconds")
        
        # Save results to file
        self._save_results()
    
    def _save_results(self):
        """Save test results to file"""
        try:
            with open('/app/output/monitoring_test_results.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            print(f"\n📝 Results saved to: /app/output/monitoring_test_results.json")
        except Exception as e:
            print(f"\n⚠️  Could not save results: {e}")

def main():
    """Main function"""
    services_config = {
        'integration-controller': 'http://localhost:8001',
        'content-engine': 'http://localhost:8002',
        'media-engine': 'http://localhost:8003',
        'delivery-gateway': 'http://localhost:8004'
    }
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    for service_name, base_url in services_config.items():
        max_retries = 30
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{base_url}/health", timeout=5)
                if response.status_code in [200, 503]:
                    print(f"✅ {service_name} is ready")
                    break
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"❌ {service_name} not ready after {max_retries * 2} seconds")
                    return False
    
    # Run tests
    runner = MonitoringTestRunner(services_config)
    results = runner.run_all_tests()
    
    return results['overall_success']

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
