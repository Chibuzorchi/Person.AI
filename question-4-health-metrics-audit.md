# Question 4: Health/Metrics/Audit Endpoint Verification

## Question
"Our services must expose /health, /metrics, and /audit endpoints. What would you verify at each endpoint during QA, and how would you automate those checks to catch failures in CI/CD?"

## Comprehensive Answer

### Architecture Overview
I would design a comprehensive monitoring and testing framework that validates health, metrics, and audit endpoints across all Person.ai services, ensuring system reliability and observability.

### Health Endpoint Testing

#### 1. **Health Check Framework**
```python
# health_check_framework.py
import requests
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import aiohttp

class HealthStatus(Enum):
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"

@dataclass
class HealthCheckResult:
    service_name: str
    status: HealthStatus
    response_time: float
    timestamp: str
    details: Dict[str, Any]
    error: Optional[str] = None

class HealthCheckFramework:
    def __init__(self, services_config: Dict[str, str]):
        self.services = services_config
        self.health_checks = {
            'basic': self._basic_health_check,
            'database': self._database_health_check,
            'external_dependencies': self._external_dependencies_check,
            'memory': self._memory_health_check,
            'disk': self._disk_health_check
        }
    
    async def check_service_health(self, service_name: str) -> HealthCheckResult:
        """Perform comprehensive health check for a service"""
        start_time = time.time()
        
        try:
            # Basic connectivity check
            response = await self._make_request(f"{self.services[service_name]}/health")
            
            if response.status == 200:
                health_data = await response.json()
                
                # Validate health response structure
                if self._validate_health_response(health_data):
                    response_time = time.time() - start_time
                    
                    # Perform additional checks
                    additional_checks = await self._perform_additional_checks(service_name, health_data)
                    
                    return HealthCheckResult(
                        service_name=service_name,
                        status=HealthStatus.HEALTHY,
                        response_time=response_time,
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        details={
                            'basic_health': health_data,
                            'additional_checks': additional_checks
                        }
                    )
                else:
                    return HealthCheckResult(
                        service_name=service_name,
                        status=HealthStatus.UNHEALTHY,
                        response_time=time.time() - start_time,
                        timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                        details={},
                        error="Invalid health response structure"
                    )
            else:
                return HealthCheckResult(
                    service_name=service_name,
                    status=HealthStatus.UNHEALTHY,
                    response_time=time.time() - start_time,
                    timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                    details={},
                    error=f"HTTP {response.status}"
                )
                
        except Exception as e:
            return HealthCheckResult(
                service_name=service_name,
                status=HealthStatus.UNHEALTHY,
                response_time=time.time() - start_time,
                timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
                details={},
                error=str(e)
            )
    
    async def _make_request(self, url: str) -> aiohttp.ClientResponse:
        """Make HTTP request with timeout"""
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            return await session.get(url)
    
    def _validate_health_response(self, health_data: Dict[str, Any]) -> bool:
        """Validate health response structure"""
        required_fields = ['status', 'uptime', 'version', 'timestamp']
        
        for field in required_fields:
            if field not in health_data:
                return False
        
        # Validate status values
        valid_statuses = ['healthy', 'unhealthy', 'degraded']
        if health_data['status'] not in valid_statuses:
            return False
        
        # Validate uptime is numeric
        if not isinstance(health_data['uptime'], (int, float)):
            return False
        
        return True
    
    async def _perform_additional_checks(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform additional health checks"""
        additional_checks = {}
        
        for check_name, check_func in self.health_checks.items():
            try:
                result = await check_func(service_name, health_data)
                additional_checks[check_name] = result
            except Exception as e:
                additional_checks[check_name] = {'error': str(e)}
        
        return additional_checks
    
    async def _basic_health_check(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic health check validation"""
        return {
            'status': health_data['status'],
            'uptime_seconds': health_data['uptime'],
            'version': health_data['version'],
            'timestamp': health_data['timestamp']
        }
    
    async def _database_health_check(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Database connectivity check"""
        # This would check database connectivity
        return {
            'database_connected': True,
            'connection_pool_size': 10,
            'active_connections': 5
        }
    
    async def _external_dependencies_check(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Check external dependencies"""
        dependencies = {
            'gmail_api': True,
            'slack_api': True,
            'elevenlabs_api': True,
            'quickbooks_api': True,
            'salesforce_api': True
        }
        
        return {
            'dependencies': dependencies,
            'all_healthy': all(dependencies.values())
        }
    
    async def _memory_health_check(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Memory usage check"""
        return {
            'memory_usage_percent': 65.5,
            'memory_available_mb': 2048,
            'memory_threshold_exceeded': False
        }
    
    async def _disk_health_check(self, service_name: str, health_data: Dict[str, Any]) -> Dict[str, Any]:
        """Disk usage check"""
        return {
            'disk_usage_percent': 45.2,
            'disk_available_gb': 50.5,
            'disk_threshold_exceeded': False
        }
```

