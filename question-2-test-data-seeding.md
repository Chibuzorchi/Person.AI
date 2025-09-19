# Question 2: QuickBooks & Salesforce Test Data Seeding

## Question
"Suppose we want to QA QuickBooks and Salesforce connectors, but no real customer data is available. How would you seed realistic fake datasets (e.g., invoices, opportunities, contacts) so that automated regression tests remain useful?"

## Comprehensive Answer

### Architecture Overview
I would design a comprehensive test data seeding system that generates realistic, consistent, and maintainable datasets for both QuickBooks and Salesforce, ensuring automated regression tests remain valuable and representative of real-world scenarios.

### Core Data Generation Strategy

#### 1. **Test Data Factory Framework**
```python
# test_data_factory.py
from faker import Faker
import random
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import json
import uuid

class TestDataFactory:
    def __init__(self, seed: int = 42):
        self.fake = Faker()
        self.fake.seed_instance(seed)
        random.seed(seed)
        self.generated_data = {
            'customers': [],
            'invoices': [],
            'opportunities': [],
            'contacts': [],
            'accounts': []
        }
    
    def generate_customer_base(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate base customer data for both QuickBooks and Salesforce"""
        customers = []
        for i in range(count):
            customer = {
                'id': f"CUST-{i:06d}",
                'name': self.fake.company(),
                'email': self.fake.company_email(),
                'phone': self.fake.phone_number(),
                'website': self.fake.url(),
                'billing_address': self._generate_address(),
                'shipping_address': self._generate_address(),
                'tax_id': self.fake.ssn().replace('-', ''),
                'currency': random.choice(['USD', 'EUR', 'GBP', 'CAD']),
                'payment_terms': random.choice(['Net 15', 'Net 30', 'Net 45', 'Due on Receipt']),
                'credit_limit': round(random.uniform(10000, 100000), 2),
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30)
            }
            customers.append(customer)
            self.generated_data['customers'].append(customer)
        return customers
    
    def _generate_address(self) -> Dict[str, str]:
        """Generate realistic address data"""
        return {
            'line1': self.fake.street_address(),
            'line2': self.fake.secondary_address() if random.random() < 0.3 else None,
            'city': self.fake.city(),
            'state': self.fake.state(),
            'postal_code': self.fake.postcode(),
            'country': self.fake.country_code()
        }
    
    def _random_date_in_range(self, days_back: int) -> str:
        """Generate random date within specified range"""
        start_date = datetime.now() - timedelta(days=days_back)
        random_date = start_date + timedelta(days=random.randint(0, days_back))
        return random_date.isoformat()
```

### QuickBooks Test Data Generation

