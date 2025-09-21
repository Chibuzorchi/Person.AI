"""
API mock tests
"""
import pytest
import requests
import time
import json

# Configuration
QUICKBOOKS_URL = "http://localhost:5002"
SALESFORCE_URL = "http://localhost:5003"

class TestQuickBooksMock:
    def test_health_endpoint(self):
        """Test QuickBooks health endpoint"""
        response = requests.get(f"{QUICKBOOKS_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'quickbooks-mock'
    
    def test_customers_endpoint(self):
        """Test QuickBooks customers endpoint"""
        response = requests.get(f"{QUICKBOOKS_URL}/v3/company/123/customers?maxResults=5", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'QueryResponse' in data
        assert 'Customer' in data['QueryResponse']
        customers = data['QueryResponse']['Customer']
        assert len(customers) > 0
        
        # Check customer structure
        customer = customers[0]
        assert 'Id' in customer
        assert 'Name' in customer
        assert 'Email' in customer
        assert 'MetaData' in customer
    
    def test_invoices_endpoint(self):
        """Test QuickBooks invoices endpoint"""
        response = requests.get(f"{QUICKBOOKS_URL}/v3/company/123/invoices?maxResults=5", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'QueryResponse' in data
        assert 'Invoice' in data['QueryResponse']
        invoices = data['QueryResponse']['Invoice']
        assert len(invoices) > 0
        
        # Check invoice structure
        invoice = invoices[0]
        assert 'Id' in invoice
        assert 'DocNumber' in invoice
        assert 'TotalAmt' in invoice
        assert 'MetaData' in invoice
    
    def test_create_customer(self):
        """Test QuickBooks customer creation"""
        customer_data = {
            "Name": "Test Customer",
            "Email": "test@example.com",
            "Phone": "+1-555-0123"
        }
        response = requests.post(f"{QUICKBOOKS_URL}/v3/company/123/customers", json=customer_data, timeout=10)
        assert response.status_code == 201
        data = response.json()
        assert 'QueryResponse' in data
        assert 'Customer' in data['QueryResponse']
        customer = data['QueryResponse']['Customer'][0]
        assert customer['Name'] == "Test Customer"
    
    def test_create_invoice(self):
        """Test QuickBooks invoice creation"""
        invoice_data = {
            "DocNumber": "TEST-001",
            "CustomerRef": {"value": "QB-CUST-000001"},
            "TotalAmt": 100.00
        }
        response = requests.post(f"{QUICKBOOKS_URL}/v3/company/123/invoices", json=invoice_data, timeout=10)
        assert response.status_code == 201
        data = response.json()
        assert 'QueryResponse' in data
        assert 'Invoice' in data['QueryResponse']
        invoice = data['QueryResponse']['Invoice'][0]
        assert invoice['DocNumber'] == "TEST-001"

class TestSalesforceMock:
    def test_health_endpoint(self):
        """Test Salesforce health endpoint"""
        response = requests.get(f"{SALESFORCE_URL}/health", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['service'] == 'salesforce-mock'
    
    def test_accounts_endpoint(self):
        """Test Salesforce accounts endpoint"""
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Account?limit=5", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'records' in data
        assert 'totalSize' in data
        accounts = data['records']
        assert len(accounts) > 0
        
        # Check account structure
        account = accounts[0]
        assert 'Id' in account
        assert 'Name' in account
        assert 'Industry' in account
        assert 'CreatedDate' in account
    
    def test_contacts_endpoint(self):
        """Test Salesforce contacts endpoint"""
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Contact?limit=5", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'records' in data
        contacts = data['records']
        assert len(contacts) > 0
        
        # Check contact structure
        contact = contacts[0]
        assert 'Id' in contact
        assert 'FirstName' in contact
        assert 'LastName' in contact
        assert 'Email' in contact
    
    def test_opportunities_endpoint(self):
        """Test Salesforce opportunities endpoint"""
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Opportunity?limit=5", timeout=10)
        assert response.status_code == 200
        data = response.json()
        assert 'records' in data
        opportunities = data['records']
        assert len(opportunities) > 0
        
        # Check opportunity structure
        opportunity = opportunities[0]
        assert 'Id' in opportunity
        assert 'Name' in opportunity
        assert 'Amount' in opportunity
        assert 'StageName' in opportunity
    
    def test_create_account(self):
        """Test Salesforce account creation"""
        account_data = {
            "Name": "Test Account",
            "Industry": "Technology",
            "Type": "Customer - Direct"
        }
        response = requests.post(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Account", json=account_data, timeout=10)
        assert response.status_code == 201
        data = response.json()
        assert data['Name'] == "Test Account"
        assert data['Industry'] == "Technology"
    
    def test_create_contact(self):
        """Test Salesforce contact creation"""
        contact_data = {
            "FirstName": "John",
            "LastName": "Doe",
            "Email": "john.doe@example.com",
            "Title": "Manager"
        }
        response = requests.post(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Contact", json=contact_data, timeout=10)
        assert response.status_code == 201
        data = response.json()
        assert data['FirstName'] == "John"
        assert data['LastName'] == "Doe"
    
    def test_create_opportunity(self):
        """Test Salesforce opportunity creation"""
        opportunity_data = {
            "Name": "Test Opportunity",
            "Amount": 50000,
            "StageName": "Prospecting",
            "CloseDate": "2024-12-31"
        }
        response = requests.post(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Opportunity", json=opportunity_data, timeout=10)
        assert response.status_code == 201
        data = response.json()
        assert data['Name'] == "Test Opportunity"
        assert data['Amount'] == 50000
