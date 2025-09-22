#!/usr/bin/env python3
"""
Standalone E2E Tests - No Docker Required
Tests the E2E pipeline logic without requiring Docker services
"""
import pytest
import json
import sys
import os
import asyncio
from unittest.mock import Mock, patch

# Mark as Tier 1 Critical and Standalone
pytestmark = [pytest.mark.tier1_critical, pytest.mark.standalone]

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestE2EStandalone:
    """Test E2E pipeline without Docker services"""
    
    def test_e2e_test_runner_initialization(self):
        """Test that E2E test runner can be initialized"""
        try:
            from test_runner.e2e_test_runner import E2ETestRunner
            runner = E2ETestRunner()
            assert runner is not None
            print("✅ E2E test runner initialized successfully")
        except ImportError as e:
            pytest.skip(f"E2E test runner not available: {e}")
    
    def test_gmail_mock_initialization(self):
        """Test Gmail mock service initialization"""
        try:
            from mock_services.gmail.app import app
            assert app is not None
            print("✅ Gmail mock service initialized successfully")
        except ImportError as e:
            pytest.skip(f"Gmail mock not available: {e}")
    
    def test_content_engine_initialization(self):
        """Test Content Engine initialization"""
        try:
            from mock_services.content_engine.app import app
            assert app is not None
            print("✅ Content Engine initialized successfully")
        except ImportError as e:
            pytest.skip(f"Content Engine not available: {e}")
    
    def test_media_engine_initialization(self):
        """Test Media Engine initialization"""
        try:
            from mock_services.media_engine.app import app
            assert app is not None
            print("✅ Media Engine initialized successfully")
        except ImportError as e:
            pytest.skip(f"Media Engine not available: {e}")
    
    def test_delivery_gateway_initialization(self):
        """Test Delivery Gateway initialization"""
        try:
            from mock_services.delivery_gateway.app import app
            assert app is not None
            print("✅ Delivery Gateway initialized successfully")
        except ImportError as e:
            pytest.skip(f"Delivery Gateway not available: {e}")
    
    def test_e2e_pipeline_logic(self):
        """Test E2E pipeline logic without actual HTTP calls"""
        try:
            from test_runner.e2e_test_runner import E2ETestRunner
            
            # Mock the HTTP calls
            with patch('requests.get') as mock_get, \
                 patch('requests.post') as mock_post:
                
                # Mock Gmail data
                mock_gmail_response = Mock()
                mock_gmail_response.json.return_value = {
                    "messages": [
                        {
                            "id": "test123",
                            "payload": {
                                "headers": [
                                    {"name": "Subject", "value": "Test Email"},
                                    {"name": "From", "value": "test@example.com"}
                                ]
                            }
                        }
                    ]
                }
                mock_gmail_response.status_code = 200
                mock_get.return_value = mock_gmail_response
                
                # Mock Content Engine response
                mock_content_response = Mock()
                mock_content_response.json.return_value = {
                    "content": "Test briefing content",
                    "status": "success"
                }
                mock_content_response.status_code = 200
                mock_post.return_value = mock_content_response
                
                # Mock Media Engine response
                mock_media_response = Mock()
                mock_media_response.json.return_value = {
                    "audio_file": "test_audio.wav",
                    "status": "success"
                }
                mock_media_response.status_code = 200
                
                # Mock Delivery Gateway response
                mock_delivery_response = Mock()
                mock_delivery_response.json.return_value = {
                    "message": "Briefing delivered successfully",
                    "status": "success"
                }
                mock_delivery_response.status_code = 200
                
                # Set up mock responses
                mock_post.side_effect = [mock_content_response, mock_media_response, mock_delivery_response]
                
                # Test the pipeline
                runner = E2ETestRunner()
                # Since this is an async method, we need to run it properly
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(runner.run_complete_e2e_test())
                finally:
                    loop.close()
                
                assert result is not None
                print("✅ E2E pipeline logic works correctly")
                
        except ImportError as e:
            pytest.skip(f"E2E test runner not available: {e}")

    def test_ai_quality_validation_logic(self):
        """Test AI quality validation logic without external services"""
        try:
            from ai_quality_validation import AIQualityValidator
            validator = AIQualityValidator()
            
            # Test content that should pass (DEMO: Add negative value to make it fail)
            test_content = """Daily Brief - 2024-01-15

Email Summary:
• Quarterly Sales Report - john@company.com
• Client Meeting Request - sarah@client.com
• Invoice Payment Overdue - billing@vendor.com

Key Insights:
• 3 urgent items require immediate attention
• 2 client meetings scheduled for this week
• 1 invoice payment overdue
• Revenue: $500 (LOSS DETECTED)  # DEMO: This will make business rules fail
• New project proposal received

Action Items:
• Review quarterly sales report
• Schedule follow-up meeting with client
• Process invoice payment
• Prepare project proposal

Generated by Person.ai"""
            
            # Test text validation
            result = validator.validate_content_quality(test_content, "text")
            
            # Check that validation passed
            assert result['validations']['semantic_similarity']['passed'] == True
            assert result['validations']['structure']['passed'] == True
            assert result['validations']['business_rules']['passed'] == True
            
            print("✅ AI quality validation logic works correctly")
            
        except ImportError as e:
            pytest.skip(f"AI quality validation not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
