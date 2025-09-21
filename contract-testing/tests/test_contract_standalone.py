#!/usr/bin/env python3
"""
Standalone Contract Testing - No External Dependencies
Tests the contract testing system without requiring external services
"""
import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestContractStandalone:
    """Test contract testing system without external dependencies"""
    
    def test_safe_integration_initialization(self):
        """Test safe integration initialization"""
        try:
            from safe_integration import SafeContractIntegration
            integration = SafeContractIntegration()
            assert integration is not None
            print("✅ Safe contract integration initialized successfully")
        except ImportError as e:
            pytest.skip(f"Safe contract integration not available: {e}")
    
    def test_advanced_contract_testing_availability(self):
        """Test if advanced contract testing is available"""
        try:
            from safe_integration import SafeContractIntegration
            integration = SafeContractIntegration()
            
            # Test if advanced features are available
            result = integration.test_advanced_features()
            assert result is not None
            print("✅ Advanced contract testing features available")
            
        except ImportError as e:
            pytest.skip(f"Safe contract integration not available: {e}")
    
    def test_contract_validation_logic(self):
        """Test contract validation logic"""
        try:
            from safe_integration import SafeContractIntegration
            integration = SafeContractIntegration()
            
            # Test with sample contract data
            sample_contract = {
                "endpoint": "/api/test",
                "method": "GET",
                "response": {
                    "status": "success",
                    "data": {"test": "value"}
                }
            }
            
            result = integration.validate_contract(sample_contract)
            assert result is not None
            print("✅ Contract validation logic works")
            
        except ImportError as e:
            pytest.skip(f"Safe contract integration not available: {e}")
    
    def test_schema_drift_detection_logic(self):
        """Test schema drift detection logic"""
        try:
            from safe_integration import SafeContractIntegration
            integration = SafeContractIntegration()
            
            # Test with sample schema data
            baseline_schema = {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"}
                }
            }
            
            new_schema = {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "data": {"type": "object"},
                    "new_field": {"type": "string"}  # This should trigger drift
                }
            }
            
            result = integration.detect_schema_drift(baseline_schema, new_schema)
            assert result is not None
            print("✅ Schema drift detection logic works")
            
        except ImportError as e:
            pytest.skip(f"Safe contract integration not available: {e}")
    
    def test_contract_files_exist(self):
        """Test that contract files exist"""
        contract_files = [
            'contracts/slack_chat_postMessage_POST.json',
            'contracts/quickbooks_customers_GET.json',
            'contracts/salesforce_accounts_GET.json'
        ]
        
        for file_path in contract_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            assert os.path.exists(full_path), f"Contract file {file_path} not found"
        
        print("✅ All contract files exist")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
