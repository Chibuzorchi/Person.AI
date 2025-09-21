#!/usr/bin/env python3
"""
Standalone Bubble Frontend Tests - No Docker Required
Tests the Bubble frontend mock without requiring Docker services
"""
import pytest
import json
import sys
import os
from unittest.mock import Mock, patch

# Mark all tests in this file as standalone
pytestmark = pytest.mark.standalone

# Add the parent directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TestBubbleStandalone:
    """Test Bubble frontend mock without Docker services"""
    
    def test_api_initialization(self):
        """Test API initialization"""
        try:
            from api.app import app
            assert app is not None
            print("✅ Bubble API initialized successfully")
        except ImportError as e:
            pytest.skip(f"Bubble API not available: {e}")
    
    def test_api_health_endpoint_logic(self):
        """Test API health endpoint logic without HTTP calls"""
        try:
            from api.app import app
            with app.test_client() as client:
                response = client.get('/health')
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'healthy'
                print("✅ API health endpoint logic works")
        except ImportError as e:
            pytest.skip(f"Bubble API not available: {e}")
    
    def test_api_login_endpoint_logic(self):
        """Test API login endpoint logic without HTTP calls"""
        try:
            from api.app import app
            with app.test_client() as client:
                login_data = {
                    "email": "test@example.com",
                    "password": "testpassword"
                }
                response = client.post('/api/login', json=login_data)
                assert response.status_code == 200
                data = response.get_json()
                assert 'token' in data
                print("✅ API login endpoint logic works")
        except ImportError as e:
            pytest.skip(f"Bubble API not available: {e}")
    
    def test_api_briefings_endpoint_logic(self):
        """Test API briefings endpoint logic without HTTP calls"""
        try:
            from api.app import app
            with app.test_client() as client:
                # First login to get token
                login_data = {
                    "email": "test@example.com",
                    "password": "testpassword"
                }
                login_response = client.post('/api/login', json=login_data)
                token = login_response.get_json()['token']
                
                # Test briefings endpoint
                headers = {'Authorization': f'Bearer {token}'}
                response = client.get('/api/briefings', headers=headers)
                assert response.status_code == 200
                data = response.get_json()
                assert 'briefings' in data
                print("✅ API briefings endpoint logic works")
        except ImportError as e:
            pytest.skip(f"Bubble API not available: {e}")
    
    def test_frontend_files_exist(self):
        """Test that frontend files exist"""
        frontend_files = [
            'frontend/index.html',
            'frontend/app.js',
            'frontend/styles.css'
        ]
        
        for file_path in frontend_files:
            full_path = os.path.join(os.path.dirname(__file__), '..', file_path)
            assert os.path.exists(full_path), f"Frontend file {file_path} not found"
        
        print("✅ All frontend files exist")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