#### 1. **Invoice Data Factory**
```python
# quickbooks_data_factory.py
from test_data_factory import TestDataFactory
from decimal import Decimal
import random

class QuickBooksDataFactory(TestDataFactory):
    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self.item_catalog = self._generate_item_catalog()
    
    def generate_invoices(self, count: int = 200, customer_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate realistic QuickBooks invoices"""
        if not customer_ids:
            customer_ids = [f"CUST-{i:06d}" for i in range(100)]
        
        invoices = []
        for i in range(count):
            customer_id = random.choice(customer_ids)
            invoice = {
                'id': f"INV-{i:06d}",
                'doc_number': f"INV-{i:06d}",
                'customer_id': customer_id,
                'customer_name': self._get_customer_name(customer_id),
                'due_date': self._calculate_due_date(),
                'invoice_date': self._random_date_in_range(90),
                'status': random.choice(['DRAFT', 'SENT', 'VIEWED', 'PAID', 'OVERDUE']),
                'subtotal': 0,
                'tax_amount': 0,
                'total_amount': 0,
                'balance': 0,
                'line_items': self._generate_line_items(),
                'memo': self.fake.sentence() if random.random() < 0.3 else None,
                'created_date': self._random_date_in_range(90),
                'last_modified': self._random_date_in_range(7)
            }
            
            # Calculate totals
            invoice = self._calculate_invoice_totals(invoice)
            invoices.append(invoice)
            self.generated_data['invoices'].append(invoice)
        
        return invoices
    
    def _generate_item_catalog(self) -> List[Dict[str, Any]]:
        """Generate realistic item catalog"""
        items = []
        categories = ['Services', 'Products', 'Software', 'Consulting', 'Support']
        
        for i in range(50):
            item = {
                'id': f"ITEM-{i:06d}",
                'name': self.fake.catch_phrase(),
                'description': self.fake.text(max_nb_chars=200),
                'category': random.choice(categories),
                'unit_price': round(random.uniform(10, 1000), 2),
                'cost': round(random.uniform(5, 500), 2),
                'taxable': random.choice([True, False]),
                'active': random.choice([True, False])
            }
            items.append(item)
        
        return items
    
    def _generate_line_items(self) -> List[Dict[str, Any]]:
        """Generate line items for invoice"""
        line_items = []
        num_items = random.randint(1, 10)
        
        for _ in range(num_items):
            item = random.choice(self.item_catalog)
            quantity = random.randint(1, 20)
            unit_price = item['unit_price']
            line_total = quantity * unit_price
            
            line_item = {
                'id': f"LINE-{len(line_items):06d}",
                'item_id': item['id'],
                'item_name': item['name'],
                'description': item['description'],
                'quantity': quantity,
                'unit_price': unit_price,
                'line_total': round(line_total, 2),
                'taxable': item['taxable']
            }
            line_items.append(line_item)
        
        return line_items
    
    def _calculate_invoice_totals(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate invoice totals"""
        subtotal = sum(item['line_total'] for item in invoice['line_items'])
        tax_rate = 0.08  # 8% tax rate
        tax_amount = round(subtotal * tax_rate, 2)
        total_amount = subtotal + tax_amount
        
        # Calculate balance based on status
        if invoice['status'] == 'PAID':
            balance = 0
        elif invoice['status'] == 'DRAFT':
            balance = total_amount
        else:
            balance = round(total_amount * random.uniform(0, 1), 2)
        
        invoice.update({
            'subtotal': round(subtotal, 2),
            'tax_amount': tax_amount,
            'total_amount': round(total_amount, 2),
            'balance': balance
        })
        
        return invoice
    
    def _calculate_due_date(self) -> str:
        """Calculate due date based on payment terms"""
        base_date = datetime.now()
        days_to_add = random.choice([15, 30, 45, 0])  # Common payment terms
        due_date = base_date + timedelta(days=days_to_add)
        return due_date.isoformat()
    
    def generate_customers(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate QuickBooks-specific customer data"""
        customers = []
        for i in range(count):
            customer = {
                'id': f"QB-CUST-{i:06d}",
                'name': self.fake.company(),
                'display_name': self.fake.company(),
                'email': self.fake.company_email(),
                'phone': self.fake.phone_number(),
                'website': self.fake.url(),
                'billing_address': self._generate_address(),
                'shipping_address': self._generate_address(),
                'tax_id': self.fake.ssn().replace('-', ''),
                'currency': 'USD',
                'payment_terms': random.choice(['Net 15', 'Net 30', 'Net 45', 'Due on Receipt']),
                'credit_limit': round(random.uniform(10000, 100000), 2),
                'balance': round(random.uniform(0, 50000), 2),
                'is_active': random.choice([True, False]),
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30)
            }
            customers.append(customer)
        
        return customers
```

### Salesforce Test Data Generation

