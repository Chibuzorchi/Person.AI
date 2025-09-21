"""
QuickBooks test data factory
"""
from typing import List, Dict, Any
from .base_factory import BaseDataFactory
import random
from decimal import Decimal
from datetime import datetime, timedelta

class QuickBooksDataFactory(BaseDataFactory):
    def __init__(self, seed: int = 42):
        super().__init__(seed)
        self.item_catalog = self._generate_item_catalog()
    
    def generate_customers(self, count: int = 100) -> List[Dict[str, Any]]:
        """Generate QuickBooks customer data"""
        customers = []
        for i in range(count):
            customer = {
                'id': self._generate_id('QB-CUST', 6),
                'name': self._generate_company_name(),
                'email': self._generate_email(),
                'phone': self._generate_phone(),
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
    
    def generate_invoices(self, count: int = 200, customer_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate QuickBooks invoice data"""
        if not customer_ids:
            customer_ids = [self._generate_id('QB-CUST', 6) for _ in range(100)]
        
        invoices = []
        for i in range(count):
            customer_id = random.choice(customer_ids)
            invoice = {
                'id': self._generate_id('INV', 6),
                'doc_number': f"INV-{i+1:06d}",
                'customer_id': customer_id,
                'customer_name': self._generate_company_name(),
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
        
        return invoices
    
    def _generate_item_catalog(self) -> List[Dict[str, Any]]:
        """Generate item catalog for invoices"""
        items = []
        categories = ['Services', 'Products', 'Software', 'Consulting', 'Support']
        
        for i in range(50):
            item = {
                'id': self._generate_id('ITEM', 6),
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
                'id': self._generate_id('LINE', 6),
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
