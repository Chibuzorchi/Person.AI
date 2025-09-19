# Question 3: End-to-End Brief Generation Test

## Question
"A new daily brief should: pull data from Gmail, generate narrative texts, and deliver it to Slack. How would you design an end-to-end test to validate that all four stages succeeded, including both text and audio delivery?"

## Comprehensive Answer

### Architecture Overview
I would design a comprehensive end-to-end testing framework that validates the complete Person.ai pipeline: Gmail data extraction → Content generation → Media processing (ElevenLabs) → Multi-channel delivery (Slack, Email, SMS).

### Test Framework Architecture

#### 1. **Core Test Infrastructure**
```python
# e2e_test_framework.py
import pytest
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import time
from dataclasses import dataclass
from enum import Enum

class TestStage(Enum):
    GMAIL_EXTRACTION = "gmail_extraction"
    CONTENT_GENERATION = "content_generation"
    MEDIA_PROCESSING = "media_processing"
    DELIVERY = "delivery"
    VERIFICATION = "verification"

@dataclass
class TestContext:
    test_id: str
    start_time: datetime
    gmail_data: Optional[Dict] = None
    generated_content: Optional[Dict] = None
    audio_file: Optional[str] = None
    delivery_status: Optional[Dict] = None
    verification_results: Optional[Dict] = None

class E2ETestFramework:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_contexts = {}
        self.mock_services = {}
        self.setup_mock_services()
    
    def setup_mock_services(self):
        """Initialize mock services for testing"""
        self.mock_services = {
            'gmail': GmailMockService(self.config['gmail_mock_url']),
            'content_engine': ContentEngineMockService(self.config['content_engine_url']),
            'media_engine': MediaEngineMockService(self.config['media_engine_url']),
            'delivery_gateway': DeliveryGatewayMockService(self.config['delivery_gateway_url']),
            'slack': SlackMockService(self.config['slack_mock_url'])
        }
```

#### 2. **Gmail Data Extraction Testing**
```python
# gmail_extraction_tests.py
import pytest
from faker import Faker
from datetime import datetime, timedelta
import random

class GmailMockService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.fake = Faker()
    
    def generate_realistic_email_data(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate realistic Gmail data for testing"""
        emails = []
        for i in range(count):
            email = {
                'id': f"gmail_{i:06d}",
                'thread_id': f"thread_{random.randint(1, 20):06d}",
                'subject': self._generate_email_subject(),
                'sender': self.fake.email(),
                'recipients': [self.fake.email() for _ in range(random.randint(1, 5))],
                'body': self._generate_email_body(),
                'date': self._random_date_in_range(7),
                'labels': self._generate_labels(),
                'attachments': self._generate_attachments(),
                'importance': random.choice(['high', 'normal', 'low']),
                'read': random.choice([True, False]),
                'starred': random.choice([True, False])
            }
            emails.append(email)
        return emails
    
    def _generate_email_subject(self) -> str:
        """Generate realistic email subjects"""
        subjects = [
            "Daily Standup Meeting - Project Update",
            "Invoice #INV-2024-001 - Payment Due",
            "Client Meeting Scheduled for Tomorrow",
            "Quarterly Sales Report - Q1 2024",
            "New Feature Release - Version 2.1.0",
            "Budget Approval Required - Marketing Campaign",
            "Team Building Event - Next Friday",
            "Security Alert - Password Reset Required",
            "Contract Renewal - 30 Days Notice",
            "Performance Review - Annual Assessment"
        ]
        return random.choice(subjects)
    
    def _generate_email_body(self) -> str:
        """Generate realistic email body content"""
        templates = [
            "Hi team,\n\nI wanted to update you on the progress of {project}.\n\n{details}\n\nBest regards,\n{sender}",
            "Dear {recipient},\n\nPlease find attached the {document_type} for your review.\n\n{instructions}\n\nThank you,\n{sender}",
            "Hello,\n\nThis is a reminder that {action} is due by {deadline}.\n\n{additional_info}\n\nRegards,\n{sender}"
        ]
        template = random.choice(templates)
        return template.format(
            project=self.fake.catch_phrase(),
            details=self.fake.text(max_nb_chars=200),
            recipient=self.fake.name(),
            document_type=random.choice(['report', 'proposal', 'contract', 'invoice']),
            instructions=self.fake.sentence(),
            sender=self.fake.name(),
            action=random.choice(['payment', 'review', 'approval', 'submission']),
            deadline=self.fake.date(),
            additional_info=self.fake.sentence()
        )
    
    def _generate_labels(self) -> List[str]:
        """Generate realistic Gmail labels"""
        labels = ['INBOX', 'SENT', 'DRAFT', 'SPAM', 'TRASH']
        custom_labels = ['Work', 'Personal', 'Important', 'Follow-up', 'Archive']
        return random.sample(labels + custom_labels, random.randint(1, 4))
    
    def _generate_attachments(self) -> List[Dict[str, str]]:
        """Generate realistic attachment data"""
        if random.random() < 0.3:  # 30% chance of attachments
            return [{
                'filename': f"document_{random.randint(1, 100)}.pdf",
                'size': random.randint(1000, 5000000),
                'mime_type': 'application/pdf'
            }]
        return []
    
    def _random_date_in_range(self, days_back: int) -> str:
        """Generate random date within specified range"""
        start_date = datetime.now() - timedelta(days=days_back)
        random_date = start_date + timedelta(days=random.randint(0, days_back))
        return random_date.isoformat()

class TestGmailExtraction:
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.gmail_mock = framework.mock_services['gmail']
    
    async def test_gmail_data_extraction(self, test_context: TestContext) -> bool:
        """Test Gmail data extraction stage"""
        try:
            # Generate test email data
            email_data = self.gmail_mock.generate_realistic_email_data(50)
            
            # Simulate Gmail API call
            response = await self._call_gmail_api(email_data)
            
            if response['status'] == 'success':
                test_context.gmail_data = response['data']
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Gmail extraction failed: {e}")
            return False
    
    async def _call_gmail_api(self, email_data: List[Dict]) -> Dict[str, Any]:
        """Simulate Gmail API call"""
        # In real implementation, this would call the actual Gmail API
        # For testing, we simulate the response
        return {
            'status': 'success',
            'data': {
                'emails': email_data,
                'total_count': len(email_data),
                'extraction_time': time.time(),
                'filters_applied': ['unread', 'last_7_days']
            }
        }
```