#### 1. **Opportunity Data Factory**
```python
# salesforce_data_factory.py
from test_data_factory import TestDataFactory
from datetime import datetime, timedelta
import random

class SalesforceDataFactory(TestDataFactory):
    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self.stage_names = [
            'Prospecting', 'Qualification', 'Needs Analysis', 
            'Proposal/Price Quote', 'Negotiation/Review', 'Closed Won', 'Closed Lost'
        ]
        self.lead_sources = [
            'Web', 'Phone Inquiry', 'Partner Referral', 'Purchased List',
            'Other', 'Advertisement', 'Employee Referral', 'External Referral'
        ]
    
    def generate_opportunities(self, count: int = 150, account_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate realistic Salesforce opportunities"""
        if not account_ids:
            account_ids = [f"ACC-{i:06d}" for i in range(50)]
        
        opportunities = []
        for i in range(count):
            account_id = random.choice(account_ids)
            opportunity = {
                'id': f"OPP-{i:06d}",
                'name': self._generate_opportunity_name(),
                'account_id': account_id,
                'account_name': self._get_account_name(account_id),
                'amount': round(random.uniform(1000, 500000), 2),
                'stage_name': random.choice(self.stage_names),
                'probability': self._calculate_probability(random.choice(self.stage_names)),
                'close_date': self._calculate_close_date(),
                'lead_source': random.choice(self.lead_sources),
                'type': random.choice(['New Business', 'Existing Business - Upgrade', 'Existing Business - Replacement']),
                'forecast_category': self._determine_forecast_category(random.choice(self.stage_names)),
                'description': self.fake.text(max_nb_chars=500) if random.random() < 0.7 else None,
                'next_step': self.fake.sentence() if random.random() < 0.5 else None,
                'created_date': self._random_date_in_range(180),
                'last_modified': self._random_date_in_range(30),
                'owner_id': f"USER-{random.randint(1, 20):03d}",
                'is_won': random.choice([True, False]) if random.choice(self.stage_names) in ['Closed Won', 'Closed Lost'] else False,
                'is_closed': random.choice([True, False]) if random.choice(self.stage_names) in ['Closed Won', 'Closed Lost'] else False
            }
            opportunities.append(opportunity)
            self.generated_data['opportunities'].append(opportunity)
        
        return opportunities
    
    def _generate_opportunity_name(self) -> str:
        """Generate realistic opportunity names"""
        prefixes = ['New', 'Renewal', 'Expansion', 'Upgrade', 'Implementation']
        services = ['Software License', 'Consulting Services', 'Support Contract', 'Training', 'Integration']
        return f"{random.choice(prefixes)} {random.choice(services)} - {self.fake.company()}"
    
    def _calculate_probability(self, stage_name: str) -> int:
        """Calculate probability based on stage"""
        stage_probabilities = {
            'Prospecting': random.randint(10, 20),
            'Qualification': random.randint(20, 30),
            'Needs Analysis': random.randint(30, 40),
            'Proposal/Price Quote': random.randint(40, 60),
            'Negotiation/Review': random.randint(60, 80),
            'Closed Won': 100,
            'Closed Lost': 0
        }
        return stage_probabilities.get(stage_name, 50)
    
    def _calculate_close_date(self) -> str:
        """Calculate realistic close date"""
        base_date = datetime.now()
        days_ahead = random.randint(7, 180)  # 1 week to 6 months
        close_date = base_date + timedelta(days=days_ahead)
        return close_date.isoformat()
    
    def _determine_forecast_category(self, stage_name: str) -> str:
        """Determine forecast category based on stage"""
        if stage_name in ['Closed Won']:
            return 'Closed'
        elif stage_name in ['Closed Lost']:
            return 'Omitted'
        elif stage_name in ['Negotiation/Review', 'Proposal/Price Quote']:
            return 'Best Case'
        else:
            return 'Pipeline'
    
    def generate_accounts(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate Salesforce account data"""
        accounts = []
        for i in range(count):
            account = {
                'id': f"ACC-{i:06d}",
                'name': self.fake.company(),
                'type': random.choice(['Customer - Direct', 'Customer - Channel', 'Prospect', 'Partner', 'Reseller']),
                'industry': random.choice([
                    'Technology', 'Healthcare', 'Financial Services', 'Manufacturing',
                    'Retail', 'Education', 'Government', 'Non-Profit'
                ]),
                'annual_revenue': round(random.uniform(100000, 10000000), 2),
                'number_of_employees': random.randint(10, 10000),
                'phone': self.fake.phone_number(),
                'website': self.fake.url(),
                'billing_address': self._generate_address(),
                'shipping_address': self._generate_address(),
                'description': self.fake.text(max_nb_chars=500) if random.random() < 0.6 else None,
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30),
                'owner_id': f"USER-{random.randint(1, 20):03d}",
                'is_active': random.choice([True, False])
            }
            accounts.append(account)
            self.generated_data['accounts'].append(account)
        
        return accounts
    
    def generate_contacts(self, count: int = 200, account_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate Salesforce contact data"""
        if not account_ids:
            account_ids = [f"ACC-{i:06d}" for i in range(50)]
        
        contacts = []
        for i in range(count):
            account_id = random.choice(account_ids)
            contact = {
                'id': f"CON-{i:06d}",
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self.fake.email(),
                'phone': self.fake.phone_number(),
                'mobile_phone': self.fake.phone_number() if random.random() < 0.8 else None,
                'title': self.fake.job(),
                'department': random.choice([
                    'Sales', 'Marketing', 'IT', 'Finance', 'Operations',
                    'Human Resources', 'Customer Service', 'Executive'
                ]),
                'account_id': account_id,
                'account_name': self._get_account_name(account_id),
                'mailing_address': self._generate_address(),
                'description': self.fake.text(max_nb_chars=300) if random.random() < 0.4 else None,
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30),
                'owner_id': f"USER-{random.randint(1, 20):03d}",
                'is_active': random.choice([True, False])
            }
            contacts.append(contact)
            self.generated_data['contacts'].append(contact)
        
        return contacts
```