#### 2. **Health Endpoint Test Suite**
```python
# health_endpoint_tests.py
import pytest
import asyncio
from health_check_framework import HealthCheckFramework, HealthStatus

class TestHealthEndpoints:
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def health_framework(self, services_config):
        return HealthCheckFramework(services_config)
    
    @pytest.mark.asyncio
    async def test_all_services_healthy(self, health_framework):
        """Test that all services are healthy"""
        results = []
        
        for service_name in health_framework.services.keys():
            result = await health_framework.check_service_health(service_name)
            results.append(result)
        
        # Assert all services are healthy
        for result in results:
            assert result.status == HealthStatus.HEALTHY, f"Service {result.service_name} is not healthy: {result.error}"
            assert result.response_time < 5.0, f"Service {result.service_name} response time too slow: {result.response_time}s"
    
    @pytest.mark.asyncio
    async def test_health_response_structure(self, health_framework):
        """Test health response structure validation"""
        for service_name in health_framework.services.keys():
            result = await health_framework.check_service_health(service_name)
            
            if result.status == HealthStatus.HEALTHY:
                health_data = result.details['basic_health']
                
                # Validate required fields
                assert 'status' in health_data
                assert 'uptime' in health_data
                assert 'version' in health_data
                assert 'timestamp' in health_data
                
                # Validate field types
                assert isinstance(health_data['uptime'], (int, float))
                assert isinstance(health_data['version'], str)
                assert health_data['status'] in ['healthy', 'unhealthy', 'degraded']
    
    @pytest.mark.asyncio
    async def test_health_response_time(self, health_framework):
        """Test health endpoint response times"""
        for service_name in health_framework.services.keys():
            result = await health_framework.check_service_health(service_name)
            
            assert result.response_time < 2.0, f"Service {result.service_name} health check too slow: {result.response_time}s"
    
    @pytest.mark.asyncio
    async def test_health_endpoint_availability(self, health_framework):
        """Test health endpoint availability"""
        for service_name in health_framework.services.keys():
            result = await health_framework.check_service_health(service_name)
            
            assert result.status != HealthStatus.UNKNOWN, f"Service {result.service_name} health endpoint not available"
```

### Metrics Endpoint Testing

