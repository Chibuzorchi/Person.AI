"""
E2E Pipeline Tests
"""
import pytest
import requests
import time
import asyncio
import sys
import os

# Add the parent directory to the path so we can import the test runner
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from test_runner.e2e_test_runner import E2ETestRunner
except ImportError:
    # Skip all tests in this file if the test runner is not available
    pytestmark = pytest.mark.skip(reason="E2E test runner not available")

class TestE2EPipeline:
    def test_services_health(self):
        """Test that all services are healthy"""
        services = [
            ('Gmail Mock', 'http://localhost:5004/health'),
            ('Content Engine', 'http://localhost:5005/health'),
            ('Media Engine', 'http://localhost:5006/health'),
            ('Delivery Gateway', 'http://localhost:5007/health')
        ]
        
        for service_name, url in services:
            response = requests.get(url, timeout=10)
            assert response.status_code == 200, f"{service_name} is not healthy"
            
            data = response.json()
            assert data['status'] == 'healthy', f"{service_name} status is not healthy"
    
    def test_gmail_data_extraction(self):
        """Test Gmail data extraction"""
        response = requests.get(
            'http://localhost:5004/gmail/v1/users/me/messages?maxResults=5',
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'messages' in data
        assert len(data['messages']) > 0
    
    def test_content_generation(self):
        """Test content generation"""
        test_data = {
            'gmail_data': {
                'emails': [
                    {
                        'subject': 'Test Email',
                        'sender': 'test@example.com',
                        'body': 'This is a test email body content.'
                    }
                ]
            }
        }
        
        response = requests.post(
            'http://localhost:5005/generate-brief',
            json=test_data,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'content' in data
        assert 'text_content' in data['content']
        # DEMO: This will fail because audio_script is commented out in content engine
        assert 'audio_script' in data['content'], "audio_script missing - content engine has it commented out for demo"
    
    def test_audio_generation(self):
        """Test audio generation"""
        test_data = {
            'text': 'Hello, this is a test audio generation for Person.ai E2E testing.'
        }
        
        response = requests.post(
            'http://localhost:5006/generate-audio',
            json=test_data,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'result' in data
        assert 'filename' in data['result']
        assert 'duration' in data['result']
    
    def test_delivery_gateway(self):
        """Test delivery gateway"""
        test_data = {
            'content': {
                'text_content': 'Test brief content',
                'audio_script': 'Test audio script'
            },
            'audio_file': 'test.wav'
        }
        
        response = requests.post(
            'http://localhost:5007/deliver/all',
            json=test_data,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'results' in data
        assert 'slack' in data['results']
        assert 'email' in data['results']
        assert 'sms' in data['results']
    
    @pytest.mark.asyncio
    async def test_complete_e2e_pipeline(self):
        """Test complete E2E pipeline"""
        runner = E2ETestRunner()
        
        # DEMO: Add artificial delay to make test fail on duration
        import time
        time.sleep(2)  # This will make duration longer but not hang the demo
        
        # Wait for services
        assert runner.wait_for_services(timeout=30)
        
        # Run complete test
        results = await runner.run_complete_e2e_test()
        
        # Assertions
        assert results['overall_success'] == True
        assert len(results['stages']) == 5  # All 5 stages
        
        for stage_name, stage_result in results['stages'].items():
            assert stage_result['success'] == True, f"Stage {stage_name} failed"
        
        # Check duration is reasonable (less than 5 minutes)
        assert results['duration'] < 300, "Test took too long"