### Data Seeding Implementation

#### 1. **Database Seeding Scripts**
```python
# data_seeder.py
import json
import sqlite3
from typing import List, Dict, Any
from quickbooks_data_factory import QuickBooksDataFactory
from salesforce_data_factory import SalesforceDataFactory

class DataSeeder:
    def __init__(self, db_path: str = "test_data.db"):
        self.db_path = db_path
        self.qb_factory = QuickBooksDataFactory()
        self.sf_factory = SalesforceDataFactory()
    
    def seed_quickbooks_data(self):
        """Seed QuickBooks test data"""
        print("Generating QuickBooks test data...")
        
        # Generate customers
        customers = self.qb_factory.generate_customers(100)
        print(f"Generated {len(customers)} customers")
        
        # Generate invoices
        customer_ids = [c['id'] for c in customers]
        invoices = self.qb_factory.generate_invoices(200, customer_ids)
        print(f"Generated {len(invoices)} invoices")
        
        # Store in database
        self._store_quickbooks_data(customers, invoices)
        print("QuickBooks data seeded successfully")
    
    def seed_salesforce_data(self):
        """Seed Salesforce test data"""
        print("Generating Salesforce test data...")
        
        # Generate accounts
        accounts = self.sf_factory.generate_accounts(50)
        print(f"Generated {len(accounts)} accounts")
        
        # Generate contacts
        account_ids = [a['id'] for a in accounts]
        contacts = self.sf_factory.generate_contacts(200, account_ids)
        print(f"Generated {len(contacts)} contacts")
        
        # Generate opportunities
        opportunities = self.sf_factory.generate_opportunities(150, account_ids)
        print(f"Generated {len(opportunities)} opportunities")
        
        # Store in database
        self._store_salesforce_data(accounts, contacts, opportunities)
        print("Salesforce data seeded successfully")
    
    def _store_quickbooks_data(self, customers: List[Dict], invoices: List[Dict]):
        """Store QuickBooks data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qb_customers (
                id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                phone TEXT,
                website TEXT,
                billing_address TEXT,
                shipping_address TEXT,
                tax_id TEXT,
                currency TEXT,
                payment_terms TEXT,
                credit_limit REAL,
                balance REAL,
                is_active BOOLEAN,
                created_date TEXT,
                last_modified TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS qb_invoices (
                id TEXT PRIMARY KEY,
                doc_number TEXT,
                customer_id TEXT,
                customer_name TEXT,
                due_date TEXT,
                invoice_date TEXT,
                status TEXT,
                subtotal REAL,
                tax_amount REAL,
                total_amount REAL,
                balance REAL,
                line_items TEXT,
                memo TEXT,
                created_date TEXT,
                last_modified TEXT,
                FOREIGN KEY (customer_id) REFERENCES qb_customers (id)
            )
        ''')
        
        # Insert customers
        for customer in customers:
            cursor.execute('''
                INSERT OR REPLACE INTO qb_customers VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                INSERT OR REPLACE INTO qb_invoices VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                invoice['id'], invoice['doc_number'], invoice['customer_id'],
                invoice['customer_name'], invoice['due_date'], invoice['invoice_date'],
                invoice['status'], invoice['subtotal'], invoice['tax_amount'],
                invoice['total_amount'], invoice['balance'], json.dumps(invoice['line_items']),
                invoice['memo'], invoice['created_date'], invoice['last_modified']
            ))
        
        conn.commit()
        conn.close()
    
    def _store_salesforce_data(self, accounts: List[Dict], contacts: List[Dict], opportunities: List[Dict]):
        """Store Salesforce data in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sf_accounts (
                id TEXT PRIMARY KEY,
                name TEXT,
                type TEXT,
                industry TEXT,
                annual_revenue REAL,
                number_of_employees INTEGER,
                phone TEXT,
                website TEXT,
                billing_address TEXT,
                shipping_address TEXT,
                description TEXT,
                created_date TEXT,
                last_modified TEXT,
                owner_id TEXT,
                is_active BOOLEAN
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sf_contacts (
                id TEXT PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                email TEXT,
                phone TEXT,
                mobile_phone TEXT,
                title TEXT,
                department TEXT,
                account_id TEXT,
                account_name TEXT,
                mailing_address TEXT,
                description TEXT,
                created_date TEXT,
                last_modified TEXT,
                owner_id TEXT,
                is_active BOOLEAN,
                FOREIGN KEY (account_id) REFERENCES sf_accounts (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sf_opportunities (
                id TEXT PRIMARY KEY,
                name TEXT,
                account_id TEXT,
                account_name TEXT,
                amount REAL,
                stage_name TEXT,
                probability INTEGER,
                close_date TEXT,
                lead_source TEXT,
                type TEXT,
                forecast_category TEXT,
                description TEXT,
                next_step TEXT,
                created_date TEXT,
                last_modified TEXT,
                owner_id TEXT,
                is_won BOOLEAN,
                is_closed BOOLEAN,
                FOREIGN KEY (account_id) REFERENCES sf_accounts (id)
            )
        ''')
        
        # Insert accounts
        for account in accounts:
            cursor.execute('''
                INSERT OR REPLACE INTO sf_accounts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                INSERT OR REPLACE INTO sf_contacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                INSERT OR REPLACE INTO sf_opportunities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                opportunity['id'], opportunity['name'], opportunity['account_id'],
                opportunity['account_name'], opportunity['amount'], opportunity['stage_name'],
                opportunity['probability'], opportunity['close_date'], opportunity['lead_source'],
                opportunity['type'], opportunity['forecast_category'], opportunity['description'],
                opportunity['next_step'], opportunity['created_date'], opportunity['last_modified'],
                opportunity['owner_id'], opportunity['is_won'], opportunity['is_closed']
            ))
        
        conn.commit()
        conn.close()
```

