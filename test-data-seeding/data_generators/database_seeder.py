"""
Database seeder for test data
"""
import os
import psycopg2
import json
from typing import List, Dict, Any
from .quickbooks_factory import QuickBooksDataFactory
from .salesforce_factory import SalesforceDataFactory

class DatabaseSeeder:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'postgresql://test_user:test_password@localhost:5432/test_data')
        self.qb_factory = QuickBooksDataFactory()
        self.sf_factory = SalesforceDataFactory()
    
    def seed_all_data(self, customer_count: int = 100, invoice_count: int = 200, 
                     account_count: int = 50, contact_count: int = 200, opportunity_count: int = 150):
        """Seed all test data"""
        print("🌱 Starting data seeding process...")
        
        # Generate data
        print(f"📊 Generating {customer_count} customers...")
        customers = self.qb_factory.generate_customers(customer_count)
        
        print(f"📊 Generating {invoice_count} invoices...")
        customer_ids = [c['id'] for c in customers]
        invoices = self.qb_factory.generate_invoices(invoice_count, customer_ids)
        
        print(f"📊 Generating {account_count} accounts...")
        accounts = self.sf_factory.generate_accounts(account_count)
        
        print(f"📊 Generating {contact_count} contacts...")
        account_ids = [a['id'] for a in accounts]
        contacts = self.sf_factory.generate_contacts(contact_count, account_ids)
        
        print(f"📊 Generating {opportunity_count} opportunities...")
        opportunities = self.sf_factory.generate_opportunities(opportunity_count, account_ids)
        
        # Store in database
        print("💾 Storing data in database...")
        self._store_quickbooks_data(customers, invoices)
        self._store_salesforce_data(accounts, contacts, opportunities)
        
        print("✅ Data seeding completed successfully!")
        return {
            'customers': len(customers),
            'invoices': len(invoices),
            'accounts': len(accounts),
            'contacts': len(contacts),
            'opportunities': len(opportunities)
        }
    
    def _store_quickbooks_data(self, customers: List[Dict], invoices: List[Dict]):
        """Store QuickBooks data in database"""
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()
        
        try:
            # Insert customers
            for customer in customers:
                cursor.execute('''
                    INSERT INTO qb_customers 
                    (id, name, email, phone, website, billing_address, shipping_address, 
                     tax_id, currency, payment_terms, credit_limit, balance, is_active, 
                     created_date, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        website = EXCLUDED.website,
                        billing_address = EXCLUDED.billing_address,
                        shipping_address = EXCLUDED.shipping_address,
                        tax_id = EXCLUDED.tax_id,
                        currency = EXCLUDED.currency,
                        payment_terms = EXCLUDED.payment_terms,
                        credit_limit = EXCLUDED.credit_limit,
                        balance = EXCLUDED.balance,
                        is_active = EXCLUDED.is_active,
                        last_modified = EXCLUDED.last_modified
                ''', (
                    customer['id'], customer['name'], customer['email'], customer['phone'],
                    customer['website'], json.dumps(customer['billing_address']),
                    json.dumps(customer['shipping_address']), customer['tax_id'],
                    customer['currency'], customer['payment_terms'], customer['credit_limit'],
                    customer['balance'], customer['is_active'], customer['created_date'],
                    customer['last_modified']
                ))
            
            # Insert invoices
            for invoice in invoices:
                cursor.execute('''
                    INSERT INTO qb_invoices 
                    (id, doc_number, customer_id, customer_name, due_date, invoice_date,
                     status, subtotal, tax_amount, total_amount, balance, line_items, memo,
                     created_date, last_modified)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        doc_number = EXCLUDED.doc_number,
                        customer_id = EXCLUDED.customer_id,
                        customer_name = EXCLUDED.customer_name,
                        due_date = EXCLUDED.due_date,
                        invoice_date = EXCLUDED.invoice_date,
                        status = EXCLUDED.status,
                        subtotal = EXCLUDED.subtotal,
                        tax_amount = EXCLUDED.tax_amount,
                        total_amount = EXCLUDED.total_amount,
                        balance = EXCLUDED.balance,
                        line_items = EXCLUDED.line_items,
                        memo = EXCLUDED.memo,
                        last_modified = EXCLUDED.last_modified
                ''', (
                    invoice['id'], invoice['doc_number'], invoice['customer_id'],
                    invoice['customer_name'], invoice['due_date'], invoice['invoice_date'],
                    invoice['status'], invoice['subtotal'], invoice['tax_amount'],
                    invoice['total_amount'], invoice['balance'], json.dumps(invoice['line_items']),
                    invoice['memo'], invoice['created_date'], invoice['last_modified']
                ))
            
            conn.commit()
            print(f"✅ Stored {len(customers)} customers and {len(invoices)} invoices")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error storing QuickBooks data: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def _store_salesforce_data(self, accounts: List[Dict], contacts: List[Dict], opportunities: List[Dict]):
        """Store Salesforce data in database"""
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()
        
        try:
            # Insert accounts
            for account in accounts:
                cursor.execute('''
                    INSERT INTO sf_accounts 
                    (id, name, type, industry, annual_revenue, number_of_employees, phone, website,
                     billing_address, shipping_address, description, created_date, last_modified, 
                     owner_id, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        type = EXCLUDED.type,
                        industry = EXCLUDED.industry,
                        annual_revenue = EXCLUDED.annual_revenue,
                        number_of_employees = EXCLUDED.number_of_employees,
                        phone = EXCLUDED.phone,
                        website = EXCLUDED.website,
                        billing_address = EXCLUDED.billing_address,
                        shipping_address = EXCLUDED.shipping_address,
                        description = EXCLUDED.description,
                        last_modified = EXCLUDED.last_modified,
                        owner_id = EXCLUDED.owner_id,
                        is_active = EXCLUDED.is_active
                ''', (
                    account['id'], account['name'], account['type'], account['industry'],
                    account['annual_revenue'], account['number_of_employees'], account['phone'],
                    account['website'], json.dumps(account['billing_address']),
                    json.dumps(account['shipping_address']), account['description'],
                    account['created_date'], account['last_modified'], account['owner_id'],
                    account['is_active']
                ))
            
            # Insert contacts
            for contact in contacts:
                cursor.execute('''
                    INSERT INTO sf_contacts 
                    (id, first_name, last_name, email, phone, mobile_phone, title, department,
                     account_id, account_name, mailing_address, description, created_date, 
                     last_modified, owner_id, is_active)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        email = EXCLUDED.email,
                        phone = EXCLUDED.phone,
                        mobile_phone = EXCLUDED.mobile_phone,
                        title = EXCLUDED.title,
                        department = EXCLUDED.department,
                        account_id = EXCLUDED.account_id,
                        account_name = EXCLUDED.account_name,
                        mailing_address = EXCLUDED.mailing_address,
                        description = EXCLUDED.description,
                        last_modified = EXCLUDED.last_modified,
                        owner_id = EXCLUDED.owner_id,
                        is_active = EXCLUDED.is_active
                ''', (
                    contact['id'], contact['first_name'], contact['last_name'],
                    contact['email'], contact['phone'], contact['mobile_phone'],
                    contact['title'], contact['department'], contact['account_id'],
                    contact['account_name'], json.dumps(contact['mailing_address']),
                    contact['description'], contact['created_date'], contact['last_modified'],
                    contact['owner_id'], contact['is_active']
                ))
            
            # Insert opportunities
            for opportunity in opportunities:
                cursor.execute('''
                    INSERT INTO sf_opportunities 
                    (id, name, account_id, account_name, amount, stage_name, probability, close_date,
                     lead_source, type, forecast_category, description, next_step, created_date,
                     last_modified, owner_id, is_won, is_closed)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        name = EXCLUDED.name,
                        account_id = EXCLUDED.account_id,
                        account_name = EXCLUDED.account_name,
                        amount = EXCLUDED.amount,
                        stage_name = EXCLUDED.stage_name,
                        probability = EXCLUDED.probability,
                        close_date = EXCLUDED.close_date,
                        lead_source = EXCLUDED.lead_source,
                        type = EXCLUDED.type,
                        forecast_category = EXCLUDED.forecast_category,
                        description = EXCLUDED.description,
                        next_step = EXCLUDED.next_step,
                        last_modified = EXCLUDED.last_modified,
                        owner_id = EXCLUDED.owner_id,
                        is_won = EXCLUDED.is_won,
                        is_closed = EXCLUDED.is_closed
                ''', (
                    opportunity['id'], opportunity['name'], opportunity['account_id'],
                    opportunity['account_name'], opportunity['amount'], opportunity['stage_name'],
                    opportunity['probability'], opportunity['close_date'], opportunity['lead_source'],
                    opportunity['type'], opportunity['forecast_category'], opportunity['description'],
                    opportunity['next_step'], opportunity['created_date'], opportunity['last_modified'],
                    opportunity['owner_id'], opportunity['is_won'], opportunity['is_closed']
                ))
            
            conn.commit()
            print(f"✅ Stored {len(accounts)} accounts, {len(contacts)} contacts, and {len(opportunities)} opportunities")
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Error storing Salesforce data: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def clear_all_data(self):
        """Clear all test data"""
        conn = psycopg2.connect(self.database_url)
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM qb_invoices")
            cursor.execute("DELETE FROM qb_customers")
            cursor.execute("DELETE FROM sf_opportunities")
            cursor.execute("DELETE FROM sf_contacts")
            cursor.execute("DELETE FROM sf_accounts")
            conn.commit()
            print("🗑️ All test data cleared")
        except Exception as e:
            conn.rollback()
            print(f"❌ Error clearing data: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