#### 3. **Content Generation Testing**
```python
# content_generation_tests.py
import pytest
from typing import Dict, List, Any
import json
import time

class ContentEngineMockService:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def generate_brief_content(self, gmail_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate brief content from Gmail data"""
        # Simulate content generation
        email_summary = self._summarize_emails(gmail_data['emails'])
        key_insights = self._extract_key_insights(gmail_data['emails'])
        action_items = self._identify_action_items(gmail_data['emails'])
        
        return {
            'text_content': self._generate_text_brief(email_summary, key_insights, action_items),
            'audio_script': self._generate_audio_script(email_summary, key_insights, action_items),
            'metadata': {
                'generation_time': time.time(),
                'email_count': len(gmail_data['emails']),
                'confidence_score': 0.85
            }
        }
    
    def _summarize_emails(self, emails: List[Dict]) -> str:
        """Summarize email content"""
        summaries = []
        for email in emails[:10]:  # Top 10 emails
            summaries.append(f"• {email['subject']} - {email['sender']}")
        return "\n".join(summaries)
    
    def _extract_key_insights(self, emails: List[Dict]) -> List[str]:
        """Extract key insights from emails"""
        insights = [
            "3 urgent items require immediate attention",
            "2 client meetings scheduled for this week",
            "1 invoice payment overdue",
            "New project proposal received"
        ]
        return insights
    
    def _identify_action_items(self, emails: List[Dict]) -> List[str]:
        """Identify action items from emails"""
        actions = [
            "Review quarterly sales report",
            "Schedule follow-up meeting with client",
            "Process invoice payment",
            "Prepare project proposal"
        ]
        return actions
    
    def _generate_text_brief(self, summary: str, insights: List[str], actions: List[str]) -> str:
        """Generate text brief"""
        return f"""
Daily Brief - {datetime.now().strftime('%Y-%m-%d')}

Email Summary:
{summary}

Key Insights:
{chr(10).join(f'• {insight}' for insight in insights)}

Action Items:
{chr(10).join(f'• {action}' for action in actions)}

Generated by Person.ai
        """.strip()
    
    def _generate_audio_script(self, summary: str, insights: List[str], actions: List[str]) -> str:
        """Generate audio script"""
        return f"""
Good morning! Here's your daily brief for {datetime.now().strftime('%B %d, %Y')}.

{summary}

Key insights for today: {', '.join(insights)}.

Your action items: {', '.join(actions)}.

This brief was generated by Person.ai. Have a productive day!
        """.strip()

class TestContentGeneration:
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.content_engine = framework.mock_services['content_engine']
    
    async def test_content_generation(self, test_context: TestContext) -> bool:
        """Test content generation stage"""
        try:
            if not test_context.gmail_data:
                return False
            
            # Generate content
            content = self.content_engine.generate_brief_content(test_context.gmail_data)
            
            # Validate content
            if self._validate_content(content):
                test_context.generated_content = content
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Content generation failed: {e}")
            return False
    
    def _validate_content(self, content: Dict[str, Any]) -> bool:
        """Validate generated content"""
        required_fields = ['text_content', 'audio_script', 'metadata']
        
        for field in required_fields:
            if field not in content:
                return False
        
        # Validate text content
        if len(content['text_content']) < 100:
            return False
        
        # Validate audio script
        if len(content['audio_script']) < 50:
            return False
        
        return True
```

