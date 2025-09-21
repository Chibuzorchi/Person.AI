"""
Base factory for generating realistic test data
"""
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from faker import Faker
import uuid

class BaseDataFactory:
    def __init__(self, seed: int = 42):
        self.fake = Faker()
        self.fake.seed_instance(seed)
        random.seed(seed)
        self.generated_data = {}
    
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
    
    def _generate_phone(self) -> str:
        """Generate realistic phone number"""
        return self.fake.phone_number()
    
    def _generate_email(self, domain: str = None) -> str:
        """Generate realistic email"""
        if domain:
            return f"{self.fake.user_name()}@{domain}"
        return self.fake.email()
    
    def _generate_company_name(self) -> str:
        """Generate realistic company name"""
        return self.fake.company()
    
    def _generate_id(self, prefix: str, length: int = 6) -> str:
        """Generate ID with prefix"""
        return f"{prefix}-{random.randint(10**(length-1), 10**length-1):0{length}d}"
