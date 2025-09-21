#!/usr/bin/env python3
"""
E2E Test Runner for Person.ai Pipeline
"""
import os
import sys
import json
import time
import requests
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
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

class E2ETestRunner:
    def __init__(self):
        self.config = {
            'gmail_mock_url': os.getenv('GMAIL_MOCK_URL', 'http://localhost:5004'),
            'content_engine_url': os.getenv('CONTENT_ENGINE_URL', 'http://localhost:5005'),
            'media_engine_url': os.getenv('MEDIA_ENGINE_URL', 'http://localhost:5006'),
            'delivery_gateway_url': os.getenv('DELIVERY_GATEWAY_URL', 'http://localhost:5007')
        }
        self.test_results = []
        self.logs = []
    
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        self.logs.append(log_entry)
    
    def wait_for_services(self, timeout: int = 60):
        """Wait for all services to be ready"""
        self.log("Waiting for services to be ready...")
        
        services = [
            ('Gmail Mock', f"{self.config['gmail_mock_url']}/health"),
            ('Content Engine', f"{self.config['content_engine_url']}/health"),
            ('Media Engine', f"{self.config['media_engine_url']}/health"),
            ('Delivery Gateway', f"{self.config['delivery_gateway_url']}/health")
        ]
        
        for service_name, url in services:
            self.log(f"Checking {service_name}...")
            for i in range(timeout):
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        self.log(f"✅ {service_name} is ready")
                        break
                except:
                    pass
                
                if i == timeout - 1:
                    self.log(f"❌ {service_name} failed to start", "ERROR")
                    return False
                
                time.sleep(1)
        
        return True
    
    async def test_gmail_extraction(self, test_context: TestContext) -> bool:
        """Test Gmail data extraction stage"""
        self.log("🔍 Testing Gmail data extraction...")
        
        try:
            # Get Gmail messages
            response = requests.get(
                f"{self.config['gmail_mock_url']}/gmail/v1/users/me/messages",
                params={'maxResults': 10}
            )
            
            if response.status_code != 200:
                self.log(f"Gmail API failed: {response.status_code}", "ERROR")
                return False
            
            messages_data = response.json()
            messages = messages_data.get('messages', [])
            
            # Get detailed message data
            detailed_emails = []
            for message in messages[:5]:  # Get first 5 messages
                msg_response = requests.get(
                    f"{self.config['gmail_mock_url']}/gmail/v1/users/me/messages/{message['id']}"
                )
                
                if msg_response.status_code == 200:
                    detailed_emails.append(msg_response.json())
            
            test_context.gmail_data = {
                'emails': detailed_emails,
                'total_count': len(detailed_emails),
                'extraction_time': time.time()
            }
            
            self.log(f"✅ Extracted {len(detailed_emails)} emails")
            return True
            
        except Exception as e:
            self.log(f"Gmail extraction failed: {e}", "ERROR")
            return False
    
    async def test_content_generation(self, test_context: TestContext) -> bool:
        """Test content generation stage"""
        self.log("🔍 Testing content generation...")
        
        try:
            if not test_context.gmail_data:
                self.log("No Gmail data available", "ERROR")
                return False
            
            # Generate content
            response = requests.post(
                f"{self.config['content_engine_url']}/generate-brief",
                json={'gmail_data': test_context.gmail_data}
            )
            
            if response.status_code != 200:
                self.log(f"Content generation failed: {response.status_code}", "ERROR")
                return False
            
            content_data = response.json()
            test_context.generated_content = content_data['content']
            
            self.log("✅ Content generated successfully")
            self.log(f"Text length: {len(test_context.generated_content['text_content'])}")
            self.log(f"Audio script length: {len(test_context.generated_content['audio_script'])}")
            
            return True
            
        except Exception as e:
            self.log(f"Content generation failed: {e}", "ERROR")
            return False
    
    async def test_media_processing(self, test_context: TestContext) -> bool:
        """Test media processing stage"""
        self.log("🔍 Testing media processing...")
        
        try:
            if not test_context.generated_content:
                self.log("No generated content available", "ERROR")
                return False
            
            # Generate audio
            response = requests.post(
                f"{self.config['media_engine_url']}/generate-audio",
                json={'text': test_context.generated_content['audio_script']}
            )
            
            if response.status_code != 200:
                self.log(f"Media processing failed: {response.status_code}", "ERROR")
                return False
            
            audio_data = response.json()
            test_context.audio_file = audio_data['result']['filename']
            
            self.log("✅ Audio generated successfully")
            self.log(f"Audio file: {test_context.audio_file}")
            self.log(f"Duration: {audio_data['result']['duration']:.2f}s")
            self.log(f"File size: {audio_data['result']['file_size']} bytes")
            
            return True
            
        except Exception as e:
            self.log(f"Media processing failed: {e}", "ERROR")
            return False
    
    async def test_delivery(self, test_context: TestContext) -> bool:
        """Test delivery stage"""
        self.log("🔍 Testing delivery...")
        
        try:
            if not test_context.generated_content or not test_context.audio_file:
                self.log("No content or audio file available", "ERROR")
                return False
            
            # Deliver to all channels
            response = requests.post(
                f"{self.config['delivery_gateway_url']}/deliver/all",
                json={
                    'content': test_context.generated_content,
                    'audio_file': test_context.audio_file
                }
            )
            
            if response.status_code != 200:
                self.log(f"Delivery failed: {response.status_code}", "ERROR")
                return False
            
            delivery_data = response.json()
            test_context.delivery_status = delivery_data['results']
            
            # Check delivery results
            success_count = 0
            for channel, result in delivery_data['results'].items():
                if result['status'] == 'delivered':
                    success_count += 1
                    self.log(f"✅ {channel.title()} delivery successful")
                else:
                    self.log(f"❌ {channel.title()} delivery failed: {result.get('error', 'Unknown error')}", "ERROR")
            
            self.log(f"Delivery summary: {success_count}/3 channels successful")
            return success_count > 0
            
        except Exception as e:
            self.log(f"Delivery failed: {e}", "ERROR")
            return False
    
    async def test_verification(self, test_context: TestContext) -> bool:
        """Test verification stage"""
        self.log("🔍 Testing verification...")
        
        try:
            verification_results = {
                'gmail_data_valid': test_context.gmail_data is not None,
                'content_generated': test_context.generated_content is not None,
                'audio_generated': test_context.audio_file is not None,
                'delivery_successful': test_context.delivery_status is not None,
                'all_stages_complete': all([
                    test_context.gmail_data is not None,
                    test_context.generated_content is not None,
                    test_context.audio_file is not None,
                    test_context.delivery_status is not None
                ])
            }
            
            test_context.verification_results = verification_results
            
            # Log verification results
            for check, result in verification_results.items():
                status = "✅" if result else "❌"
                self.log(f"{status} {check}: {result}")
            
            return verification_results['all_stages_complete']
            
        except Exception as e:
            self.log(f"Verification failed: {e}", "ERROR")
            return False
    
    async def run_complete_e2e_test(self) -> Dict[str, Any]:
        """Run complete end-to-end test"""
        test_id = f"e2e_{int(time.time())}"
        test_context = TestContext(
            test_id=test_id,
            start_time=datetime.now()
        )
        
        self.log(f"🚀 Starting E2E test: {test_id}")
        
        results = {
            'test_id': test_id,
            'start_time': test_context.start_time.isoformat(),
            'stages': {},
            'overall_success': True,
            'errors': [],
            'duration': 0
        }
        
        # Run each stage
        stages = [
            ('gmail_extraction', self.test_gmail_extraction),
            ('content_generation', self.test_content_generation),
            ('media_processing', self.test_media_processing),
            ('delivery', self.test_delivery),
            ('verification', self.test_verification)
        ]
        
        for stage_name, stage_func in stages:
            stage_start = time.time()
            try:
                success = await stage_func(test_context)
                stage_duration = time.time() - stage_start
                
                results['stages'][stage_name] = {
                    'success': success,
                    'duration': stage_duration,
                    'timestamp': datetime.now().isoformat()
                }
                
                if not success:
                    results['overall_success'] = False
                    results['errors'].append(f"Stage {stage_name} failed")
                    
            except Exception as e:
                stage_duration = time.time() - stage_start
                results['stages'][stage_name] = {
                    'success': False,
                    'error': str(e),
                    'duration': stage_duration,
                    'timestamp': datetime.now().isoformat()
                }
                results['overall_success'] = False
                results['errors'].append(f"Stage {stage_name} error: {str(e)}")
        
        # Calculate total duration
        results['end_time'] = datetime.now().isoformat()
        results['duration'] = (datetime.now() - test_context.start_time).total_seconds()
        
        # Save results
        self.save_test_results(results)
        
        return results
    
    def save_test_results(self, results: Dict[str, Any]):
        """Save test results to file"""
        try:
            os.makedirs('/app/output', exist_ok=True)
            results_file = f"/app/output/e2e_test_results_{results['test_id']}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            self.log(f"Test results saved to: {results_file}")
            
        except Exception as e:
            self.log(f"Failed to save results: {e}", "ERROR")

async def main():
    """Main function"""
    print("🚀 Person.ai E2E Test Runner")
    print("=" * 50)
    
    runner = E2ETestRunner()
    
    # Wait for services
    if not runner.wait_for_services():
        print("❌ Services not ready, exiting")
        sys.exit(1)
    
    # Run E2E test
    results = await runner.run_complete_e2e_test()
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 E2E Test Summary")
    print("=" * 50)
    print(f"Test ID: {results['test_id']}")
    print(f"Duration: {results['duration']:.2f} seconds")
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    
    print("\nStage Results:")
    for stage_name, stage_result in results['stages'].items():
        status = "✅" if stage_result['success'] else "❌"
        duration = stage_result.get('duration', 0)
        print(f"  {status} {stage_name}: {duration:.2f}s")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  ❌ {error}")
    
    print(f"\n📝 Logs saved to: /app/output/e2e_logs_{results['test_id']}.txt")
    
    # Save logs
    try:
        with open(f"/app/output/e2e_logs_{results['test_id']}.txt", 'w') as f:
            f.write('\n'.join(runner.logs))
    except:
        pass
    
    return results['overall_success']

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