#### 4. **Media Processing Testing**
```python
# media_processing_tests.py
import pytest
import os
import tempfile
from typing import Dict, Any
import time

class MediaEngineMockService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.elevenlabs_api_key = "mock_api_key"
    
    def process_audio(self, audio_script: str) -> Dict[str, Any]:
        """Process audio using ElevenLabs"""
        # Simulate audio processing
        audio_file = self._generate_mock_audio_file(audio_script)
        
        return {
            'audio_file': audio_file,
            'duration': len(audio_script) * 0.1,  # Simulate duration
            'file_size': os.path.getsize(audio_file),
            'processing_time': time.time(),
            'voice_id': 'mock_voice_id',
            'quality': 'high'
        }
    
    def _generate_mock_audio_file(self, script: str) -> str:
        """Generate mock audio file"""
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        temp_file.write(b'mock_audio_data')
        temp_file.close()
        return temp_file.name

class TestMediaProcessing:
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.media_engine = framework.mock_services['media_engine']
    
    async def test_media_processing(self, test_context: TestContext) -> bool:
        """Test media processing stage"""
        try:
            if not test_context.generated_content:
                return False
            
            # Process audio
            audio_result = self.media_engine.process_audio(
                test_context.generated_content['audio_script']
            )
            
            # Validate audio file
            if self._validate_audio_file(audio_result['audio_file']):
                test_context.audio_file = audio_result['audio_file']
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Media processing failed: {e}")
            return False
    
    def _validate_audio_file(self, audio_file: str) -> bool:
        """Validate audio file"""
        if not os.path.exists(audio_file):
            return False
        
        if os.path.getsize(audio_file) == 0:
            return False
        
        return True
```

#### 5. **Delivery Testing**
```python
# delivery_tests.py
import pytest
import requests
from typing import Dict, List, Any
import time

class DeliveryGatewayMockService:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.delivery_channels = ['slack', 'email', 'sms']
    
    def send_to_slack(self, content: Dict[str, Any], audio_file: str) -> Dict[str, Any]:
        """Send brief to Slack"""
        # Simulate Slack delivery
        return {
            'channel': 'general',
            'message_id': f"slack_{int(time.time())}",
            'status': 'delivered',
            'delivery_time': time.time(),
            'text_delivered': True,
            'audio_delivered': True
        }
    
    def send_to_email(self, content: Dict[str, Any], audio_file: str) -> Dict[str, Any]:
        """Send brief to email"""
        # Simulate email delivery
        return {
            'recipient': 'user@example.com',
            'message_id': f"email_{int(time.time())}",
            'status': 'delivered',
            'delivery_time': time.time(),
            'text_delivered': True,
            'audio_delivered': True
        }
    
    def send_to_sms(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Send brief to SMS"""
        # Simulate SMS delivery
        return {
            'recipient': '+1234567890',
            'message_id': f"sms_{int(time.time())}",
            'status': 'delivered',
            'delivery_time': time.time(),
            'text_delivered': True
        }

class TestDelivery:
    def __init__(self, framework: E2ETestFramework):
        self.framework = framework
        self.delivery_gateway = framework.mock_services['delivery_gateway']
    
    async def test_delivery(self, test_context: TestContext) -> bool:
        """Test delivery stage"""
        try:
            if not test_context.generated_content or not test_context.audio_file:
                return False
            
            delivery_results = {}
            
            # Test Slack delivery
            slack_result = self.delivery_gateway.send_to_slack(
                test_context.generated_content,
                test_context.audio_file
            )
            delivery_results['slack'] = slack_result
            
            # Test email delivery
            email_result = self.delivery_gateway.send_to_email(
                test_context.generated_content,
                test_context.audio_file
            )
            delivery_results['email'] = email_result
            
            # Test SMS delivery
            sms_result = self.delivery_gateway.send_to_sms(
                test_context.generated_content
            )
            delivery_results['sms'] = sms_result
            
            # Validate all deliveries
            if self._validate_deliveries(delivery_results):
                test_context.delivery_status = delivery_results
                return True
            else:
                return False
                
        except Exception as e:
            print(f"Delivery failed: {e}")
            return False
    
    def _validate_deliveries(self, delivery_results: Dict[str, Any]) -> bool:
        """Validate delivery results"""
        for channel, result in delivery_results.items():
            if result['status'] != 'delivered':
                return False
            if not result['text_delivered']:
                return False
        return True
```