### API Mocking for Test Data

#### 1. **QuickBooks API Mock**
```python
# quickbooks_api_mock.py
from flask import Flask, jsonify, request
import sqlite3
import json
from typing import Dict, Any, List

class QuickBooksAPIMock:
    def __init__(self, db_path: str = "test_data.db"):
        self.app = Flask(__name__)
        self.db_path = db_path
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/v3/company/<company_id>/customers', methods=['GET'])
        def get_customers(company_id):
            """Get customers endpoint"""
            customers = self._get_customers_from_db()
            return jsonify({
                "QueryResponse": {
                    "Customer": customers,
                    "maxResults": len(customers)
                }
            })
        
        @self.app.route('/v3/company/<company_id>/invoices', methods=['GET'])
        def get_invoices(company_id):
            """Get invoices endpoint"""
            invoices = self._get_invoices_from_db()
            return jsonify({
                "QueryResponse": {
                    "Invoice": invoices,
                    "maxResults": len(invoices)
                }
            })
        
        @self.app.route('/v3/company/<company_id>/invoices', methods=['POST'])
        def create_invoice(company_id):
            """Create invoice endpoint"""
            invoice_data = request.json
            # Simulate invoice creation
            new_invoice = self._create_invoice(invoice_data)
            return jsonify({
                "QueryResponse": {
                    "Invoice": [new_invoice]
                }
            })
    
    def _get_customers_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve customers from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qb_customers")
        rows = cursor.fetchall()
        conn.close()
        
        customers = []
        for row in rows:
            customers.append({
                "Id": row[0],
                "Name": row[1],
                "Email": row[2],
                "Phone": row[3],
                "Website": row[4],
                "BillAddr": json.loads(row[5]),
                "ShipAddr": json.loads(row[6]),
                "TaxIdentifier": row[7],
                "CurrencyRef": {"value": row[8]},
                "PaymentTermsRef": {"value": row[9]},
                "CreditLimit": row[10],
                "Balance": row[11],
                "Active": row[12],
                "MetaData": {
                    "CreateTime": row[13],
                    "LastUpdatedTime": row[14]
                }
            })
        
        return customers
    
    def _get_invoices_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve invoices from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM qb_invoices")
        rows = cursor.fetchall()
        conn.close()
        
        invoices = []
        for row in rows:
            invoices.append({
                "Id": row[0],
                "DocNumber": row[1],
                "CustomerRef": {"value": row[2]},
                "DueDate": row[4],
                "TxnDate": row[5],
                "TxnStatus": row[6],
                "SubTotal": row[7],
                "TotalAmt": row[9],
                "Balance": row[10],
                "Line": json.loads(row[11]),
                "PrivateNote": row[12],
                "MetaData": {
                    "CreateTime": row[13],
                    "LastUpdatedTime": row[14]
                }
            })
        
        return invoices
    
    def run(self, host='0.0.0.0', port=5000):
        """Run the mock server"""
        self.app.run(host=host, port=port, debug=True)
```