#### 1. **Metrics Validation Framework**
```python
# metrics_validation_framework.py
import requests
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import time

@dataclass
class MetricValidationResult:
    metric_name: str
    is_valid: bool
    value: Optional[float] = None
    error: Optional[str] = None

class MetricsValidationFramework:
    def __init__(self, services_config: Dict[str, str]):
        self.services = services_config
        self.required_metrics = {
            'http_requests_total': 'counter',
            'http_request_duration_seconds': 'histogram',
            'process_cpu_seconds_total': 'counter',
            'process_memory_usage_bytes': 'gauge',
            'go_memstats_alloc_bytes': 'gauge',
            'go_memstats_gc_duration_seconds': 'histogram'
        }
    
    async def validate_metrics_endpoint(self, service_name: str) -> List[MetricValidationResult]:
        """Validate metrics endpoint for a service"""
        results = []
        
        try:
            response = requests.get(f"{self.services[service_name]}/metrics", timeout=10)
            
            if response.status_code == 200:
                metrics_text = response.text
                results = self._parse_and_validate_metrics(metrics_text)
            else:
                results.append(MetricValidationResult(
                    metric_name="metrics_endpoint",
                    is_valid=False,
                    error=f"HTTP {response.status_code}"
                ))
                
        except Exception as e:
            results.append(MetricValidationResult(
                metric_name="metrics_endpoint",
                is_valid=False,
                error=str(e)
            ))
        
        return results
    
    def _parse_and_validate_metrics(self, metrics_text: str) -> List[MetricValidationResult]:
        """Parse and validate Prometheus metrics"""
        results = []
        lines = metrics_text.strip().split('\n')
        
        # Skip comments and empty lines
        metric_lines = [line for line in lines if line and not line.startswith('#')]
        
        # Group metrics by name
        metrics_by_name = {}
        for line in metric_lines:
            if ' ' in line:
                metric_name = line.split(' ')[0].split('{')[0]
                if metric_name not in metrics_by_name:
                    metrics_by_name[metric_name] = []
                metrics_by_name[metric_name].append(line)
        
        # Validate each required metric
        for metric_name, metric_type in self.required_metrics.items():
            if metric_name in metrics_by_name:
                validation_result = self._validate_metric(metric_name, metric_type, metrics_by_name[metric_name])
                results.append(validation_result)
            else:
                results.append(MetricValidationResult(
                    metric_name=metric_name,
                    is_valid=False,
                    error="Metric not found"
                ))
        
        return results
    
    def _validate_metric(self, metric_name: str, metric_type: str, metric_lines: List[str]) -> MetricValidationResult:
        """Validate a specific metric"""
        try:
            # Check metric format
            for line in metric_lines:
                if not self._is_valid_metric_line(line):
                    return MetricValidationResult(
                        metric_name=metric_name,
                        is_valid=False,
                        error=f"Invalid metric line format: {line}"
                    )
            
            # Extract values
            values = []
            for line in metric_lines:
                value = self._extract_metric_value(line)
                if value is not None:
                    values.append(value)
            
            if not values:
                return MetricValidationResult(
                    metric_name=metric_name,
                    is_valid=False,
                    error="No valid values found"
                )
            
            # Validate metric type specific rules
            if metric_type == 'counter':
                if not self._validate_counter_metric(values):
                    return MetricValidationResult(
                        metric_name=metric_name,
                        is_valid=False,
                        error="Counter metric validation failed"
                    )
            elif metric_type == 'gauge':
                if not self._validate_gauge_metric(values):
                    return MetricValidationResult(
                        metric_name=metric_name,
                        is_valid=False,
                        error="Gauge metric validation failed"
                    )
            elif metric_type == 'histogram':
                if not self._validate_histogram_metric(values):
                    return MetricValidationResult(
                        metric_name=metric_name,
                        is_valid=False,
                        error="Histogram metric validation failed"
                    )
            
            return MetricValidationResult(
                metric_name=metric_name,
                is_valid=True,
                value=sum(values)
            )
            
        except Exception as e:
            return MetricValidationResult(
                metric_name=metric_name,
                is_valid=False,
                error=str(e)
            )
    
    def _is_valid_metric_line(self, line: str) -> bool:
        """Check if metric line has valid format"""
        # Basic Prometheus metric format validation
        pattern = r'^[a-zA-Z_:][a-zA-Z0-9_:]*(\{[^}]*\})?\s+[0-9]+(\.[0-9]+)?$'
        return bool(re.match(pattern, line))
    
    def _extract_metric_value(self, line: str) -> Optional[float]:
        """Extract numeric value from metric line"""
        try:
            parts = line.split(' ')
            if len(parts) >= 2:
                return float(parts[-1])
        except ValueError:
            pass
        return None
    
    def _validate_counter_metric(self, values: List[float]) -> bool:
        """Validate counter metric (should be non-decreasing)"""
        return all(values[i] >= values[i-1] for i in range(1, len(values)))
    
    def _validate_gauge_metric(self, values: List[float]) -> bool:
        """Validate gauge metric (can increase or decrease)"""
        return all(isinstance(v, (int, float)) for v in values)
    
    def _validate_histogram_metric(self, values: List[float]) -> bool:
        """Validate histogram metric (should have multiple buckets)"""
        return len(values) > 1  # Histograms typically have multiple buckets
```

