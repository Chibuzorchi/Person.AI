"""
Salesforce test data factory
"""
from typing import List, Dict, Any
from .base_factory import BaseDataFactory
import random
from decimal import Decimal
from datetime import datetime, timedelta

class SalesforceDataFactory(BaseDataFactory):
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
    
    def generate_accounts(self, count: int = 50) -> List[Dict[str, Any]]:
        """Generate Salesforce account data"""
        accounts = []
        for i in range(count):
            account = {
                'id': self._generate_id('ACC', 6),
                'name': self._generate_company_name(),
                'type': self.fake.random_element(['Customer - Direct', 'Customer - Channel', 'Prospect', 'Partner', 'Reseller']),
                'industry': self.fake.random_element([
                    'Technology', 'Healthcare', 'Financial Services', 'Manufacturing',
                    'Retail', 'Education', 'Government', 'Non-Profit'
                ]),
                'annual_revenue': round(self.fake.random.uniform(100000, 10000000), 2),
                'number_of_employees': self.fake.random.randint(10, 10000),
                'phone': self._generate_phone(),
                'website': self.fake.url(),
                'billing_address': self._generate_address(),
                'shipping_address': self._generate_address(),
                'description': self.fake.text(max_nb_chars=500) if self.fake.random.random() < 0.6 else None,
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30),
                'owner_id': self._generate_id('USER', 3),
                'is_active': self.fake.random_element([True, False])
            }
            accounts.append(account)
        
        return accounts
    
    def generate_contacts(self, count: int = 200, account_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate Salesforce contact data"""
        if not account_ids:
            account_ids = [self._generate_id('ACC', 6) for _ in range(50)]
        
        contacts = []
        for i in range(count):
            account_id = self.fake.random_element(account_ids)
            contact = {
                'id': self._generate_id('CON', 6),
                'first_name': self.fake.first_name(),
                'last_name': self.fake.last_name(),
                'email': self._generate_email(),
                'phone': self._generate_phone(),
                'mobile_phone': self._generate_phone() if self.fake.random.random() < 0.8 else None,
                'title': self.fake.job(),
                'department': self.fake.random_element([
                    'Sales', 'Marketing', 'IT', 'Finance', 'Operations',
                    'Human Resources', 'Customer Service', 'Executive'
                ]),
                'account_id': account_id,
                'account_name': self._generate_company_name(),
                'mailing_address': self._generate_address(),
                'description': self.fake.text(max_nb_chars=300) if self.fake.random.random() < 0.4 else None,
                'created_date': self._random_date_in_range(365),
                'last_modified': self._random_date_in_range(30),
                'owner_id': self._generate_id('USER', 3),
                'is_active': self.fake.random_element([True, False])
            }
            contacts.append(contact)
        
        return contacts
    
    def generate_opportunities(self, count: int = 150, account_ids: List[str] = None) -> List[Dict[str, Any]]:
        """Generate Salesforce opportunity data"""
        if not account_ids:
            account_ids = [self._generate_id('ACC', 6) for _ in range(50)]
        
        opportunities = []
        for i in range(count):
            account_id = self.fake.random_element(account_ids)
            stage_name = self.fake.random_element(self.stage_names)
            opportunity = {
                'id': self._generate_id('OPP', 6),
                'name': self._generate_opportunity_name(),
                'account_id': account_id,
                'account_name': self._generate_company_name(),
                'amount': round(self.fake.random.uniform(1000, 500000), 2),
                'stage_name': stage_name,
                'probability': self._calculate_probability(stage_name),
                'close_date': self._calculate_close_date(),
                'lead_source': self.fake.random_element(self.lead_sources),
                'type': self.fake.random_element(['New Business', 'Existing Business - Upgrade', 'Existing Business - Replacement']),
                'forecast_category': self._determine_forecast_category(stage_name),
                'description': self.fake.text(max_nb_chars=500) if self.fake.random.random() < 0.7 else None,
                'next_step': self.fake.sentence() if self.fake.random.random() < 0.5 else None,
                'created_date': self._random_date_in_range(180),
                'last_modified': self._random_date_in_range(30),
                'owner_id': self._generate_id('USER', 3),
                'is_won': stage_name == 'Closed Won',
                'is_closed': stage_name in ['Closed Won', 'Closed Lost']
            }
            opportunities.append(opportunity)
        
        return opportunities
    
    def _generate_opportunity_name(self) -> str:
        """Generate realistic opportunity names"""
        prefixes = ['New', 'Renewal', 'Expansion', 'Upgrade', 'Implementation']
        services = ['Software License', 'Consulting Services', 'Support Contract', 'Training', 'Integration']
        return f"{self.fake.random_element(prefixes)} {self.fake.random_element(services)} - {self._generate_company_name()}"
    
    def _calculate_probability(self, stage_name: str) -> int:
        """Calculate probability based on stage"""
        stage_probabilities = {
            'Prospecting': self.fake.random.randint(10, 20),
            'Qualification': self.fake.random.randint(20, 30),
            'Needs Analysis': self.fake.random.randint(30, 40),
            'Proposal/Price Quote': self.fake.random.randint(40, 60),
            'Negotiation/Review': self.fake.random.randint(60, 80),
            'Closed Won': 100,
            'Closed Lost': 0
        }
        return stage_probabilities.get(stage_name, 50)
    
    def _calculate_close_date(self) -> str:
        """Calculate realistic close date"""
        base_date = datetime.now()
        days_ahead = self.fake.random.randint(7, 180)  # 1 week to 6 months
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
