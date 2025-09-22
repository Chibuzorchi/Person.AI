#!/usr/bin/env python3
"""
Contract-First Testing Framework for Middleware Connectors
Implements schema validation, drift detection, and contract testing for Apideck, Merge, Paragon
"""

import json
import jsonschema
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
import yaml
from pathlib import Path

class ConnectorType(Enum):
    APIDECK = "apideck"
    MERGE = "merge"
    PARAGON = "paragon"
    SLACK = "slack"
    QUICKBOOKS = "quickbooks"
    SALESFORCE = "salesforce"
    NOTION = "notion"

class Priority(Enum):
    CRITICAL = "critical"      # Test on every run
    IMPORTANT = "important"    # Test on schema changes + nightly
    SECONDARY = "secondary"    # Test weekly/rotating

@dataclass
class SchemaContract:
    connector_type: ConnectorType
    endpoint: str
    method: str
    schema: Dict[str, Any]
    version: str
    last_updated: datetime
    priority: Priority
    breaking_changes: List[str]
    non_breaking_changes: List[str]

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    breaking_changes: List[str]
    non_breaking_changes: List[str]
    response_time: float
    schema_hash: str

class SchemaValidator:
    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.contracts_dir.mkdir(exist_ok=True)
        self.contracts: Dict[str, SchemaContract] = {}
        self.load_contracts()
    
    def load_contracts(self):
        """Load all schema contracts from files"""
        for contract_file in self.contracts_dir.glob("*.json"):
            try:
                with open(contract_file, 'r') as f:
                    data = json.load(f)
                
                contract = SchemaContract(
                    connector_type=ConnectorType(data['connector_type']),
                    endpoint=data['endpoint'],
                    method=data['method'],
                    schema=data['schema'],
                    version=data['version'],
                    last_updated=datetime.fromisoformat(data['last_updated']),
                    priority=Priority(data['priority']),
                    breaking_changes=data.get('breaking_changes', []),
                    non_breaking_changes=data.get('non_breaking_changes', [])
                )
                
                key = f"{contract.connector_type.value}_{contract.endpoint}_{contract.method}"
                self.contracts[key] = contract
                
            except Exception as e:
                print(f"Error loading contract {contract_file}: {e}")
    
    def create_contract(self, connector_type: ConnectorType, endpoint: str, 
                       method: str, schema: Dict[str, Any], priority: Priority) -> str:
        """Create a new schema contract"""
        contract = SchemaContract(
            connector_type=connector_type,
            endpoint=endpoint,
            method=method,
            schema=schema,
            version="1.0.0",
            last_updated=datetime.now(),
            priority=priority,
            breaking_changes=[],
            non_breaking_changes=[]
        )
        
        # Save contract to file
        contract_data = {
            'connector_type': connector_type.value,
            'endpoint': endpoint,
            'method': method,
            'schema': schema,
            'version': contract.version,
            'last_updated': contract.last_updated.isoformat(),
            'priority': priority.value,
            'breaking_changes': contract.breaking_changes,
            'non_breaking_changes': contract.non_breaking_changes
        }
        
        filename = f"{connector_type.value}_{endpoint.replace('/', '_')}_{method}.json"
        filepath = self.contracts_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(contract_data, f, indent=2)
        
        key = f"{connector_type.value}_{endpoint}_{method}"
        self.contracts[key] = contract
        
        return str(filepath)
    
    def validate_response(self, connector_type: ConnectorType, endpoint: str, 
                         method: str, response_data: Dict[str, Any]) -> ValidationResult:
        """Validate API response against schema contract"""
        key = f"{connector_type.value}_{endpoint}_{method}"
        
        if key not in self.contracts:
            return ValidationResult(
                is_valid=False,
                errors=[f"No contract found for {connector_type.value} {method} {endpoint}"],
                warnings=[],
                breaking_changes=[],
                non_breaking_changes=[],
                response_time=0.0,
                schema_hash=""
            )
        
        contract = self.contracts[key]
        start_time = time.time()
        
        try:
            # Validate against JSON schema
            jsonschema.validate(response_data, contract.schema)
            
            # Check for breaking changes
            breaking_changes = self._detect_breaking_changes(contract, response_data)
            breaking_changes.extend(self._detect_breaking_changes_new_fields(contract, response_data))  

            non_breaking_changes = self._detect_non_breaking_changes(contract, response_data)
            non_breaking_changes.extend(self._detect_non_breaking_changes_new_fields(contract, response_data))  
            
            response_time = time.time() - start_time
            schema_hash = self._calculate_schema_hash(contract.schema)
            
            return ValidationResult(
                is_valid=True,
                errors=[],
                warnings=non_breaking_changes,
                breaking_changes=breaking_changes,
                non_breaking_changes=non_breaking_changes,
                response_time=response_time,
                schema_hash=schema_hash
            )
            
        except jsonschema.ValidationError as e:
            response_time = time.time() - start_time
            return ValidationResult(
                is_valid=False,
                errors=[f"Schema validation failed: {e.message}"],
                warnings=[],
                breaking_changes=[],
                non_breaking_changes=[],
                response_time=response_time,
                schema_hash=""
            )
        except Exception as e:
            response_time = time.time() - start_time
            return ValidationResult(
                is_valid=False,
                errors=[f"Validation error: {str(e)}"],
                warnings=[],
                breaking_changes=[],
                non_breaking_changes=[],
                response_time=response_time,
                schema_hash=""
            )
    
    def _detect_breaking_changes(self, contract: SchemaContract, response_data: Dict[str, Any]) -> List[str]:
        """Detect breaking changes in API response"""
        breaking_changes = []
        
        # Check for missing required fields
        required_fields = self._get_required_fields(contract.schema)
        for field in required_fields:
            if not self._field_exists(response_data, field):
                breaking_changes.append(f"Missing required field: {field}")
        
        # Check for type changes
        for field, expected_type in self._get_field_types(contract.schema).items():
            if self._field_exists(response_data, field):
                actual_value = self._get_field_value(response_data, field)
                if not self._is_correct_type(actual_value, expected_type):
                    breaking_changes.append(f"Type change in field {field}: expected {expected_type}, got {type(actual_value).__name__}")
        
        return breaking_changes
    
    def _detect_non_breaking_changes(self, contract: SchemaContract, response_data: Dict[str, Any]) -> List[str]:
        """Detect non-breaking changes (new fields, etc.)"""
        non_breaking_changes = []
        
        # Check for new fields
        schema_fields = self._get_all_fields(contract.schema)
        response_fields = self._get_all_fields(response_data)
        
        new_fields = response_fields - schema_fields
        for field in new_fields:
            non_breaking_changes.append(f"New field added: {field}")
            # breaking_changes.append(f"New field added: {field}")
        
        return non_breaking_changes


    def _detect_breaking_changes_new_fields(self, contract: SchemaContract, response_data: Dict[str, Any]) -> List[str]:
        """Detect breaking changes for new fields (toggleable)"""
        breaking_changes = []
        
        # Check for new fields
        schema_fields = self._get_all_fields(contract.schema)
        response_fields = self._get_all_fields(response_data)
        
        new_fields = response_fields - schema_fields
        for field in new_fields:
            breaking_changes.append(f"New field added: {field}") 
        
        return breaking_changes


    def _detect_non_breaking_changes_new_fields(self, contract: SchemaContract, response_data: Dict[str, Any]) -> List[str]:
        """Detect non-breaking changes for new fields (toggleable)"""
        non_breaking_changes = []
        
        # Check for new fields
        schema_fields = self._get_all_fields(contract.schema)
        response_fields = self._get_all_fields(response_data)
        
        new_fields = response_fields - schema_fields
        for field in new_fields:
            non_breaking_changes.append(f"New field added: {field}") 
        
        return non_breaking_changes  

    
    def _get_required_fields(self, schema: Dict[str, Any]) -> List[str]:
        """Extract required fields from JSON schema"""
        if 'properties' in schema and 'required' in schema:
            return schema['required']
        return []
    
    def _get_field_types(self, schema: Dict[str, Any]) -> Dict[str, str]:
        """Extract field types from JSON schema"""
        field_types = {}
        if 'properties' in schema:
            for field, definition in schema['properties'].items():
                if 'type' in definition:
                    field_types[field] = definition['type']
        return field_types
    
    def _get_all_fields(self, data: Dict[str, Any], prefix: str = "") -> set:
        """Get all field paths from nested dictionary"""
        fields = set()
        for key, value in data.items():
            field_path = f"{prefix}.{key}" if prefix else key
            fields.add(field_path)
            if isinstance(value, dict):
                fields.update(self._get_all_fields(value, field_path))
        return fields
    
    def _field_exists(self, data: Dict[str, Any], field_path: str) -> bool:
        """Check if field exists in nested dictionary"""
        try:
            self._get_field_value(data, field_path)
            return True
        except KeyError:
            return False
    
    def _get_field_value(self, data: Dict[str, Any], field_path: str) -> Any:
        """Get value from nested dictionary using dot notation"""
        keys = field_path.split('.')
        value = data
        for key in keys:
            value = value[key]
        return value
    
    def _is_correct_type(self, value: Any, expected_type: str) -> bool:
        """Check if value matches expected type"""
        type_mapping = {
            'string': str,
            'integer': int,
            'number': (int, float),
            'boolean': bool,
            'array': list,
            'object': dict
        }
        
        if expected_type in type_mapping:
            expected_python_type = type_mapping[expected_type]
            if isinstance(expected_python_type, tuple):
                return isinstance(value, expected_python_type)
            return isinstance(value, expected_python_type)
        
        return True  # Unknown type, assume valid
    
    def _calculate_schema_hash(self, schema: Dict[str, Any]) -> str:
        """Calculate hash of schema for change detection"""
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()