#### 2. **Metrics Endpoint Test Suite**
```python
# metrics_endpoint_tests.py
import pytest
from metrics_validation_framework import MetricsValidationFramework

class TestMetricsEndpoints:
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def metrics_framework(self, services_config):
        return MetricsValidationFramework(services_config)
    
    @pytest.mark.asyncio
    async def test_metrics_endpoint_availability(self, metrics_framework):
        """Test metrics endpoint availability"""
        for service_name in metrics_framework.services.keys():
            results = await metrics_framework.validate_metrics_endpoint(service_name)
            
            # Check if metrics endpoint is accessible
            endpoint_result = next((r for r in results if r.metric_name == "metrics_endpoint"), None)
            assert endpoint_result is not None, f"Metrics endpoint not accessible for {service_name}"
            assert endpoint_result.is_valid, f"Metrics endpoint error for {service_name}: {endpoint_result.error}"
    
    @pytest.mark.asyncio
    async def test_required_metrics_present(self, metrics_framework):
        """Test that all required metrics are present"""
        for service_name in metrics_framework.services.keys():
            results = await metrics_framework.validate_metrics_endpoint(service_name)
            
            # Check that all required metrics are present and valid
            for metric_name in metrics_framework.required_metrics.keys():
                metric_result = next((r for r in results if r.metric_name == metric_name), None)
                assert metric_result is not None, f"Required metric {metric_name} not found in {service_name}"
                assert metric_result.is_valid, f"Metric {metric_name} validation failed in {service_name}: {metric_result.error}"
    
    @pytest.mark.asyncio
    async def test_metrics_format_validation(self, metrics_framework):
        """Test metrics format validation"""
        for service_name in metrics_framework.services.keys():
            results = await metrics_framework.validate_metrics_endpoint(service_name)
            
            # All metrics should be valid
            for result in results:
                if result.metric_name != "metrics_endpoint":
                    assert result.is_valid, f"Metric {result.metric_name} format invalid in {service_name}: {result.error}"
    
    @pytest.mark.asyncio
    async def test_metrics_values_reasonable(self, metrics_framework):
        """Test that metric values are reasonable"""
        for service_name in metrics_framework.services.keys():
            results = await metrics_framework.validate_metrics_endpoint(service_name)
            
            for result in results:
                if result.is_valid and result.value is not None:
                    # Check for reasonable values
                    if result.metric_name == 'process_memory_usage_bytes':
                        assert result.value > 0, f"Memory usage should be positive in {service_name}"
                        assert result.value < 10 * 1024 * 1024 * 1024, f"Memory usage too high in {service_name}: {result.value}"
                    elif result.metric_name == 'http_requests_total':
                        assert result.value >= 0, f"Request count should be non-negative in {service_name}"
```

### Audit Endpoint Testing

