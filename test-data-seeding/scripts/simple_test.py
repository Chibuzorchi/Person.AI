#!/usr/bin/env python3
"""
Simple test without database dependencies
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_generation():
    """Test data generation without database"""
    print("🔍 Testing data generation...")
    
    try:
        from data_generators.quickbooks_factory import QuickBooksDataFactory
        from data_generators.salesforce_factory import SalesforceDataFactory
        
        # Test QuickBooks
        print("   Testing QuickBooks data generation...")
        qb_factory = QuickBooksDataFactory(seed=42)
        customers = qb_factory.generate_customers(5)
        invoices = qb_factory.generate_invoices(5, [c['id'] for c in customers])
        
        assert len(customers) == 5
        assert len(invoices) == 5
        assert all('id' in customer for customer in customers)
        assert all('name' in customer for customer in customers)
        assert all('id' in invoice for invoice in invoices)
        assert all('total_amount' in invoice for invoice in invoices)
        print("   ✅ QuickBooks data generation works")
        
        # Test Salesforce
        print("   Testing Salesforce data generation...")
        sf_factory = SalesforceDataFactory(seed=42)
        accounts = sf_factory.generate_accounts(5)
        contacts = sf_factory.generate_contacts(5, [a['id'] for a in accounts])
        opportunities = sf_factory.generate_opportunities(5, [a['id'] for a in accounts])
        
        assert len(accounts) == 5
        assert len(contacts) == 5
        assert len(opportunities) == 5
        assert all('id' in account for account in accounts)
        assert all('name' in account for account in accounts)
        assert all('id' in contact for contact in contacts)
        assert all('first_name' in contact for contact in contacts)
        assert all('id' in opportunity for opportunity in opportunities)
        assert all('amount' in opportunity for opportunity in opportunities)
        print("   ✅ Salesforce data generation works")
        
        return True
    except Exception as e:
        print(f"   ❌ Data generation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Test Data Seeding - Simple Test")
    print("=" * 40)
    
    success = test_data_generation()
    
    print("\n" + "=" * 40)
    if success:
        print("✅ Simple test passed! Data generation works.")
        print("\n📝 Next steps:")
        print("   • Start the full system: docker-compose up -d")
        print("   • Run the complete test: python scripts/quick_demo.py")
    else:
        print("❌ Simple test failed! Check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    main()
