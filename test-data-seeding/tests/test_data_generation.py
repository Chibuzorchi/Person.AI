"""
Test data generation tests
"""
import pytest
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Mark as Tier 2 Important and Standalone
pytestmark = [pytest.mark.tier2_important, pytest.mark.standalone]

from data_generators.quickbooks_factory import QuickBooksDataFactory
from data_generators.salesforce_factory import SalesforceDataFactory

class TestQuickBooksDataGeneration:
    def test_customer_generation(self):
        """Test QuickBooks customer data generation"""
        factory = QuickBooksDataFactory(seed=42)
        customers = factory.generate_customers(10)
        
        assert len(customers) == 10
        assert all('id' in customer for customer in customers)
        assert all('name' in customer for customer in customers)
        assert all('email' in customer for customer in customers)
        assert all(customer['id'].startswith('QB-CUST-') for customer in customers)
        assert all(customer['currency'] == 'USD' for customer in customers)
    
    def test_invoice_generation(self):
        """Test QuickBooks invoice data generation"""
        factory = QuickBooksDataFactory(seed=42)
        customers = factory.generate_customers(5)
        customer_ids = [c['id'] for c in customers]
        invoices = factory.generate_invoices(10, customer_ids)
        
        assert len(invoices) == 10
        assert all('id' in invoice for invoice in invoices)
        assert all('doc_number' in invoice for invoice in invoices)
        assert all('customer_id' in invoice for invoice in invoices)
        assert all(invoice['id'].startswith('INV-') for invoice in invoices)
        assert all(invoice['customer_id'] in customer_ids for invoice in invoices)
        assert all(invoice['total_amount'] > 0 for invoice in invoices)
    
    def test_invoice_totals_calculation(self):
        """Test invoice totals calculation"""
        factory = QuickBooksDataFactory(seed=42)
        customers = factory.generate_customers(1)
        customer_ids = [c['id'] for c in customers]
        invoices = factory.generate_invoices(1, customer_ids)
        
        invoice = invoices[0]
        assert invoice['subtotal'] > 0
        assert invoice['tax_amount'] > 0
        assert invoice['total_amount'] > 0
        assert invoice['total_amount'] == invoice['subtotal'] + invoice['tax_amount']
    
    def test_data_consistency(self):
        """Test data consistency across generations"""
        factory1 = QuickBooksDataFactory(seed=42)
        factory2 = QuickBooksDataFactory(seed=42)
        
        customers1 = factory1.generate_customers(5)
        customers2 = factory2.generate_customers(5)
        
        # Same seed should produce same data
        assert customers1[0]['name'] == customers2[0]['name']
        assert customers1[0]['email'] == customers2[0]['email']

class TestSalesforceDataGeneration:
    def test_account_generation(self):
        """Test Salesforce account data generation"""
        factory = SalesforceDataFactory(seed=42)
        accounts = factory.generate_accounts(10)
        
        assert len(accounts) == 10
        assert all('id' in account for account in accounts)
        assert all('name' in account for account in accounts)
        assert all('industry' in account for account in accounts)
        assert all(account['id'].startswith('ACC-') for account in accounts)
        assert all(account['annual_revenue'] > 0 for account in accounts)
    
    def test_contact_generation(self):
        """Test Salesforce contact data generation"""
        factory = SalesforceDataFactory(seed=42)
        accounts = factory.generate_accounts(5)
        account_ids = [a['id'] for a in accounts]
        contacts = factory.generate_contacts(10, account_ids)
        
        assert len(contacts) == 10
        assert all('id' in contact for contact in contacts)
        assert all('first_name' in contact for contact in contacts)
        assert all('last_name' in contact for contact in contacts)
        assert all('email' in contact for contact in contacts)
        assert all(contact['id'].startswith('CON-') for contact in contacts)
        assert all(contact['account_id'] in account_ids for contact in contacts)
    
    def test_opportunity_generation(self):
        """Test Salesforce opportunity data generation"""
        factory = SalesforceDataFactory(seed=42)
        accounts = factory.generate_accounts(5)
        account_ids = [a['id'] for a in accounts]
        opportunities = factory.generate_opportunities(10, account_ids)
        
        assert len(opportunities) == 10
        assert all('id' in opportunity for opportunity in opportunities)
        assert all('name' in opportunity for opportunity in opportunities)
        assert all('amount' in opportunity for opportunity in opportunities)
        assert all('stage_name' in opportunity for opportunity in opportunities)
        assert all(opportunity['id'].startswith('OPP-') for opportunity in opportunities)
        assert all(opportunity['account_id'] in account_ids for opportunity in opportunities)
        assert all(0 <= opportunity['probability'] <= 100 for opportunity in opportunities)
    
    def test_opportunity_stage_logic(self):
        """Test opportunity stage logic"""
        factory = SalesforceDataFactory(seed=42)
        accounts = factory.generate_accounts(1)
        account_ids = [a['id'] for a in accounts]
        opportunities = factory.generate_opportunities(100, account_ids)
        
        # Check that closed opportunities have correct flags
        closed_won = [opp for opp in opportunities if opp['stage_name'] == 'Closed Won']
        closed_lost = [opp for opp in opportunities if opp['stage_name'] == 'Closed Lost']
        
        assert all(opp['is_won'] for opp in closed_won)
        assert all(not opp['is_won'] for opp in closed_lost)
        assert all(opp['is_closed'] for opp in closed_won)
        assert all(opp['is_closed'] for opp in closed_lost)
    
    def test_data_consistency(self):
        """Test data consistency across generations"""
        factory1 = SalesforceDataFactory(seed=42)
        factory2 = SalesforceDataFactory(seed=42)
        
        accounts1 = factory1.generate_accounts(5)
        accounts2 = factory2.generate_accounts(5)
        
        # Same seed should produce same data
        assert accounts1[0]['name'] == accounts2[0]['name']
        assert accounts1[0]['industry'] == accounts2[0]['industry']
