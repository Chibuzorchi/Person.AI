#!/usr/bin/env python3
"""
Demo: Schema Drift Detection
This script demonstrates how contract testing catches schema changes
"""

import json
import jsonschema
from pathlib import Path

def load_contract(contract_file):
    """Load a contract from JSON file"""
    with open(contract_file, 'r') as f:
        return json.load(f)

def validate_response_against_contract(response, contract):
    """Validate a response against a contract schema"""
    try:
        jsonschema.validate(response, contract['schema'])
        return True, "✅ Schema validation passed"
    except jsonschema.ValidationError as e:
        return False, f"❌ Schema validation failed: {e.message}"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

def demo_schema_drift():
    """Demonstrate schema drift detection"""
    print("🔍 Schema Drift Detection Demo")
    print("=" * 50)
    
    # Load the contract
    contract_file = Path(__file__).parent / "contracts" / "slack_chat_postMessage_POST.json"
    contract = load_contract(contract_file)
    
    print(f"📋 Contract: {contract['endpoint']} ({contract['method']})")
    print(f"🔧 Required fields: {contract['schema']['required']}")
    print()
    
    # Test 1: Old response format (missing thread_ts)
    print("🧪 Test 1: Old Response Format (Missing thread_ts)")
    print("-" * 40)
    old_response = {
        "ok": True,
        "channel": "#test",
        "ts": "1758528870.870159",
        "message": {
            "text": "Hello from Person.ai!",
            "user": "U1234567890",
            "ts": "1758528870.870159"
        }
    }
    
    is_valid, message = validate_response_against_contract(old_response, contract)
    print(f"Response: {json.dumps(old_response, indent=2)}")
    print(f"Result: {message}")
    print()
    
    # Test 2: New response format (with thread_ts)
    print("🧪 Test 2: New Response Format (With thread_ts)")
    print("-" * 40)
    new_response = {
        "ok": True,
        "channel": "#test",
        "ts": "1758528870.870159",
        "thread_ts": "1758528870.870159",  # This field is now required
        "message": {
            "text": "Hello from Person.ai!",
            "user": "U1234567890",
            "ts": "1758528870.870159"
        }
    }
    
    is_valid, message = validate_response_against_contract(new_response, contract)
    print(f"Response: {json.dumps(new_response, indent=2)}")
    print(f"Result: {message}")
    print()
    
    # Test 3: Show what happens when we remove thread_ts from required
    print("🧪 Test 3: Contract Without thread_ts Requirement")
    print("-" * 40)
    
    # Create a modified contract without thread_ts requirement
    modified_contract = contract.copy()
    modified_contract['schema']['required'] = ["ok", "channel", "ts", "message"]
    
    is_valid, message = validate_response_against_contract(old_response, modified_contract)
    print(f"Modified contract required fields: {modified_contract['schema']['required']}")
    print(f"Old response validation: {message}")
    print()
    
    print("🎯 Summary:")
    print("This demonstrates how contract testing catches schema drift:")
    print("• When APIs change, contracts should be updated")
    print("• Old responses fail validation against new contracts")
    print("• This prevents breaking changes from reaching production")
    print("• Contract tests should run in CI/CD to catch these issues early")

if __name__ == "__main__":
    demo_schema_drift()
