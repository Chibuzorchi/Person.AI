#!/usr/bin/env python3
"""
Schema Drift Detection Integration for Monitoring System
Enhances existing monitoring-system with automated schema drift detection
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import requests

class SchemaDriftDetector:
    """Schema drift detection for monitoring system"""
    
    def __init__(self, baselines_dir: str = "schema_baselines", monitoring_interval: int = 300):
        self.baselines_dir = Path(baselines_dir)
        self.baselines_dir.mkdir(exist_ok=True)
        self.monitoring_interval = monitoring_interval
        self.baselines = self._load_baselines()
        self.drift_history = self._load_drift_history()
    
    def _load_baselines(self) -> Dict[str, Any]:
        """Load schema baselines"""
        if self.baselines_dir.exists():
            baseline_files = list(self.baselines_dir.glob("*.json"))
            baselines = {}
            for file in baseline_files:
                with open(file, 'r') as f:
                    baselines[file.stem] = json.load(f)
            return baselines
        return {}
    
    def _load_drift_history(self) -> List[Dict[str, Any]]:
        """Load drift detection history"""
        history_file = self.baselines_dir / "drift_history.json"
        if history_file.exists():
            with open(history_file, 'r') as f:
                return json.load(f)
        return []
    
    def _save_drift_history(self):
        """Save drift detection history"""
        history_file = self.baselines_dir / "drift_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.drift_history, f, indent=2)
    
    def create_baseline(self, service_name: str, endpoint: str, schema: Dict[str, Any]) -> str:
        """Create schema baseline for a service endpoint"""
        baseline_key = f"{service_name}_{endpoint.replace('/', '_')}"
        
        baseline = {
            "service_name": service_name,
            "endpoint": endpoint,
            "schema": schema,
            "created_at": datetime.now().isoformat(),
            "schema_hash": self._calculate_schema_hash(schema),
            "version": "1.0.0"
        }
        
        baseline_file = self.baselines_dir / f"{baseline_key}.json"
        with open(baseline_file, 'w') as f:
            json.dump(baseline, f, indent=2)
        
        self.baselines[baseline_key] = baseline
        return baseline_key
    
    def detect_drift(self, service_name: str, endpoint: str, current_response: Dict[str, Any]) -> Dict[str, Any]:
        """Detect schema drift by comparing current response with baseline"""
        baseline_key = f"{service_name}_{endpoint.replace('/', '_')}"
        
        if baseline_key not in self.baselines:
            # Create new baseline
            current_schema = self._extract_schema(current_response)
            self.create_baseline(service_name, endpoint, current_schema)
            
            return {
                "has_drift": False,
                "is_new_baseline": True,
                "changes": [],
                "breaking_changes": [],
                "non_breaking_changes": [],
                "drift_score": 0.0,
                "message": "New baseline created"
            }
        
        baseline = self.baselines[baseline_key]
        current_schema = self._extract_schema(current_response)
        
        # Compare schemas
        changes = self._compare_schemas(baseline["schema"], current_schema)
        breaking_changes = [c for c in changes if c["type"] == "breaking"]
        non_breaking_changes = [c for c in changes if c["type"] == "non_breaking"]
        
        has_drift = len(changes) > 0
        drift_score = len(breaking_changes) * 0.5 + len(non_breaking_changes) * 0.1
        
        # Record drift detection
        drift_record = {
            "timestamp": datetime.now().isoformat(),
            "service_name": service_name,
            "endpoint": endpoint,
            "has_drift": has_drift,
            "drift_score": drift_score,
            "breaking_changes": len(breaking_changes),
            "non_breaking_changes": len(non_breaking_changes),
            "changes": changes
        }
        
        self.drift_history.append(drift_record)
        self._save_drift_history()
        
        return {
            "has_drift": has_drift,
            "is_new_baseline": False,
            "changes": [c["description"] for c in changes],
            "breaking_changes": [c["description"] for c in breaking_changes],
            "non_breaking_changes": [c["description"] for c in non_breaking_changes],
            "drift_score": drift_score,
            "baseline_version": baseline["version"],
            "current_schema_hash": self._calculate_schema_hash(current_schema),
            "baseline_schema_hash": baseline["schema_hash"]
        }
    
    def _extract_schema(self, data: Any, path: str = "") -> Dict[str, Any]:
        """Extract schema from data structure"""
        if isinstance(data, dict):
            schema = {"type": "object", "properties": {}, "required": []}
            for key, value in data.items():
                field_path = f"{path}.{key}" if path else key
                schema["properties"][key] = self._extract_schema(value, field_path)
                schema["required"].append(key)
            return schema
        elif isinstance(data, list):
            if data:
                schema = {"type": "array", "items": self._extract_schema(data[0], f"{path}[0]")}
            else:
                schema = {"type": "array", "items": {"type": "string"}}
            return schema
        elif isinstance(data, bool):
            return {"type": "boolean"}
        elif isinstance(data, int):
            return {"type": "integer"}
        elif isinstance(data, float):
            return {"type": "number"}
        else:
            return {"type": "string"}
    
    def _compare_schemas(self, baseline_schema: Dict[str, Any], current_schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compare two schemas and identify changes"""
        changes = []
        
        # Compare types
        if baseline_schema.get("type") != current_schema.get("type"):
            changes.append({
                "type": "breaking",
                "description": f"Type changed from {baseline_schema.get('type')} to {current_schema.get('type')}"
            })
        
        # Compare object properties
        if baseline_schema.get("type") == "object" and current_schema.get("type") == "object":
            baseline_props = baseline_schema.get("properties", {})
            current_props = current_schema.get("properties", {})
            baseline_required = set(baseline_schema.get("required", []))
            current_required = set(current_schema.get("required", []))
            
            # Check for missing required fields
            missing_required = baseline_required - current_required
            for field in missing_required:
                changes.append({
                    "type": "breaking",
                    "description": f"Required field '{field}' is missing"
                })
            
            # Check for new required fields
            new_required = current_required - baseline_required
            for field in new_required:
                changes.append({
                    "type": "breaking",
                    "description": f"New required field '{field}' added"
                })
            
            # Check for removed fields
            removed_fields = set(baseline_props.keys()) - set(current_props.keys())
            for field in removed_fields:
                changes.append({
                    "type": "breaking",
                    "description": f"Field '{field}' removed"
                })
            
            # Check for new fields
            new_fields = set(current_props.keys()) - set(baseline_props.keys())
            for field in new_fields:
                changes.append({
                    "type": "non_breaking",
                    "description": f"New optional field '{field}' added"
                })
            
            # Check for type changes in existing fields
            common_fields = set(baseline_props.keys()) & set(current_props.keys())
            for field in common_fields:
                baseline_field = baseline_props[field]
                current_field = current_props[field]
                
                if baseline_field.get("type") != current_field.get("type"):
                    changes.append({
                        "type": "breaking",
                        "description": f"Field '{field}' type changed from {baseline_field.get('type')} to {current_field.get('type')}"
                    })
        
        return changes
    
    def _calculate_schema_hash(self, schema: Dict[str, Any]) -> str:
        """Calculate hash of schema for change detection"""
        schema_str = json.dumps(schema, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    def get_drift_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get drift detection summary for the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_drifts = [
            drift for drift in self.drift_history
            if datetime.fromisoformat(drift["timestamp"]) > cutoff_time
        ]
        
        total_drifts = len(recent_drifts)
        services_with_drift = len(set(drift["service_name"] for drift in recent_drifts if drift["has_drift"]))
        total_breaking_changes = sum(drift["breaking_changes"] for drift in recent_drifts)
        total_non_breaking_changes = sum(drift["non_breaking_changes"] for drift in recent_drifts)
        
        return {
            "time_period_hours": hours,
            "total_drift_checks": total_drifts,
            "services_with_drift": services_with_drift,
            "total_breaking_changes": total_breaking_changes,
            "total_non_breaking_changes": total_non_breaking_changes,
            "drift_rate": services_with_drift / max(total_drifts, 1),
            "recent_drifts": recent_drifts[-10:]  # Last 10 drift records
        }
    
    def monitor_service_endpoints(self, services: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Monitor multiple service endpoints for schema drift"""
        print(f"🔍 Monitoring {len(services)} services for schema drift...")
        
        monitoring_results = {
            "timestamp": datetime.now().isoformat(),
            "services_monitored": len(services),
            "drift_detections": [],
            "summary": {}
        }
        
        for service in services:
            service_name = service["name"]
            base_url = service["base_url"]
            endpoints = service["endpoints"]
            
            print(f"  Monitoring {service_name}...")
            
            for endpoint in endpoints:
                try:
                    # Make API call
                    url = f"{base_url}{endpoint}"
                    response = requests.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        response_data = response.json()
                        
                        # Detect drift
                        drift_result = self.detect_drift(service_name, endpoint, response_data)
                        
                        drift_record = {
                            "service_name": service_name,
                            "endpoint": endpoint,
                            "has_drift": drift_result["has_drift"],
                            "drift_score": drift_result["drift_score"],
                            "breaking_changes": len(drift_result["breaking_changes"]),
                            "non_breaking_changes": len(drift_result["non_breaking_changes"]),
                            "is_new_baseline": drift_result["is_new_baseline"]
                        }
                        
                        monitoring_results["drift_detections"].append(drift_record)
                        
                        if drift_result["has_drift"]:
                            print(f"    ⚠️  Drift detected in {endpoint}: {drift_result['drift_score']:.2f}")
                        else:
                            print(f"    ✅ No drift in {endpoint}")
                    
                    else:
                        print(f"    ❌ Failed to call {endpoint}: HTTP {response.status_code}")
                
                except Exception as e:
                    print(f"    ❌ Error monitoring {endpoint}: {str(e)}")
        
        # Calculate summary
        total_checks = len(monitoring_results["drift_detections"])
        drifts_detected = sum(1 for d in monitoring_results["drift_detections"] if d["has_drift"])
        breaking_changes = sum(d["breaking_changes"] for d in monitoring_results["drift_detections"])
        
        monitoring_results["summary"] = {
            "total_checks": total_checks,
            "drifts_detected": drifts_detected,
            "breaking_changes": breaking_changes,
            "drift_rate": drifts_detected / max(total_checks, 1)
        }
        
        return monitoring_results

def integrate_with_monitoring_system():
    """Integrate schema drift detection with existing monitoring system"""
    print("🔍 Integrating Schema Drift Detection with Monitoring System")
    print("=" * 60)
    
    detector = SchemaDriftDetector()
    
    # Define services to monitor (based on existing monitoring-system)
    services = [
        {
            "name": "integration-controller",
            "base_url": "http://localhost:8001",
            "endpoints": ["/health", "/metrics", "/audit"]
        },
        {
            "name": "content-engine",
            "base_url": "http://localhost:8002",
            "endpoints": ["/health", "/metrics", "/audit"]
        },
        {
            "name": "media-engine",
            "base_url": "http://localhost:8003",
            "endpoints": ["/health", "/metrics", "/audit"]
        },
        {
            "name": "delivery-gateway",
            "base_url": "http://localhost:8004",
            "endpoints": ["/health", "/metrics", "/audit"]
        }
    ]
    
    print(f"📊 Services to Monitor:")
    for service in services:
        print(f"  {service['name']}: {len(service['endpoints'])} endpoints")
    
    # Simulate schema drift detection
    print(f"\n🔍 Simulating Schema Drift Detection:")
    
    # Sample responses for testing
    sample_responses = {
        "integration-controller": {
            "/health": {
                "status": "healthy",
                "uptime": 3600,
                "version": "1.2.3",
                "timestamp": datetime.now().isoformat()
            },
            "/metrics": {
                "http_requests_total": 1000,
                "http_request_duration_seconds": 0.5,
                "memory_usage_bytes": 1024000
            },
            "/audit": {
                "events": [
                    {
                        "id": "evt_123",
                        "type": "user_login",
                        "timestamp": datetime.now().isoformat(),
                        "user_id": "user_456"
                    }
                ]
            }
        }
    }
    
    for service_name, endpoints in sample_responses.items():
        print(f"\n  {service_name}:")
        for endpoint, response_data in endpoints.items():
            drift_result = detector.detect_drift(service_name, endpoint, response_data)
            
            if drift_result["is_new_baseline"]:
                print(f"    {endpoint}: ✅ New baseline created")
            elif drift_result["has_drift"]:
                print(f"    {endpoint}: ⚠️  Drift detected (score: {drift_result['drift_score']:.2f})")
                if drift_result["breaking_changes"]:
                    print(f"      Breaking changes: {drift_result['breaking_changes']}")
                if drift_result["non_breaking_changes"]:
                    print(f"      Non-breaking changes: {drift_result['non_breaking_changes']}")
            else:
                print(f"    {endpoint}: ✅ No drift detected")
    
    # Show drift summary
    print(f"\n📊 Drift Detection Summary:")
    summary = detector.get_drift_summary(24)
    print(f"  Total checks: {summary['total_drift_checks']}")
    print(f"  Services with drift: {summary['services_with_drift']}")
    print(f"  Breaking changes: {summary['total_breaking_changes']}")
    print(f"  Non-breaking changes: {summary['total_non_breaking_changes']}")
    print(f"  Drift rate: {summary['drift_rate']:.2%}")
    
    print(f"\n✅ Schema Drift Detection Integration Complete!")
    print(f"   • Automated schema drift detection implemented")
    print(f"   • Baseline creation and management implemented")
    print(f"   • Breaking vs non-breaking change detection implemented")
    print(f"   • Drift history tracking implemented")
    print(f"   • Ready for CI/CD integration")

if __name__ == "__main__":
    integrate_with_monitoring_system()