#### 2. **Salesforce API Mock**
```python
# salesforce_api_mock.py
from flask import Flask, jsonify, request
import sqlite3
import json
from typing import Dict, Any, List

class SalesforceAPIMock:
    def __init__(self, db_path: str = "test_data.db"):
        self.app = Flask(__name__)
        self.db_path = db_path
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup API routes"""
        
        @self.app.route('/services/data/v52.0/sobjects/Account', methods=['GET'])
        def get_accounts():
            """Get accounts endpoint"""
            accounts = self._get_accounts_from_db()
            return jsonify({
                "totalSize": len(accounts),
                "done": True,
                "records": accounts
            })
        
        @self.app.route('/services/data/v52.0/sobjects/Contact', methods=['GET'])
        def get_contacts():
            """Get contacts endpoint"""
            contacts = self._get_contacts_from_db()
            return jsonify({
                "totalSize": len(contacts),
                "done": True,
                "records": contacts
            })
        
        @self.app.route('/services/data/v52.0/sobjects/Opportunity', methods=['GET'])
        def get_opportunities():
            """Get opportunities endpoint"""
            opportunities = self._get_opportunities_from_db()
            return jsonify({
                "totalSize": len(opportunities),
                "done": True,
                "records": opportunities
            })
    
    def _get_accounts_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve accounts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sf_accounts")
        rows = cursor.fetchall()
        conn.close()
        
        accounts = []
        for row in rows:
            accounts.append({
                "Id": row[0],
                "Name": row[1],
                "Type": row[2],
                "Industry": row[3],
                "AnnualRevenue": row[4],
                "NumberOfEmployees": row[5],
                "Phone": row[6],
                "Website": row[7],
                "BillingAddress": json.loads(row[8]),
                "ShippingAddress": json.loads(row[9]),
                "Description": row[10],
                "CreatedDate": row[11],
                "LastModifiedDate": row[12],
                "OwnerId": row[13],
                "IsActive": row[14]
            })
        
        return accounts
    
    def _get_contacts_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve contacts from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sf_contacts")
        rows = cursor.fetchall()
        conn.close()
        
        contacts = []
        for row in rows:
            contacts.append({
                "Id": row[0],
                "FirstName": row[1],
                "LastName": row[2],
                "Email": row[3],
                "Phone": row[4],
                "MobilePhone": row[5],
                "Title": row[6],
                "Department": row[7],
                "AccountId": row[8],
                "Account": {"Name": row[9]},
                "MailingAddress": json.loads(row[10]),
                "Description": row[11],
                "CreatedDate": row[12],
                "LastModifiedDate": row[13],
                "OwnerId": row[14],
                "IsActive": row[15]
            })
        
        return contacts
    
    def _get_opportunities_from_db(self) -> List[Dict[str, Any]]:
        """Retrieve opportunities from database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sf_opportunities")
        rows = cursor.fetchall()
        conn.close()
        
        opportunities = []
        for row in rows:
            opportunities.append({
                "Id": row[0],
                "Name": row[1],
                "AccountId": row[2],
                "Account": {"Name": row[3]},
                "Amount": row[4],
                "StageName": row[5],
                "Probability": row[6],
                "CloseDate": row[7],
                "LeadSource": row[8],
                "Type": row[9],
                "ForecastCategoryName": row[10],
                "Description": row[11],
                "NextStep": row[12],
                "CreatedDate": row[13],
                "LastModifiedDate": row[14],
                "OwnerId": row[15],
                "IsWon": row[16],
                "IsClosed": row[17]
            })
        
        return opportunities
    
    def run(self, host='0.0.0.0', port=5001):
        """Run the mock server"""
        self.app.run(host=host, port=port, debug=True)
```