#### 1. **Audit Validation Framework**
```python
# audit_validation_framework.py
import requests
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import time

@dataclass
class AuditEvent:
    timestamp: str
    event_type: str
    user_id: str
    resource_id: str
    action: str
    details: Dict[str, Any]
    success: bool

class AuditValidationFramework:
    def __init__(self, services_config: Dict[str, str]):
        self.services = services_config
        self.required_events = [
            'user_login',
            'brief_created',
            'brief_delivered',
            'integration_connected',
            'integration_disconnected',
            'error_occurred'
        ]
    
    async def validate_audit_endpoint(self, service_name: str) -> Dict[str, Any]:
        """Validate audit endpoint for a service"""
        try:
            response = requests.get(f"{self.services[service_name]}/audit", timeout=10)
            
            if response.status_code == 200:
                audit_data = response.json()
                return self._validate_audit_data(audit_data, service_name)
            else:
                return {
                    'is_valid': False,
                    'error': f"HTTP {response.status_code}",
                    'service': service_name
                }
                
        except Exception as e:
            return {
                'is_valid': False,
                'error': str(e),
                'service': service_name
            }
    
    def _validate_audit_data(self, audit_data: Dict[str, Any], service_name: str) -> Dict[str, Any]:
        """Validate audit data structure and content"""
        validation_result = {
            'is_valid': True,
            'service': service_name,
            'events_count': 0,
            'validation_errors': [],
            'coverage': {}
        }
        
        # Validate structure
        if 'events' not in audit_data:
            validation_result['is_valid'] = False
            validation_result['validation_errors'].append("Missing 'events' field")
            return validation_result
        
        events = audit_data['events']
        validation_result['events_count'] = len(events)
        
        # Validate each event
        for i, event in enumerate(events):
            event_validation = self._validate_audit_event(event, i)
            if not event_validation['is_valid']:
                validation_result['validation_errors'].extend(event_validation['errors'])
        
        # Check event coverage
        validation_result['coverage'] = self._check_event_coverage(events)
        
        # Overall validation
        if validation_result['validation_errors']:
            validation_result['is_valid'] = False
        
        return validation_result
    
    def _validate_audit_event(self, event: Dict[str, Any], index: int) -> Dict[str, Any]:
        """Validate individual audit event"""
        validation_result = {
            'is_valid': True,
            'errors': []
        }
        
        required_fields = ['timestamp', 'event_type', 'user_id', 'action', 'success']
        
        for field in required_fields:
            if field not in event:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Event {index}: Missing required field '{field}'")
        
        # Validate timestamp format
        if 'timestamp' in event:
            try:
                datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Event {index}: Invalid timestamp format")
        
        # Validate event type
        if 'event_type' in event:
            if event['event_type'] not in self.required_events:
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Event {index}: Unknown event type '{event['event_type']}'")
        
        # Validate success field
        if 'success' in event:
            if not isinstance(event['success'], bool):
                validation_result['is_valid'] = False
                validation_result['errors'].append(f"Event {index}: 'success' field must be boolean")
        
        return validation_result
    
    def _check_event_coverage(self, events: List[Dict[str, Any]]) -> Dict[str, bool]:
        """Check coverage of required event types"""
        coverage = {}
        event_types = [event.get('event_type') for event in events]
        
        for required_event in self.required_events:
            coverage[required_event] = required_event in event_types
        
        return coverage
    
    async def trigger_audit_events(self, service_name: str) -> Dict[str, Any]:
        """Trigger events to generate audit logs"""
        try:
            # Trigger various events to generate audit logs
            events_triggered = []
            
            # Simulate user login
            login_response = requests.post(f"{self.services[service_name]}/api/auth/login", 
                                        json={"username": "test_user", "password": "test_pass"})
            if login_response.status_code in [200, 401]:  # 401 is expected for invalid credentials
                events_triggered.append("user_login")
            
            # Simulate brief creation
            brief_response = requests.post(f"{self.services[service_name]}/api/briefs", 
                                        json={"title": "Test Brief", "content": "Test Content"})
            if brief_response.status_code in [200, 201]:
                events_triggered.append("brief_created")
            
            # Simulate integration connection
            integration_response = requests.post(f"{self.services[service_name]}/api/integrations/connect", 
                                              json={"type": "slack", "config": {}})
            if integration_response.status_code in [200, 201]:
                events_triggered.append("integration_connected")
            
            return {
                'success': True,
                'events_triggered': events_triggered,
                'service': service_name
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'service': service_name
            }
```