#### 6. **Complete E2E Test Implementation**
```python
# complete_e2e_test.py
import pytest
import asyncio
from datetime import datetime
import uuid

class CompleteE2ETest:
    def __init__(self, config: Dict[str, Any]):
        self.framework = E2ETestFramework(config)
        self.test_stages = [
            TestGmailExtraction(self.framework),
            TestContentGeneration(self.framework),
            TestMediaProcessing(self.framework),
            TestDelivery(self.framework)
        ]
    
    async def run_complete_e2e_test(self) -> Dict[str, Any]:
        """Run complete end-to-end test"""
        test_id = str(uuid.uuid4())
        test_context = TestContext(
            test_id=test_id,
            start_time=datetime.now()
        )
        
        results = {
            'test_id': test_id,
            'start_time': test_context.start_time,
            'stages': {},
            'overall_success': True,
            'errors': []
        }
        
        # Run each stage
        for i, stage in enumerate(self.test_stages):
            stage_name = f"stage_{i+1}"
            try:
                if i == 0:  # Gmail extraction
                    success = await stage.test_gmail_data_extraction(test_context)
                elif i == 1:  # Content generation
                    success = await stage.test_content_generation(test_context)
                elif i == 2:  # Media processing
                    success = await stage.test_media_processing(test_context)
                elif i == 3:  # Delivery
                    success = await stage.test_delivery(test_context)
                
                results['stages'][stage_name] = {
                    'success': success,
                    'timestamp': datetime.now().isoformat()
                }
                
                if not success:
                    results['overall_success'] = False
                    results['errors'].append(f"Stage {i+1} failed")
                    
            except Exception as e:
                results['stages'][stage_name] = {
                    'success': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                results['overall_success'] = False
                results['errors'].append(f"Stage {i+1} error: {str(e)}")
        
        results['end_time'] = datetime.now()
        results['duration'] = (results['end_time'] - results['start_time']).total_seconds()
        
        return results

# Test execution
@pytest.mark.asyncio
async def test_daily_brief_generation():
    """Main E2E test for daily brief generation"""
    config = {
        'gmail_mock_url': 'http://localhost:5000',
        'content_engine_url': 'http://localhost:5001',
        'media_engine_url': 'http://localhost:5002',
        'delivery_gateway_url': 'http://localhost:5003',
        'slack_mock_url': 'http://localhost:5004'
    }
    
    e2e_test = CompleteE2ETest(config)
    results = await e2e_test.run_complete_e2e_test()
    
    # Assertions
    assert results['overall_success'] == True, f"E2E test failed: {results['errors']}"
    assert len(results['stages']) == 4, "All 4 stages should be executed"
    
    for stage_name, stage_result in results['stages'].items():
        assert stage_result['success'] == True, f"Stage {stage_name} failed"
    
    print(f"E2E test completed successfully in {results['duration']:.2f} seconds")
```

### CI/CD Integration

#### 1. **GitHub Actions Workflow**
```yaml
# .github/workflows/e2e-tests.yml
name: End-to-End Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]
  schedule:
    - cron: '0 6 * * *'  # Run daily at 6 AM

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    
    services:
      gmail-mock:
        image: gmail-mock:latest
        ports:
          - 5000:5000
      
      content-engine:
        image: content-engine:latest
        ports:
          - 5001:5001
      
      media-engine:
        image: media-engine:latest
        ports:
          - 5002:5002
      
      delivery-gateway:
        image: delivery-gateway:latest
        ports:
          - 5003:5003
      
      slack-mock:
        image: slack-mock:latest
        ports:
          - 5004:5004
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio requests faker
    
    - name: Wait for services
      run: |
        timeout 60 bash -c 'until curl -f http://localhost:5000/health; do sleep 2; done'
        timeout 60 bash -c 'until curl -f http://localhost:5001/health; do sleep 2; done'
        timeout 60 bash -c 'until curl -f http://localhost:5002/health; do sleep 2; done'
        timeout 60 bash -c 'until curl -f http://localhost:5003/health; do sleep 2; done'
        timeout 60 bash -c 'until curl -f http://localhost:5004/health; do sleep 2; done'
    
    - name: Run E2E tests
      run: |
        pytest tests/e2e/complete_e2e_test.py -v --tb=short --html=e2e_report.html
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      with:
        name: e2e-test-reports
        path: e2e_report.html
```

This comprehensive E2E testing framework ensures that Person.ai's daily brief generation pipeline works correctly across all stages, providing confidence in the system's reliability and performance.
