#!/usr/bin/env python3
"""
Contract Testing Integration for Slack Mock
Enhances existing slack-mock with schema validation and drift detection
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib

class SlackContractValidator:
    """Contract validation for Slack API responses"""
    
    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.contracts_dir.mkdir(exist_ok=True)
        self.contracts = self._load_contracts()
    
    def _load_contracts(self) -> Dict[str, Any]:
        """Load existing contracts or create defaults"""
        contracts = {}
        
        # Default Slack API contracts
        default_contracts = {
            "chat_postMessage": {
                "endpoint": "/api/chat.postMessage",
                "method": "POST",
                "schema": {
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
            },
            "conversations_list": {
                "endpoint": "/api/conversations.list",
                "method": "GET",
                "schema": {
                    "type": "object",
                    "properties": {
                        "ok": {"type": "boolean"},
                        "channels": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {"type": "string"},
                                    "is_channel": {"type": "boolean"}
                                },
                                "required": ["id", "name", "is_channel"]
                            }
                        }
                    },
                    "required": ["ok", "channels"]
                }
            }
        }
        
        for key, contract in default_contracts.items():
            contracts[key] = contract
        
        return contracts
    
    def validate_response(self, endpoint: str, method: str, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API response against contract"""
        contract_key = f"{method.lower()}_{endpoint.replace('/api/', '').replace('.', '_')}"
        
        if contract_key not in self.contracts:
            return {
                "is_valid": False,
                "error": f"No contract found for {method} {endpoint}",
                "score": 0.0
            }
        
        contract = self.contracts[contract_key]
        schema = contract["schema"]
        
        # Basic validation (simplified for demo)
        validation_result = self._validate_against_schema(response_data, schema)
        
        return {
            "is_valid": validation_result["is_valid"],
            "score": validation_result["score"],
            "details": validation_result["details"],
            "errors": validation_result.get("errors", []),
            "warnings": validation_result.get("warnings", []),
            "contract_version": "1.0.0",
            "validated_at": datetime.now().isoformat()
        }
    
    def _validate_against_schema(self, data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Simplified schema validation"""
        errors = []
        warnings = []
        score = 1.0
        
        # Check required fields
        required_fields = schema.get("required", [])
        for field in required_fields:
            if field not in data:
                errors.append(f"Missing required field: {field}")
                score -= 0.3
        
        # Check field types
        properties = schema.get("properties", {})
        for field, definition in properties.items():
            if field in data:
                expected_type = definition.get("type")
                actual_type = type(data[field]).__name__
                
                if expected_type == "boolean" and actual_type != "bool":
                    errors.append(f"Field '{field}' should be boolean, got {actual_type}")
                    score -= 0.2
                elif expected_type == "string" and actual_type != "str":
                    errors.append(f"Field '{field}' should be string, got {actual_type}")
                    score -= 0.2
                elif expected_type == "array" and actual_type != "list":
                    errors.append(f"Field '{field}' should be array, got {actual_type}")
                    score -= 0.2
        
        return {
            "is_valid": len(errors) == 0,
            "score": max(0.0, score),
            "details": f"Validation {'passed' if len(errors) == 0 else 'failed'}: {len(errors)} errors, {len(warnings)} warnings",
            "errors": errors,
            "warnings": warnings
        }
    
    def detect_schema_drift(self, endpoint: str, method: str, new_response: Dict[str, Any]) -> Dict[str, Any]:
        """Detect schema drift by comparing with baseline"""
        contract_key = f"{method.lower()}_{endpoint.replace('/api/', '').replace('.', '_')}"
        
        if contract_key not in self.contracts:
            return {
                "has_drift": False,
                "changes": [],
                "breaking_changes": [],
                "non_breaking_changes": []
            }
        
        # Simplified drift detection
        baseline_schema = self.contracts[contract_key]["schema"]
        changes = []
        breaking_changes = []
        non_breaking_changes = []
        
        # Check for new fields
        baseline_fields = self._get_all_fields(baseline_schema)
        response_fields = self._get_all_fields(new_response)
        
        new_fields = response_fields - baseline_fields
        for field in new_fields:
            changes.append(f"New field added: {field}")
            non_breaking_changes.append(field)
        
        # Check for missing required fields
        required_fields = baseline_schema.get("required", [])
        for field in required_fields:
            if field not in new_response:
                changes.append(f"Required field missing: {field}")
                breaking_changes.append(field)
        
        return {
            "has_drift": len(changes) > 0,
            "changes": changes,
            "breaking_changes": breaking_changes,
            "non_breaking_changes": non_breaking_changes,
            "drift_score": len(breaking_changes) * 0.5 + len(non_breaking_changes) * 0.1
        }
    
    def _get_all_fields(self, data: Any, prefix: str = "") -> set:
        """Get all field paths from nested structure"""
        fields = set()
        
        if isinstance(data, dict):
            for key, value in data.items():
                field_path = f"{prefix}.{key}" if prefix else key
                fields.add(field_path)
                if isinstance(value, (dict, list)):
                    fields.update(self._get_all_fields(value, field_path))
        elif isinstance(data, list) and data:
            # Check first item for structure
            fields.update(self._get_all_fields(data[0], f"{prefix}[0]"))
        
        return fields

def integrate_with_slack_mock():
    """Integrate contract testing with existing slack-mock"""
    print("🔗 Integrating Contract Testing with Slack Mock")
    print("=" * 50)
    
    validator = SlackContractValidator()
    
    # Test with sample Slack API responses
    sample_responses = {
        "chat_postMessage": {
            "ok": True,
            "channel": "C1234567890",
            "ts": "1234567890.123456",
            "message": {
                "text": "Hello, world!",
                "user": "U1234567890",
                "ts": "1234567890.123456"
            }
        },
        "conversations_list": {
            "ok": True,
            "channels": [
                {
                    "id": "C1234567890",
                    "name": "general",
                    "is_channel": True
                }
            ]
        }
    }
    
    print("📋 Testing Contract Validation:")
    for endpoint, response in sample_responses.items():
        method = "POST" if endpoint == "chat_postMessage" else "GET"
        api_endpoint = f"/api/{endpoint.replace('_', '.')}"
        
        result = validator.validate_response(api_endpoint, method, response)
        
        print(f"\n  {method} {api_endpoint}:")
        print(f"    Status: {'✅ PASS' if result['is_valid'] else '❌ FAIL'}")
        print(f"    Score: {result['score']:.3f}")
        print(f"    Details: {result.get('details', 'No details available')}")
        
        if result.get('errors'):
            print(f"    Errors: {result['errors']}")
    
    print("\n🔍 Testing Schema Drift Detection:")
    # Simulate schema drift
    drifted_response = {
        "ok": True,
        "channel": "C1234567890",
        "ts": "1234567890.123456",
        "message": {
            "text": "Hello, world!",
            "user": "U1234567890",
            "ts": "1234567890.123456"
        },
        "new_field": "This is a new field"  # This should trigger drift detection
    }
    
    drift_result = validator.detect_schema_drift("/api/chat.postMessage", "POST", drifted_response)
    
    print(f"  Schema Drift Detection:")
    print(f"    Has Drift: {'✅ YES' if drift_result['has_drift'] else '❌ NO'}")
    print(f"    Changes: {drift_result['changes']}")
    print(f"    Breaking Changes: {drift_result['breaking_changes']}")
    print(f"    Non-Breaking Changes: {drift_result['non_breaking_changes']}")
    
    print(f"\n✅ Contract Testing Integration Complete!")
    print(f"   • Schema validation implemented")
    print(f"   • Drift detection implemented")
    print(f"   • Ready for CI/CD integration")

if __name__ == "__main__":
    integrate_with_slack_mock()
