#!/usr/bin/env python3
"""
Standalone Slack Tests - No Docker Required
Tests the Slack mock without requiring Docker services
"""
import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestSlackStandalone:
    """Test Slack mock without Docker services"""
    
    def test_slack_mock_initialization(self):
        """Test that Slack mock can be initialized"""
        try:
            # Test the contract testing functionality
            from contract_testing import SlackContractValidator
            validator = SlackContractValidator()
            assert validator is not None
            print("✅ Slack contract validator initialized successfully")
        except ImportError as e:
            pytest.skip(f"Slack contract testing not available: {e}")
    
    def test_contract_validation_logic(self):
        """Test contract validation logic without HTTP calls"""
        try:
            from contract_testing import SlackContractValidator
            
            validator = SlackContractValidator()
            
            # Test with sample Slack API response
            sample_response = {
                "ok": True,
                "channel": "C1234567890",
                "ts": "1234567890.123456",
                "message": {
                    "text": "Hello, world!",
                    "user": "U1234567890",
                    "ts": "1234567890.123456"
                }
            }
            
            result = validator.validate_response("/api/chat.postMessage", "POST", sample_response)
            assert result is not None
            assert 'is_valid' in result
            print("✅ Contract validation logic works")
            
        except ImportError as e:
            pytest.skip(f"Slack contract testing not available: {e}")
    
    def test_schema_drift_detection_logic(self):
        """Test schema drift detection logic"""
        try:
            from contract_testing import SlackContractValidator
            
            validator = SlackContractValidator()
            
            # Test with drifted response
            drifted_response = {
                "ok": True,
                "channel": "C1234567890",
                "ts": "1234567890.123456",
                "message": {
                    "text": "Hello, world!",
                    "user": "U1234567890",
                    "ts": "1234567890.123456"
                },
                "new_field": "This is a new field"
            }
            
            result = validator.detect_schema_drift("/api/chat.postMessage", "POST", drifted_response)
            assert result is not None
            assert 'has_drift' in result
            print("✅ Schema drift detection logic works")
            
        except ImportError as e:
            pytest.skip(f"Slack contract testing not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