#### 2. **Audit Endpoint Test Suite**
```python
# audit_endpoint_tests.py
import pytest
import time
from audit_validation_framework import AuditValidationFramework

class TestAuditEndpoints:
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def audit_framework(self, services_config):
        return AuditValidationFramework(services_config)
    
    @pytest.mark.asyncio
    async def test_audit_endpoint_availability(self, audit_framework):
        """Test audit endpoint availability"""
        for service_name in audit_framework.services.keys():
            result = await audit_framework.validate_audit_endpoint(service_name)
            
            assert result['is_valid'], f"Audit endpoint not available for {service_name}: {result.get('error')}"
    
    @pytest.mark.asyncio
    async def test_audit_data_structure(self, audit_framework):
        """Test audit data structure validation"""
        for service_name in audit_framework.services.keys():
            result = await audit_framework.validate_audit_endpoint(service_name)
            
            assert result['is_valid'], f"Audit data structure invalid for {service_name}: {result.get('validation_errors')}"
            assert result['events_count'] > 0, f"No audit events found for {service_name}"
    
    @pytest.mark.asyncio
    async def test_audit_event_validation(self, audit_framework):
        """Test individual audit event validation"""
        for service_name in audit_framework.services.keys():
            result = await audit_framework.validate_audit_endpoint(service_name)
            
            assert result['is_valid'], f"Audit event validation failed for {service_name}: {result.get('validation_errors')}"
    
    @pytest.mark.asyncio
    async def test_audit_event_coverage(self, audit_framework):
        """Test audit event coverage"""
        for service_name in audit_framework.services.keys():
            result = await audit_framework.validate_audit_endpoint(service_name)
            
            coverage = result.get('coverage', {})
            required_events = audit_framework.required_events
            
            for event_type in required_events:
                assert coverage.get(event_type, False), f"Required event type '{event_type}' not found in {service_name}"
    
    @pytest.mark.asyncio
    async def test_audit_event_generation(self, audit_framework):
        """Test audit event generation"""
        for service_name in audit_framework.services.keys():
            # Trigger events
            trigger_result = await audit_framework.trigger_audit_events(service_name)
            
            if trigger_result['success']:
                # Wait for events to be logged
                time.sleep(2)
                
                # Validate audit endpoint again
                result = await audit_framework.validate_audit_endpoint(service_name)
                
                assert result['is_valid'], f"Audit endpoint validation failed after triggering events for {service_name}"
                assert result['events_count'] > 0, f"No audit events found after triggering for {service_name}"
```

### CI/CD Integration

#### 1. **Complete Monitoring Test Suite**
```python
# complete_monitoring_tests.py
import pytest
import asyncio
from health_check_framework import HealthCheckFramework
from metrics_validation_framework import MetricsValidationFramework
from audit_validation_framework import AuditValidationFramework

class TestCompleteMonitoring:
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def monitoring_frameworks(self, services_config):
        return {
            'health': HealthCheckFramework(services_config),
            'metrics': MetricsValidationFramework(services_config),
            'audit': AuditValidationFramework(services_config)
        }
    
    @pytest.mark.asyncio
    async def test_all_monitoring_endpoints(self, monitoring_frameworks):
        """Test all monitoring endpoints across all services"""
        results = {
            'health': {},
            'metrics': {},
            'audit': {}
        }
        
        # Test health endpoints
        for service_name in monitoring_frameworks['health'].services.keys():
            health_result = await monitoring_frameworks['health'].check_service_health(service_name)
            results['health'][service_name] = health_result
        
        # Test metrics endpoints
        for service_name in monitoring_frameworks['metrics'].services.keys():
            metrics_results = await monitoring_frameworks['metrics'].validate_metrics_endpoint(service_name)
            results['metrics'][service_name] = metrics_results
        
        # Test audit endpoints
        for service_name in monitoring_frameworks['audit'].services.keys():
            audit_result = await monitoring_frameworks['audit'].validate_audit_endpoint(service_name)
            results['audit'][service_name] = audit_result
        
        # Validate all results
        for service_name in monitoring_frameworks['health'].services.keys():
            # Health check
            health_result = results['health'][service_name]
            assert health_result.status.value == 'healthy', f"Health check failed for {service_name}"
            
            # Metrics validation
            metrics_results = results['metrics'][service_name]
            for metric_result in metrics_results:
                if metric_result.metric_name != "metrics_endpoint":
                    assert metric_result.is_valid, f"Metric {metric_result.metric_name} failed for {service_name}"
            
            # Audit validation
            audit_result = results['audit'][service_name]
            assert audit_result['is_valid'], f"Audit validation failed for {service_name}"
    
    @pytest.mark.asyncio
    async def test_monitoring_endpoint_performance(self, monitoring_frameworks):
        """Test monitoring endpoint performance"""
        for service_name in monitoring_frameworks['health'].services.keys():
            # Health endpoint performance
            health_result = await monitoring_frameworks['health'].check_service_health(service_name)
            assert health_result.response_time < 5.0, f"Health endpoint too slow for {service_name}: {health_result.response_time}s"
            
            # Metrics endpoint performance
            start_time = time.time()
            metrics_results = await monitoring_frameworks['metrics'].validate_metrics_endpoint(service_name)
            metrics_time = time.time() - start_time
            assert metrics_time < 10.0, f"Metrics endpoint too slow for {service_name}: {metrics_time}s"
            
            # Audit endpoint performance
            start_time = time.time()
            audit_result = await monitoring_frameworks['audit'].validate_audit_endpoint(service_name)
            audit_time = time.time() - start_time
            assert audit_time < 10.0, f"Audit endpoint too slow for {service_name}: {audit_time}s"
```

