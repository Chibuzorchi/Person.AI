# Test Data Seeding System

A comprehensive test data generation and seeding system for QuickBooks and Salesforce integrations, designed to support Person.ai's QA processes.

## 🏗️ Architecture

This system provides:
- **Realistic test data generation** using Faker
- **PostgreSQL database** for data storage
- **Mock API servers** for QuickBooks and Salesforce
- **Docker Compose** for easy deployment
- **Comprehensive test suite** for validation

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### 1. Start the System
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Seed Test Data
```bash
# Seed data using Docker
docker-compose run data-seeder

# Or run locally (after installing dependencies)
python scripts/seed_data.py
```

### 3. Test the APIs
```bash
# Run the quick demo
python scripts/quick_demo.py

# Or test individual endpoints
curl http://localhost:5000/health  # QuickBooks
curl http://localhost:5001/health  # Salesforce
```

## 📊 Generated Data

### QuickBooks Data
- **Customers**: 100 realistic business customers
- **Invoices**: 200 invoices with line items and calculations
- **Items**: 50 product/service items for invoice line items

### Salesforce Data
- **Accounts**: 50 business accounts across various industries
- **Contacts**: 200 contacts linked to accounts
- **Opportunities**: 150 sales opportunities with realistic stages

## 🔧 Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://test_user:test_password@postgres:5432/test_data

# Data volumes
CUSTOMER_COUNT=100
INVOICE_COUNT=200
ACCOUNT_COUNT=50
CONTACT_COUNT=200
OPPORTUNITY_COUNT=150
```

### Customizing Data Generation
```python
# Modify data_generators/base_factory.py
# Change seed for different data sets
factory = QuickBooksDataFactory(seed=123)

# Adjust data volumes
customers = factory.generate_customers(500)  # More customers
```

## 🧪 Testing

### Run All Tests
```bash
# Using Docker
docker-compose exec data-seeder pytest tests/ -v

# Or locally
pytest tests/ -v
```

### Test Categories
- **Data Generation**: Tests for realistic data creation
- **API Mocks**: Tests for QuickBooks and Salesforce endpoints
- **Database Seeding**: Tests for data persistence

## 📡 API Endpoints

### QuickBooks Mock (Port 5000)
```
GET  /health                           # Health check
GET  /v3/company/{id}/customers       # List customers
GET  /v3/company/{id}/invoices        # List invoices
POST /v3/company/{id}/customers       # Create customer
POST /v3/company/{id}/invoices        # Create invoice
```

### Salesforce Mock (Port 5001)
```
GET  /health                                    # Health check
GET  /services/data/v52.0/sobjects/Account     # List accounts
GET  /services/data/v52.0/sobjects/Contact     # List contacts
GET  /services/data/v52.0/sobjects/Opportunity # List opportunities
POST /services/data/v52.0/sobjects/Account     # Create account
POST /services/data/v52.0/sobjects/Contact     # Create contact
POST /services/data/v52.0/sobjects/Opportunity # Create opportunity
```

## 🗄️ Database Schema

### QuickBooks Tables
- `qb_customers`: Customer information and billing details
- `qb_invoices`: Invoices with line items and calculations

### Salesforce Tables
- `sf_accounts`: Business accounts and company information
- `sf_contacts`: Individual contacts linked to accounts
- `sf_opportunities`: Sales opportunities with stages and amounts

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/test-data-seeding.yml
name: Test Data Seeding
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: docker-compose up -d && docker-compose run data-seeder pytest tests/
```

## 🛠️ Development

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Start database only
docker-compose up -d postgres

# Run seeder locally
python scripts/seed_data.py

# Run tests
pytest tests/ -v
```

### Adding New Data Types
1. Create new factory in `data_generators/`
2. Add database table in `init.sql`
3. Update `database_seeder.py`
4. Add API endpoints in `api_mocks/`
5. Write tests in `tests/`

## 📈 Performance

### Data Volumes
- **Small**: 50 customers, 100 invoices (30 seconds)
- **Medium**: 100 customers, 200 invoices (60 seconds)
- **Large**: 500 customers, 1000 invoices (5 minutes)

### Memory Usage
- **PostgreSQL**: ~100MB for medium dataset
- **API Mocks**: ~50MB each
- **Total**: ~200MB for complete system

## 🐛 Troubleshooting

### Common Issues
1. **Database connection failed**: Check if PostgreSQL is running
2. **API endpoints not responding**: Verify Docker services are up
3. **Data not seeding**: Check database permissions and schema

### Debug Commands
```bash
# Check service logs
docker-compose logs postgres
docker-compose logs quickbooks-mock
docker-compose logs salesforce-mock

# Check database
docker-compose exec postgres psql -U test_user -d test_data -c "SELECT COUNT(*) FROM qb_customers;"

# Test API connectivity
curl -v http://localhost:5000/health
```

## 📝 License

This project is part of Person.ai's QA testing framework.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

**Built for Person.ai QA Engineering** 
