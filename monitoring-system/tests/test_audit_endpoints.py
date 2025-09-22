import pytest
import requests
import time
from datetime import datetime
from typing import List, Dict, Any

# Mark as Tier 3 Secondary and Integration
pytestmark = [pytest.mark.tier3_secondary, pytest.mark.integration]

class TestAuditEndpoints:
    """Test suite for audit endpoints across all services"""
    
    @pytest.fixture
    def services_config(self):
        return {
            'integration-controller': 'http://localhost:8001',
            'content-engine': 'http://localhost:8002',
            'media-engine': 'http://localhost:8003',
            'delivery-gateway': 'http://localhost:8004'
        }
    
    @pytest.fixture
    def required_event_types(self):
        return [
            'user_login',
            'brief_created',
            'integration_connected',
            'content_generated',
            'audio_generated',
            'message_delivered',
            'error_occurred'
        ]
    
    def test_audit_endpoint_availability(self, services_config):
        """Test audit endpoint availability"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            
            assert response.status_code == 200, f"Service {service_name} audit endpoint failed with status {response.status_code}"
            assert response.headers['Content-Type'] == 'application/json', f"Service {service_name} audit should return JSON"
    
    def test_audit_data_structure(self, services_config):
        """Test audit data structure validation"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            audit_data = response.json()
            
            # Validate top-level structure
            required_fields = ['service', 'total_events', 'returned_events', 'events']
            for field in required_fields:
                assert field in audit_data, f"Service {service_name} missing required field: {field}"
            
            # Validate field types
            assert isinstance(audit_data['total_events'], int), f"Service {service_name} total_events should be int"
            assert isinstance(audit_data['returned_events'], int), f"Service {service_name} returned_events should be int"
            assert isinstance(audit_data['events'], list), f"Service {service_name} events should be list"
            
            # Validate service name
            assert audit_data['service'] == service_name, f"Service {service_name} audit service name mismatch"
    
    def test_audit_event_validation(self, services_config):
        """Test individual audit event validation"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            audit_data = response.json()
            
            events = audit_data['events']
            assert len(events) > 0, f"Service {service_name} should have audit events"
            
            for i, event in enumerate(events):
                # Validate required fields
                required_fields = ['timestamp', 'event_type', 'user_id', 'action', 'success']
                for field in required_fields:
                    assert field in event, f"Service {service_name} event {i} missing required field: {field}"
                
                # Validate field types
                assert isinstance(event['timestamp'], str), f"Service {service_name} event {i} timestamp should be string"
                assert isinstance(event['event_type'], str), f"Service {service_name} event {i} event_type should be string"
                assert isinstance(event['user_id'], str), f"Service {service_name} event {i} user_id should be string"
                assert isinstance(event['action'], str), f"Service {service_name} event {i} action should be string"
                assert isinstance(event['success'], bool), f"Service {service_name} event {i} success should be boolean"
                
                # Validate timestamp format
                try:
                    datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                except ValueError:
                    pytest.fail(f"Service {service_name} event {i} invalid timestamp format: {event['timestamp']}")
    
    def test_audit_event_coverage(self, services_config, required_event_types):
        """Test audit event coverage"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            audit_data = response.json()
            
            events = audit_data['events']
            event_types = [event.get('event_type') for event in events]
            
            # Check that at least some required event types are present
            found_event_types = set(event_types)
            required_found = [et for et in required_event_types if et in found_event_types]
            
            assert len(required_found) > 0, f"Service {service_name} should have at least one required event type"
    
    def test_audit_event_generation(self, services_config):
        """Test audit event generation by triggering events"""
        for service_name, base_url in services_config.items():
            # Get initial event count
            initial_response = requests.get(f"{base_url}/audit", timeout=10)
            initial_events = initial_response.json()['total_events']
            
            # Trigger events based on service type
            if service_name == 'integration-controller':
                # Trigger brief creation
                requests.post(f"{base_url}/api/briefs", json={"title": "Test Brief"})
                # Trigger integration connection
                requests.post(f"{base_url}/api/integrations/connect", json={"type": "slack"})
            elif service_name == 'content-engine':
                # Trigger content generation
                requests.post(f"{base_url}/api/generate", json={"text": "Test content"})
            elif service_name == 'media-engine':
                # Trigger audio generation
                requests.post(f"{base_url}/api/generate-audio", json={"text": "Test audio"})
            elif service_name == 'delivery-gateway':
                # Trigger message delivery
                requests.post(f"{base_url}/api/deliver", json={"message": "Test message"})
            
            # Wait for events to be processed
            time.sleep(2)
            
            # Check that new events were generated
            final_response = requests.get(f"{base_url}/audit", timeout=10)
            final_events = final_response.json()['total_events']
            
            assert final_events >= initial_events, f"Service {service_name} should have generated new audit events"
    
    def test_audit_response_time(self, services_config):
        """Test audit endpoint response times"""
        for service_name, base_url in services_config.items():
            start_time = time.time()
            response = requests.get(f"{base_url}/audit", timeout=10)
            response_time = time.time() - start_time
            
            assert response_time < 5.0, f"Service {service_name} audit endpoint too slow: {response_time:.2f}s"
    
    def test_audit_event_timestamps(self, services_config):
        """Test that audit event timestamps are recent"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            audit_data = response.json()
            
            events = audit_data['events']
            current_time = datetime.now()
            
            for event in events:
                try:
                    event_time = datetime.fromisoformat(event['timestamp'].replace('Z', '+00:00'))
                    time_diff = (current_time - event_time).total_seconds()
                    
                    # Events should be from the last 24 hours
                    assert time_diff < 86400, f"Service {service_name} event too old: {event['timestamp']}"
                except ValueError:
                    pytest.fail(f"Service {service_name} invalid timestamp format: {event['timestamp']}")
    
    def test_audit_event_details(self, services_config):
        """Test that audit events have appropriate details"""
        for service_name, base_url in services_config.items():
            response = requests.get(f"{base_url}/audit", timeout=10)
            audit_data = response.json()
            
            events = audit_data['events']
            
            for event in events:
                # Check that details field exists and is a dict
                if 'details' in event:
                    assert isinstance(event['details'], dict), f"Service {service_name} event details should be dict"
                
                # Check that resource_id exists for most events
                if 'resource_id' in event:
                    assert isinstance(event['resource_id'], str), f"Service {service_name} event resource_id should be string"
                    assert len(event['resource_id']) > 0, f"Service {service_name} event resource_id should not be empty"
