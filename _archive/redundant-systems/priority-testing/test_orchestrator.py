#!/usr/bin/env python3
"""
Priority-Based Testing Orchestrator for 150+ Integrations
Implements tiered testing, parallel execution, and shared mock services
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import concurrent.futures
from pathlib import Path
import yaml
import requests
import threading
from queue import Queue, Empty

class Priority(Enum):
    CRITICAL = "critical"      # Test on every run
    IMPORTANT = "important"    # Test on schema changes + nightly
    SECONDARY = "secondary"    # Test weekly/rotating

class TestTrigger(Enum):
    EVERY_COMMIT = "every_commit"
    SCHEMA_CHANGE = "schema_change"
    NIGHTLY = "nightly"
    WEEKLY = "weekly"
    ROTATING = "rotating"

@dataclass
class Integration:
    name: str
    connector_type: str
    priority: Priority
    base_url: str
    endpoints: List[str]
    mock_service: Optional[str] = None
    test_suite: str = "default"
    last_tested: Optional[datetime] = None
    test_duration: float = 0.0
    success_rate: float = 1.0
    dependencies: List[str] = field(default_factory=list)

@dataclass
class TestResult:
    integration_name: str
    test_suite: str
    passed: bool
    duration: float
    errors: List[str]
    warnings: List[str]
    timestamp: datetime
    priority: Priority

@dataclass
class TestExecution:
    integration: Integration
    result: Optional[TestResult] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str = "pending"  # pending, running, completed, failed

class SharedMockService:
    """Shared mock service for similar integrations"""
    
    def __init__(self, service_type: str, port: int, max_connections: int = 10):
        self.service_type = service_type
        self.port = port
        self.max_connections = max_connections
        self.active_connections = 0
        self.connection_lock = threading.Lock()
        self.is_running = False
        self.server_thread = None
    
    def start(self):
        """Start the shared mock service"""
        if not self.is_running:
            self.is_running = True
            self.server_thread = threading.Thread(target=self._run_server)
            self.server_thread.start()
            print(f"🚀 Started shared mock service: {self.service_type} on port {self.port}")
    
    def stop(self):
        """Stop the shared mock service"""
        self.is_running = False
        if self.server_thread:
            self.server_thread.join()
        print(f"🛑 Stopped shared mock service: {self.service_type}")
    
    def _run_server(self):
        """Run the mock server (simplified implementation)"""
        # In production, this would be a real server
        while self.is_running:
            time.sleep(1)
    
    def acquire_connection(self) -> bool:
        """Acquire a connection to the mock service"""
        with self.connection_lock:
            if self.active_connections < self.max_connections:
                self.active_connections += 1
                return True
            return False
    
    def release_connection(self):
        """Release a connection to the mock service"""
        with self.connection_lock:
            self.active_connections = max(0, self.active_connections - 1)

class PriorityTestOrchestrator:
    """Orchestrates priority-based testing for 150+ integrations"""
    
    def __init__(self, config_file: str = "test_config.yaml"):
        self.config_file = Path(config_file)
        self.integrations: Dict[str, Integration] = {}
        self.shared_mocks: Dict[str, SharedMockService] = {}
        self.test_queue: Queue = Queue()
        self.results: List[TestResult] = []
        self.max_parallel_tests = 20
        self.load_config()
        self.setup_shared_mocks()
    
    def load_config(self):
        """Load test configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            # Load integrations
            for integration_data in config.get('integrations', []):
                integration = Integration(
                    name=integration_data['name'],
                    connector_type=integration_data['connector_type'],
                    priority=Priority(integration_data['priority']),
                    base_url=integration_data['base_url'],
                    endpoints=integration_data['endpoints'],
                    mock_service=integration_data.get('mock_service'),
                    test_suite=integration_data.get('test_suite', 'default'),
                    dependencies=integration_data.get('dependencies', [])
                )
                self.integrations[integration.name] = integration
            
            # Load parallel execution settings
            self.max_parallel_tests = config.get('max_parallel_tests', 20)
        else:
            self.create_sample_config()
    
    def create_sample_config(self):
        """Create sample configuration for 150+ integrations"""
        config = {
            'max_parallel_tests': 20,
            'integrations': []
        }
        
        # Critical integrations (test every commit)
        critical_integrations = [
            {'name': 'slack', 'connector_type': 'messaging', 'priority': 'critical', 
             'base_url': 'http://localhost:8080', 'endpoints': ['/api/chat.postMessage', '/api/conversations.list']},
            {'name': 'gmail', 'connector_type': 'email', 'priority': 'critical',
             'base_url': 'http://localhost:5004', 'endpoints': ['/api/messages', '/api/threads']},
            {'name': 'salesforce', 'connector_type': 'crm', 'priority': 'critical',
             'base_url': 'http://localhost:5001', 'endpoints': ['/api/accounts', '/api/contacts']},
            {'name': 'quickbooks', 'connector_type': 'accounting', 'priority': 'critical',
             'base_url': 'http://localhost:5000', 'endpoints': ['/api/customers', '/api/invoices']},
        ]
        
        # Important integrations (test on schema changes + nightly)
        important_integrations = [
            {'name': 'hubspot', 'connector_type': 'crm', 'priority': 'important',
             'base_url': 'http://localhost:5002', 'endpoints': ['/api/contacts', '/api/companies']},
            {'name': 'stripe', 'connector_type': 'payment', 'priority': 'important',
             'base_url': 'http://localhost:5003', 'endpoints': ['/api/charges', '/api/customers']},
            {'name': 'zendesk', 'connector_type': 'support', 'priority': 'important',
             'base_url': 'http://localhost:5005', 'endpoints': ['/api/tickets', '/api/users']},
            {'name': 'asana', 'connector_type': 'project_management', 'priority': 'important',
             'base_url': 'http://localhost:5006', 'endpoints': ['/api/tasks', '/api/projects']},
        ]
        
        # Secondary integrations (test weekly/rotating)
        secondary_integrations = []
        connector_types = ['crm', 'accounting', 'marketing', 'support', 'project_management', 'communication']
        
        for i in range(142):  # 150 total - 8 already defined
            connector_type = connector_types[i % len(connector_types)]
            integration_name = f"integration_{i+1:03d}"
            
            secondary_integrations.append({
                'name': integration_name,
                'connector_type': connector_type,
                'priority': 'secondary',
                'base_url': f'http://localhost:{5000 + (i % 100)}',
                'endpoints': [f'/api/{connector_type}/data'],
                'mock_service': f'shared_{connector_type}'
            })
        
        config['integrations'] = critical_integrations + important_integrations + secondary_integrations
        
        # Save config
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        print(f"✅ Created sample configuration with {len(config['integrations'])} integrations")
    
    def setup_shared_mocks(self):
        """Setup shared mock services for similar integrations"""
        # Group integrations by connector type
        connector_groups = {}
        for integration in self.integrations.values():
            if integration.mock_service:
                if integration.mock_service not in connector_groups:
                    connector_groups[integration.mock_service] = []
                connector_groups[integration.mock_service].append(integration)
        
        # Create shared mock services
        port = 6000
        for service_type, integrations in connector_groups.items():
            mock_service = SharedMockService(service_type, port, len(integrations))
            self.shared_mocks[service_type] = mock_service
            port += 1
    
    def get_integrations_by_priority(self, priority: Priority) -> List[Integration]:
        """Get integrations by priority level"""
        return [integration for integration in self.integrations.values() 
                if integration.priority == priority]
    
    def get_integrations_by_trigger(self, trigger: TestTrigger) -> List[Integration]:
        """Get integrations that should be tested based on trigger"""
        if trigger == TestTrigger.EVERY_COMMIT:
            return self.get_integrations_by_priority(Priority.CRITICAL)
        elif trigger == TestTrigger.SCHEMA_CHANGE:
            return (self.get_integrations_by_priority(Priority.CRITICAL) + 
                   self.get_integrations_by_priority(Priority.IMPORTANT))
        elif trigger == TestTrigger.NIGHTLY:
            return (self.get_integrations_by_priority(Priority.CRITICAL) + 
                   self.get_integrations_by_priority(Priority.IMPORTANT))
        elif trigger == TestTrigger.WEEKLY:
            return self.get_integrations_by_priority(Priority.SECONDARY)
        elif trigger == TestTrigger.ROTATING:
            # Return a rotating subset of secondary integrations
            secondary = self.get_integrations_by_priority(Priority.SECONDARY)
            # Rotate based on day of week
            day_of_week = datetime.now().weekday()
            start_idx = (day_of_week * 20) % len(secondary)
            return secondary[start_idx:start_idx + 20]
        
        return []
    
    async def run_test_suite(self, integration: Integration) -> TestResult:
        """Run test suite for a single integration"""
        start_time = datetime.now()
        errors = []
        warnings = []
        
        try:
            # Acquire mock service connection if needed
            mock_service = None
            if integration.mock_service and integration.mock_service in self.shared_mocks:
                mock_service = self.shared_mocks[integration.mock_service]
                if not mock_service.acquire_connection():
                    errors.append("Could not acquire mock service connection")
                    return TestResult(
                        integration_name=integration.name,
                        test_suite=integration.test_suite,
                        passed=False,
                        duration=0.0,
                        errors=errors,
                        warnings=warnings,
                        timestamp=start_time,
                        priority=integration.priority
                    )
            
            # Run tests for each endpoint
            for endpoint in integration.endpoints:
                try:
                    url = f"{integration.base_url}{endpoint}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code != 200:
                        errors.append(f"Endpoint {endpoint} returned {response.status_code}")
                    else:
                        # Basic validation
                        data = response.json()
                        if not isinstance(data, dict):
                            warnings.append(f"Endpoint {endpoint} returned non-JSON data")
                
                except requests.exceptions.RequestException as e:
                    errors.append(f"Endpoint {endpoint} failed: {str(e)}")
                except json.JSONDecodeError:
                    warnings.append(f"Endpoint {endpoint} returned invalid JSON")
            
            # Release mock service connection
            if mock_service:
                mock_service.release_connection()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return TestResult(
                integration_name=integration.name,
                test_suite=integration.test_suite,
                passed=len(errors) == 0,
                duration=duration,
                errors=errors,
                warnings=warnings,
                timestamp=end_time,
                priority=integration.priority
            )
        
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            errors.append(f"Test suite failed: {str(e)}")
            
            return TestResult(
                integration_name=integration.name,
                test_suite=integration.test_suite,
                passed=False,
                duration=duration,
                errors=errors,
                warnings=warnings,
                timestamp=end_time,
                priority=integration.priority
            )
    
    async def run_parallel_tests(self, integrations: List[Integration]) -> List[TestResult]:
        """Run tests in parallel with controlled concurrency"""
        print(f"🚀 Running {len(integrations)} tests in parallel (max {self.max_parallel_tests})")
        
        # Create semaphore to limit concurrent tests
        semaphore = asyncio.Semaphore(self.max_parallel_tests)
        
        async def run_with_semaphore(integration):
            async with semaphore:
                return await self.run_test_suite(integration)
        
        # Run tests in parallel
        tasks = [run_with_semaphore(integration) for integration in integrations]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to TestResult
        test_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Create error result
                error_result = TestResult(
                    integration_name=integrations[i].name,
                    test_suite=integrations[i].test_suite,
                    passed=False,
                    duration=0.0,
                    errors=[f"Test execution failed: {str(result)}"],
                    warnings=[],
                    timestamp=datetime.now(),
                    priority=integrations[i].priority
                )
                test_results.append(error_result)
            else:
                test_results.append(result)
        
        return test_results
    
    def run_priority_tests(self, trigger: TestTrigger) -> Dict[str, Any]:
        """Run tests based on priority and trigger"""
        print(f"🎯 Running priority tests for trigger: {trigger.value}")
        
        # Get integrations to test
        integrations = self.get_integrations_by_trigger(trigger)
        print(f"📊 Testing {len(integrations)} integrations")
        
        # Start shared mock services
        for mock_service in self.shared_mocks.values():
            mock_service.start()
        
        try:
            # Run tests
            start_time = time.time()
            results = asyncio.run(self.run_parallel_tests(integrations))
            end_time = time.time()
            
            # Calculate statistics
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.passed)
            failed_tests = total_tests - passed_tests
            
            # Group by priority
            priority_stats = {}
            for priority in Priority:
                priority_results = [r for r in results if r.priority == priority]
                priority_stats[priority.value] = {
                    'total': len(priority_results),
                    'passed': sum(1 for r in priority_results if r.passed),
                    'failed': len(priority_results) - sum(1 for r in priority_results if r.passed)
                }
            
            # Calculate average duration
            avg_duration = sum(r.duration for r in results) / len(results) if results else 0
            
            summary = {
                'trigger': trigger.value,
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'success_rate': passed_tests / total_tests if total_tests > 0 else 0,
                'total_duration': end_time - start_time,
                'avg_test_duration': avg_duration,
                'priority_stats': priority_stats,
                'results': results
            }
            
            # Print summary
            print(f"\n📊 Test Execution Summary")
            print(f"Total Tests: {total_tests}")
            print(f"Passed: {passed_tests} ({passed_tests/total_tests*100:.1f}%)")
            print(f"Failed: {failed_tests}")
            print(f"Total Duration: {end_time - start_time:.2f}s")
            print(f"Avg Test Duration: {avg_duration:.2f}s")
            
            print(f"\n📈 Priority Breakdown:")
            for priority, stats in priority_stats.items():
                print(f"  {priority.title()}: {stats['passed']}/{stats['total']} passed")
            
            return summary
        
        finally:
            # Stop shared mock services
            for mock_service in self.shared_mocks.values():
                mock_service.stop()
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save test results to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_results_{timestamp}.json"
        
        # Convert results to JSON-serializable format
        json_results = {
            'trigger': results['trigger'],
            'total_tests': results['total_tests'],
            'passed': results['passed'],
            'failed': results['failed'],
            'success_rate': results['success_rate'],
            'total_duration': results['total_duration'],
            'avg_test_duration': results['avg_test_duration'],
            'priority_stats': results['priority_stats'],
            'timestamp': datetime.now().isoformat(),
            'results': [
                {
                    'integration_name': r.integration_name,
                    'test_suite': r.test_suite,
                    'passed': r.passed,
                    'duration': r.duration,
                    'errors': r.errors,
                    'warnings': r.warnings,
                    'timestamp': r.timestamp.isoformat(),
                    'priority': r.priority.value
                }
                for r in results['results']
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"💾 Results saved to {filename}")

def main():
    """Main function to demonstrate priority testing"""
    orchestrator = PriorityTestOrchestrator()
    
    print("🎯 Priority-Based Testing Orchestrator")
    print("=" * 50)
    
    # Run different test scenarios
    triggers = [
        TestTrigger.EVERY_COMMIT,
        TestTrigger.NIGHTLY,
        TestTrigger.WEEKLY,
        TestTrigger.ROTATING
    ]
    
    for trigger in triggers:
        print(f"\n{'='*20} {trigger.value.upper()} {'='*20}")
        results = orchestrator.run_priority_tests(trigger)
        orchestrator.save_results(results, f"results_{trigger.value}.json")
    
    print(f"\n✅ Priority testing demonstration completed!")

if __name__ == "__main__":
    main()
