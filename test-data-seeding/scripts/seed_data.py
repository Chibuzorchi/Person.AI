#!/usr/bin/env python3
"""
Data seeding script
"""
import sys
import os
sys.path.append('/app')

from data_generators.database_seeder import DatabaseSeeder

def main():
    """Main seeding function"""
    print("🌱 Starting test data seeding...")
    
    # Get counts from environment variables or use defaults
    customer_count = int(os.getenv('CUSTOMER_COUNT', 100))
    invoice_count = int(os.getenv('INVOICE_COUNT', 200))
    account_count = int(os.getenv('ACCOUNT_COUNT', 50))
    contact_count = int(os.getenv('CONTACT_COUNT', 200))
    opportunity_count = int(os.getenv('OPPORTUNITY_COUNT', 150))
    
    # Initialize seeder
    seeder = DatabaseSeeder()
    
    # Clear existing data
    print("🗑️ Clearing existing data...")
    seeder.clear_all_data()
    
    # Seed new data
    results = seeder.seed_all_data(
        customer_count=customer_count,
        invoice_count=invoice_count,
        account_count=account_count,
        contact_count=contact_count,
        opportunity_count=opportunity_count
    )
    
    print("\n📊 Seeding Summary:")
    print(f"   • Customers: {results['customers']}")
    print(f"   • Invoices: {results['invoices']}")
    print(f"   • Accounts: {results['accounts']}")
    print(f"   • Contacts: {results['contacts']}")
    print(f"   • Opportunities: {results['opportunities']}")
    print("\n✅ Data seeding completed successfully!")

if __name__ == '__main__':
    main()