class ContractTestRunner:
    def __init__(self, validator: SchemaValidator):
        self.validator = validator
        self.results: Dict[str, List[ValidationResult]] = {}
    
    def run_contract_tests(self, connector_type: ConnectorType, 
                          base_url: str, priority_filter: Optional[Priority] = None) -> Dict[str, Any]:
        """Run contract tests for a specific connector"""
        print(f"🔍 Running contract tests for {connector_type.value}")
        
        test_results = {
            'connector_type': connector_type.value,
            'total_tests': 0,
            'passed': 0,
            'failed': 0,
            'breaking_changes': 0,
            'non_breaking_changes': 0,
            'response_times': [],
            'errors': []
        }
        
        # Filter contracts by priority if specified
        contracts_to_test = []
        for contract in self.validator.contracts.values():
            if contract.connector_type == connector_type:
                if priority_filter is None or contract.priority == priority_filter:
                    contracts_to_test.append(contract)
        
        for contract in contracts_to_test:
            print(f"  Testing {contract.method} {contract.endpoint}")
            
            try:
                # Make actual API call
                url = f"{base_url}{contract.endpoint}"
                response = requests.request(
                    method=contract.method,
                    url=url,
                    timeout=30
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    # Validate response
                    validation_result = self.validator.validate_response(
                        contract.connector_type,
                        contract.endpoint,
                        contract.method,
                        response_data
                    )
                    
                    test_results['total_tests'] += 1
                    test_results['response_times'].append(validation_result.response_time)
                    
                    if validation_result.is_valid:
                        test_results['passed'] += 1
                        print(f"    ✅ PASS")
                    else:
                        test_results['failed'] += 1
                        test_results['errors'].extend(validation_result.errors)
                        print(f"    ❌ FAIL: {validation_result.errors[0]}")
                    
                    # Track changes
                    test_results['breaking_changes'] += len(validation_result.breaking_changes)
                    test_results['non_breaking_changes'] += len(validation_result.non_breaking_changes)
                    
                    if validation_result.breaking_changes:
                        print(f"    ⚠️  Breaking changes: {validation_result.breaking_changes}")
                    
                    if validation_result.non_breaking_changes:
                        print(f"    ℹ️  Non-breaking changes: {validation_result.non_breaking_changes}")
                
                else:
                    test_results['total_tests'] += 1
                    test_results['failed'] += 1
                    error_msg = f"HTTP {response.status_code}: {response.text}"
                    test_results['errors'].append(error_msg)
                    print(f"    ❌ FAIL: {error_msg}")
            
            except Exception as e:
                test_results['total_tests'] += 1
                test_results['failed'] += 1
                error_msg = f"Request failed: {str(e)}"
                test_results['errors'].append(error_msg)
                print(f"    ❌ FAIL: {error_msg}")
        
        # Calculate average response time
        if test_results['response_times']:
            test_results['avg_response_time'] = sum(test_results['response_times']) / len(test_results['response_times'])
        else:
            test_results['avg_response_time'] = 0.0
        
        return test_results

def create_sample_contracts():
    """Create sample schema contracts for testing"""
    validator = SchemaValidator()
    
    # Slack contract
    slack_schema = {
        "type": "object",
        "properties": {
            "ok": {"type": "boolean"},
            "channel": {"type": "string"},
            "ts": {"type": "string"},
            "message": {
                "type": "object",
                "properties": {
                    "text": {"type": "string"},
                    "user": {"type": "string"},
                    "ts": {"type": "string"}
                },
                "required": ["text", "user", "ts"]
            }
        },
        "required": ["ok", "channel", "ts", "message"]
    }
    
    validator.create_contract(
        ConnectorType.SLACK,
        "/api/chat.postMessage",
        "POST",
        slack_schema,
        Priority.CRITICAL
    )
    
    # QuickBooks contract
    qb_schema = {
        "type": "object",
        "properties": {
            "QueryResponse": {
                "type": "object",
                "properties": {
                    "Customer": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Id": {"type": "string"},
                                "Name": {"type": "string"},
                                "Email": {"type": "string"},
                                "Balance": {"type": "number"}
                            },
                            "required": ["Id", "Name", "Email"]
                        }
                    }
                },
                "required": ["Customer"]
            }
        },
        "required": ["QueryResponse"]
    }
    
    validator.create_contract(
        ConnectorType.QUICKBOOKS,
        "/v3/company/123/customers",
        "GET",
        qb_schema,
        Priority.CRITICAL
    )
    
    # Salesforce contract
    sf_schema = {
        "type": "object",
        "properties": {
            "totalSize": {"type": "integer"},
            "done": {"type": "boolean"},
            "records": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "Id": {"type": "string"},
                        "Name": {"type": "string"},
                        "Type": {"type": "string"},
                        "Industry": {"type": "string"}
                    },
                    "required": ["Id", "Name"]
                }
            }
        },
        "required": ["totalSize", "done", "records"]
    }
    
    validator.create_contract(
        ConnectorType.SALESFORCE,
        "/services/data/v52.0/query",
        "GET",
        sf_schema,
        Priority.CRITICAL
    )
    
    print("✅ Sample contracts created successfully")

if __name__ == "__main__":
    # Create sample contracts
    create_sample_contracts()
    
    # Test the validator
    validator = SchemaValidator()
    runner = ContractTestRunner(validator)
    
    print("\n🚀 Running contract tests...")
    
    # Test Slack (if available)
    try:
        slack_results = runner.run_contract_tests(ConnectorType.SLACK, "http://localhost:8080")
        print(f"\n📊 Slack Results: {slack_results['passed']}/{slack_results['total_tests']} passed")
    except Exception as e:
        print(f"Slack tests skipped: {e}")
    
    # Test QuickBooks (if available)
    try:
        qb_results = runner.run_contract_tests(ConnectorType.QUICKBOOKS, "http://localhost:5000")
        print(f"\n📊 QuickBooks Results: {qb_results['passed']}/{qb_results['total_tests']} passed")
    except Exception as e:
        print(f"QuickBooks tests skipped: {e}")
