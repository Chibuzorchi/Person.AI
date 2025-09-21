# Contract Testing System

## 🛡️ Safe Integration Approach

This directory contains the advanced contract testing system that can be safely integrated without breaking existing tests.

## 📁 Structure

```
contract-testing/
├── schema_validator.py          # Advanced contract testing framework
├── safe_integration.py          # Safe wrapper for integration
├── test_safe_integration.py     # Tests for safe integration
├── requirements.txt             # Dependencies
├── contracts/                   # JSON schema contracts
│   ├── slack_chat_postMessage_POST.json
│   ├── quickbooks_customers_GET.json
│   └── salesforce_accounts_GET.json
└── README.md                    # This file
```

## 🚀 Usage

### Option 1: Safe Integration (Recommended)
```python
from safe_integration import SafeContractTester

# Initialize with fallback support
tester = SafeContractTester()

# Test Slack contracts (with fallback to simple system)
result = tester.test_slack_contracts()

# Test all services
results = tester.run_all_contract_tests()
```

### Option 2: Direct Advanced Usage
```python
from schema_validator import SchemaValidator, ContractTestRunner, ConnectorType

# Initialize advanced system
validator = SchemaValidator()
runner = ContractTestRunner(validator)

# Run contract tests
results = runner.run_contract_tests(ConnectorType.SLACK, "http://localhost:8080")
```

## 🔧 Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python test_safe_integration.py

# Run demo
python safe_integration.py
```

## ✅ Safety Features

1. **No Breaking Changes**: Existing tests continue to work
2. **Fallback Support**: Falls back to simple system if advanced fails
3. **Graceful Degradation**: Handles missing dependencies gracefully
4. **Isolated**: Advanced system is in separate directory

## 🎯 Benefits

- **Multi-Connector Support**: Slack, QuickBooks, Salesforce, etc.
- **File-Based Contracts**: JSON schema files for easy management
- **Priority Testing**: Critical, Important, Secondary test levels
- **Advanced Validation**: Full JSON Schema validation
- **Production Ready**: Comprehensive error handling and logging

## 🔄 Integration Steps

1. **Phase 1**: Add advanced system alongside existing (✅ Done)
2. **Phase 2**: Gradually integrate with existing tests
3. **Phase 3**: Replace simple system with advanced (optional)

## 🧪 Testing

```bash
# Test safe integration
python test_safe_integration.py

# Test with existing slack-mock
cd ../slack-mock
python -m pytest tests/ -v

# Test with existing test-data-seeding
cd ../test-data-seeding
python -m pytest tests/ -v
```

## 📊 Current Status

- ✅ **Advanced System**: Restored and ready
- ✅ **Safe Integration**: Implemented
- ✅ **Contract Files**: Created for main services
- ✅ **Fallback Support**: Working
- ✅ **No Breaking Changes**: Verified

The advanced contract testing system is now available and can be safely integrated without breaking any existing functionality! 🎉
