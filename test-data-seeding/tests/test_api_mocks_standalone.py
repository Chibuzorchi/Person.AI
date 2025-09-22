#!/usr/bin/env python3
"""
Standalone API Mock Tests - No Docker Required
Tests the mock services without requiring Docker to be running
"""
import pytest
import json
from unittest.mock import Mock, patch
import sys
import os

# Mark as Tier 2 Important and Standalone
pytestmark = [pytest.mark.tier2_important, pytest.mark.standalone]

# Add the parent directory to the path so we can import the mock services
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'api_mocks'))

class TestQuickBooksMockStandalone:
    """Test QuickBooks mock service without Docker"""
    
    def test_quickbooks_mock_initialization(self):
        """Test that QuickBooks mock can be initialized"""
        try:
            from quickbooks_mock.app import app
            assert app is not None
            print("✅ QuickBooks mock app initialized successfully")
        except ImportError as e:
            pytest.skip(f"QuickBooks mock not available: {e}")
    
    def test_quickbooks_health_endpoint_logic(self):
        """Test health endpoint logic without making HTTP requests"""
        try:
            from quickbooks_mock.app import app
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'healthy'
                assert 'timestamp' in data
                print("✅ QuickBooks health endpoint logic works")
        except ImportError as e:
            pytest.skip(f"QuickBooks mock not available: {e}")
    
    def test_quickbooks_customers_endpoint_logic(self):
        """Test customers endpoint logic without making HTTP requests"""
        try:
            from quickbooks_mock.app import app
            with patch('quickbooks_mock.app.get_db_connection') as mock_db:
                # Mock database connection to return empty result
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_cursor.description = []
                mock_conn.cursor.return_value = mock_cursor
                mock_db.return_value = mock_conn
                
                with app.test_client() as client:
                    response = client.get('/v3/company/123/customers?maxResults=5')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert 'QueryResponse' in data
                    print("✅ QuickBooks customers endpoint logic works")
        except ImportError as e:
            pytest.skip(f"QuickBooks mock not available: {e}")
    
    def test_quickbooks_create_customer_logic(self):
        """Test create customer logic without making HTTP requests"""
        try:
            from quickbooks_mock.app import app
            customer_data = {
                "Name": "Test Customer",
                "Email": "test@example.com",
                "Phone": "555-1234"
            }
            with app.test_client() as client:
                response = client.post('/v3/company/123/customers', json=customer_data)
                assert response.status_code == 201
                data = response.get_json()
                assert 'QueryResponse' in data
                print("✅ QuickBooks create customer logic works")
        except ImportError as e:
            pytest.skip(f"QuickBooks mock not available: {e}")

class TestSalesforceMockStandalone:
    """Test Salesforce mock service without Docker"""
    
    def test_salesforce_mock_initialization(self):
        """Test that Salesforce mock can be initialized"""
        try:
            from salesforce_mock.app import app
            assert app is not None
            print("✅ Salesforce mock app initialized successfully")
        except ImportError as e:
            pytest.skip(f"Salesforce mock not available: {e}")
    
    def test_salesforce_health_endpoint_logic(self):
        """Test health endpoint logic without making HTTP requests"""
        try:
            from salesforce_mock.app import app
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'healthy'
                assert 'timestamp' in data
                print("✅ Salesforce health endpoint logic works")
        except ImportError as e:
            pytest.skip(f"Salesforce mock not available: {e}")
    
    def test_salesforce_accounts_endpoint_logic(self):
        """Test accounts endpoint logic without making HTTP requests"""
        try:
            from salesforce_mock.app import app
            with patch('salesforce_mock.app.get_db_connection') as mock_db:
                # Mock database connection to return empty result
                mock_conn = Mock()
                mock_cursor = Mock()
                mock_cursor.fetchall.return_value = []
                mock_cursor.description = []
                mock_conn.cursor.return_value = mock_cursor
                mock_db.return_value = mock_conn
                
                with app.test_client() as client:
                    response = client.get('/services/data/v52.0/sobjects/Account?limit=5')
                    assert response.status_code == 200
                    data = response.get_json()
                    assert 'records' in data
                    print("✅ Salesforce accounts endpoint logic works")
        except ImportError as e:
            pytest.skip(f"Salesforce mock not available: {e}")
    
    def test_salesforce_create_account_logic(self):
        """Test create account logic without making HTTP requests"""
        try:
            from salesforce_mock.app import app
            account_data = {
                "Name": "Test Account",
                "Type": "Customer",
                "Industry": "Technology"
            }
            with app.test_client() as client:
                response = client.post('/services/data/v52.0/sobjects/Account', json=account_data)
                assert response.status_code == 201
                data = response.get_json()
                assert 'Id' in data
                print("✅ Salesforce create account logic works")
        except ImportError as e:
            pytest.skip(f"Salesforce mock not available: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