### Test Automation Integration

#### 1. **Regression Test Suite**
```python
# regression_tests.py
import pytest
import requests
from data_seeder import DataSeeder
from quickbooks_api_mock import QuickBooksAPIMock
from salesforce_api_mock import SalesforceAPIMock

class TestDataRegressionSuite:
    @pytest.fixture(autouse=True)
    def setup_test_data(self):
        """Setup test data before each test"""
        seeder = DataSeeder("test_regression.db")
        seeder.seed_quickbooks_data()
        seeder.seed_salesforce_data()
        
        # Start mock servers
        self.qb_mock = QuickBooksAPIMock("test_regression.db")
        self.sf_mock = SalesforceAPIMock("test_regression.db")
        
        # Run in background threads
        import threading
        qb_thread = threading.Thread(target=self.qb_mock.run, kwargs={'port': 5000})
        sf_thread = threading.Thread(target=self.sf_mock.run, kwargs={'port': 5001})
        
        qb_thread.start()
        sf_thread.start()
        
        # Wait for servers to start
        import time
        time.sleep(2)
    
    def test_quickbooks_customer_data_consistency(self):
        """Test QuickBooks customer data consistency"""
        response = requests.get("http://localhost:5000/v3/company/123/customers")
        assert response.status_code == 200
        
        data = response.json()
        customers = data["QueryResponse"]["Customer"]
        
        # Verify data consistency
        assert len(customers) > 0
        for customer in customers:
            assert "Id" in customer
            assert "Name" in customer
            assert "Email" in customer
            assert customer["Id"].startswith("QB-CUST-")
    
    def test_salesforce_opportunity_data_consistency(self):
        """Test Salesforce opportunity data consistency"""
        response = requests.get("http://localhost:5001/services/data/v52.0/sobjects/Opportunity")
        assert response.status_code == 200
        
        data = response.json()
        opportunities = data["records"]
        
        # Verify data consistency
        assert len(opportunities) > 0
        for opportunity in opportunities:
            assert "Id" in opportunity
            assert "Name" in opportunity
            assert "Amount" in opportunity
            assert "StageName" in opportunity
            assert opportunity["Id"].startswith("OPP-")
    
    def test_data_relationships(self):
        """Test data relationships between entities"""
        # Test QuickBooks invoice-customer relationship
        qb_response = requests.get("http://localhost:5000/v3/company/123/invoices")
        qb_data = qb_response.json()
        invoices = qb_data["QueryResponse"]["Invoice"]
        
        for invoice in invoices:
            customer_id = invoice["CustomerRef"]["value"]
            # Verify customer exists
            customer_response = requests.get(f"http://localhost:5000/v3/company/123/customers/{customer_id}")
            assert customer_response.status_code == 200
        
        # Test Salesforce contact-account relationship
        sf_response = requests.get("http://localhost:5001/services/data/v52.0/sobjects/Contact")
        sf_data = sf_response.json()
        contacts = sf_data["records"]
        
        for contact in contacts:
            account_id = contact["AccountId"]
            # Verify account exists
            account_response = requests.get(f"http://localhost:5001/services/data/v52.0/sobjects/Account/{account_id}")
            assert account_response.status_code == 200
```

### CI/CD Integration

#### 1. **GitHub Actions Workflow**
```yaml
# .github/workflows/test-data-regression.yml
name: Test Data Regression Suite

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test-data-regression:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio requests faker flask
    
    - name: Generate test data
      run: |
        python -c "
        from data_seeder import DataSeeder
        seeder = DataSeeder('test_data.db')
        seeder.seed_quickbooks_data()
        seeder.seed_salesforce_data()
        print('Test data generated successfully')
        "
    
    - name: Run regression tests
      run: |
        pytest tests/regression_tests.py -v --tb=short --html=regression_report.html
    
    - name: Upload test reports
      uses: actions/upload-artifact@v3
      with:
        name: regression-test-reports
        path: regression_report.html
    
    - name: Clean up test data
      if: always()
      run: |
        rm -f test_data.db test_regression.db
```

This comprehensive approach ensures that Person.ai has realistic, maintainable test data that accurately represents real-world scenarios while supporting robust automated regression testing.
