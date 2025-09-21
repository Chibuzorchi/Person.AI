#!/usr/bin/env python3
"""
Simple setup test to verify the system works
"""
import sys
import os
sys.path.append('/app')

def test_imports():
    """Test that all modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from data_generators.base_factory import BaseDataFactory
        from data_generators.quickbooks_factory import QuickBooksDataFactory
        from data_generators.salesforce_factory import SalesforceDataFactory
        from data_generators.database_seeder import DatabaseSeeder
        print("   ✅ All imports successful")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_data_generation():
    """Test data generation"""
    print("🔍 Testing data generation...")
    
    try:
        from data_generators.quickbooks_factory import QuickBooksDataFactory
        from data_generators.salesforce_factory import SalesforceDataFactory
        
        # Test QuickBooks
        qb_factory = QuickBooksDataFactory(seed=42)
        customers = qb_factory.generate_customers(5)
        invoices = qb_factory.generate_invoices(5, [c['id'] for c in customers])
        
        assert len(customers) == 5
        assert len(invoices) == 5
        print("   ✅ QuickBooks data generation works")
        
        # Test Salesforce
        sf_factory = SalesforceDataFactory(seed=42)
        accounts = sf_factory.generate_accounts(5)
        contacts = sf_factory.generate_contacts(5, [a['id'] for a in accounts])
        opportunities = sf_factory.generate_opportunities(5, [a['id'] for a in accounts])
        
        assert len(accounts) == 5
        assert len(contacts) == 5
        assert len(opportunities) == 5
        print("   ✅ Salesforce data generation works")
        
        return True
    except Exception as e:
        print(f"   ❌ Data generation failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Test Data Seeding - Setup Test")
    print("=" * 40)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test data generation
    if not test_data_generation():
        success = False
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Setup test passed! System is ready.")
    else:
        print("❌ Setup test failed! Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
