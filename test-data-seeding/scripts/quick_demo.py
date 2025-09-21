#!/usr/bin/env python3
"""
Quick demo script to test the data seeding system
"""
import requests
import time
import json

# Configuration
QUICKBOOKS_URL = "http://localhost:5002"
SALESFORCE_URL = "http://localhost:5003"

def test_quickbooks_api():
    """Test QuickBooks API endpoints"""
    print("🔍 Testing QuickBooks API...")
    
    try:
        # Test health check
        response = requests.get(f"{QUICKBOOKS_URL}/health", timeout=10)
        print(f"   Health check: {response.status_code} - {response.json()}")
        
        # Test customers endpoint
        response = requests.get(f"{QUICKBOOKS_URL}/v3/company/123/customers?maxResults=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            customers = data.get('QueryResponse', {}).get('Customer', [])
            print(f"   Customers: Found {len(customers)} customers")
            if customers:
                print(f"   Sample customer: {customers[0]['Name']} ({customers[0]['Email']})")
        else:
            print(f"   Customers endpoint failed: {response.status_code}")
        
        # Test invoices endpoint
        response = requests.get(f"{QUICKBOOKS_URL}/v3/company/123/invoices?maxResults=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            invoices = data.get('QueryResponse', {}).get('Invoice', [])
            print(f"   Invoices: Found {len(invoices)} invoices")
            if invoices:
                print(f"   Sample invoice: {invoices[0]['DocNumber']} - ${invoices[0]['TotalAmt']}")
        else:
            print(f"   Invoices endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ QuickBooks API test failed: {e}")

def test_salesforce_api():
    """Test Salesforce API endpoints"""
    print("\n🔍 Testing Salesforce API...")
    
    try:
        # Test health check
        response = requests.get(f"{SALESFORCE_URL}/health", timeout=10)
        print(f"   Health check: {response.status_code} - {response.json()}")
        
        # Test accounts endpoint
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Account?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('records', [])
            print(f"   Accounts: Found {len(accounts)} accounts")
            if accounts:
                print(f"   Sample account: {accounts[0]['Name']} ({accounts[0]['Industry']})")
        else:
            print(f"   Accounts endpoint failed: {response.status_code}")
        
        # Test contacts endpoint
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Contact?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            contacts = data.get('records', [])
            print(f"   Contacts: Found {len(contacts)} contacts")
            if contacts:
                print(f"   Sample contact: {contacts[0]['FirstName']} {contacts[0]['LastName']} ({contacts[0]['Email']})")
        else:
            print(f"   Contacts endpoint failed: {response.status_code}")
        
        # Test opportunities endpoint
        response = requests.get(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Opportunity?limit=5", timeout=10)
        if response.status_code == 200:
            data = response.json()
            opportunities = data.get('records', [])
            print(f"   Opportunities: Found {len(opportunities)} opportunities")
            if opportunities:
                print(f"   Sample opportunity: {opportunities[0]['Name']} - ${opportunities[0]['Amount']} ({opportunities[0]['StageName']})")
        else:
            print(f"   Opportunities endpoint failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Salesforce API test failed: {e}")

def test_api_creation():
    """Test API creation endpoints"""
    print("\n🔍 Testing API creation...")
    
    try:
        # Test QuickBooks customer creation
        customer_data = {
            "Name": "Test Customer",
            "Email": "test@example.com",
            "Phone": "+1-555-0123"
        }
        response = requests.post(f"{QUICKBOOKS_URL}/v3/company/123/customers", json=customer_data, timeout=10)
        if response.status_code == 201:
            print("   ✅ QuickBooks customer creation works")
        else:
            print(f"   ❌ QuickBooks customer creation failed: {response.status_code}")
        
        # Test Salesforce account creation
        account_data = {
            "Name": "Test Account",
            "Industry": "Technology",
            "Type": "Customer - Direct"
        }
        response = requests.post(f"{SALESFORCE_URL}/services/data/v52.0/sobjects/Account", json=account_data, timeout=10)
        if response.status_code == 201:
            print("   ✅ Salesforce account creation works")
        else:
            print(f"   ❌ Salesforce account creation failed: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ API creation test failed: {e}")

def main():
    """Main demo function"""
    print("🚀 Quick Demo - Test Data Seeding System")
    print("=" * 50)
    
    # Wait for services to be ready
    print("⏳ Waiting for services to be ready...")
    time.sleep(5)
    
    # Test APIs
    test_quickbooks_api()
    test_salesforce_api()
    test_api_creation()
    
    print("\n" + "=" * 50)
    print("✅ Demo completed!")
    print("\n📝 Next steps:")
    print("   • Check the database for seeded data")
    print("   • Run the test suite: pytest tests/")
    print("   • Explore the API endpoints with curl or Postman")

if __name__ == '__main__':
    main()