#### 2. **GitHub Actions Workflow**
```yaml
# .github/workflows/monitoring-tests.yml
name: Monitoring Endpoint Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '*/15 * * * *'  # Run every 15 minutes

jobs:
  monitoring-tests:
    runs-on: ubuntu-latest
    
    services:
      integration-controller:
        image: personai/integration-controller:latest
        ports:
          - 8001:8001
        env:
          - HEALTH_CHECK_INTERVAL=30s
          - METRICS_ENABLED=true
          - AUDIT_ENABLED=true
      
      content-engine:
        image: personai/content-engine:latest
        ports:
          - 8002:8002
        env:
          - HEALTH_CHECK_INTERVAL=30s
          - METRICS_ENABLED=true
          - AUDIT_ENABLED=true
      
      media-engine:
        image: personai/media-engine:latest
        ports:
          - 8003:8003
        env:
          - HEALTH_CHECK_INTERVAL=30s
          - METRICS_ENABLED=true
          - AUDIT_ENABLED=true
      
      delivery-gateway:
        image: personai/delivery-gateway:latest
        ports:
          - 8004:8004
        env:
          - HEALTH_CHECK_INTERVAL=30s
          - METRICS_ENABLED=true
          - AUDIT_ENABLED=true
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio requests aiohttp
    
    - name: Wait for services
      run: |
        timeout 120 bash -c 'until curl -f http://localhost:8001/health; do sleep 5; done'
        timeout 120 bash -c 'until curl -f http://localhost:8002/health; do sleep 5; done'
        timeout 120 bash -c 'until curl -f http://localhost:8003/health; do sleep 5; done'
        timeout 120 bash -c 'until curl -f http://localhost:8004/health; do sleep 5; done'
    
    - name: Run health endpoint tests
      run: |
        pytest tests/monitoring/health_endpoint_tests.py -v --tb=short --html=health_report.html
    
    - name: Run metrics endpoint tests
      run: |
        pytest tests/monitoring/metrics_endpoint_tests.py -v --tb=short --html=metrics_report.html
    
    - name: Run audit endpoint tests
      run: |
        pytest tests/monitoring/audit_endpoint_tests.py -v --tb=short --html=audit_report.html
    
    - name: Run complete monitoring tests
      run: |
        pytest tests/monitoring/complete_monitoring_tests.py -v --tb=short --html=monitoring_report.html
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      with:
        name: monitoring-test-reports
        path: |
          health_report.html
          metrics_report.html
          audit_report.html
          monitoring_report.html
    
    - name: Alert on failure
      if: failure()
      run: |
        echo "Monitoring tests failed! Check the reports for details."
        # In production, this would send alerts to Slack/email
```

This comprehensive monitoring and testing framework ensures that Person.ai's health, metrics, and audit endpoints are properly validated and monitored, providing confidence in system reliability and observability.
