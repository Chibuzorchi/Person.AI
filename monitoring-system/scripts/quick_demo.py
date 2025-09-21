#!/usr/bin/env python3
"""
Quick demo script for the monitoring system
Shows health, metrics, and audit endpoints for all services
"""

import requests
import time
import json
from datetime import datetime

def demo_health_endpoints(services):
    """Demo health endpoints"""
    print("🔍 Health Endpoints Demo")
    print("-" * 30)
    
    for service_name, base_url in services.items():
        try:
            response = requests.get(f"{base_url}/health", timeout=5)
            if response.status_code in [200, 503]:
                health_data = response.json()
                status_icon = "✅" if health_data['status'] == 'healthy' else "⚠️" if health_data['status'] == 'degraded' else "❌"
                print(f"{status_icon} {service_name}: {health_data['status']} (uptime: {health_data['uptime']}s)")
                print(f"   Dependencies: {sum(health_data['dependencies'].values())}/{len(health_data['dependencies'])} healthy")
                print(f"   Memory: {health_data['system']['memory_usage_percent']:.1f}%")
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: {str(e)}")
        print()

def demo_metrics_endpoints(services):
    """Demo metrics endpoints"""
    print("📊 Metrics Endpoints Demo")
    print("-" * 30)
    
    for service_name, base_url in services.items():
        try:
            response = requests.get(f"{base_url}/metrics", timeout=5)
            if response.status_code == 200:
                metrics_text = response.text
                metric_lines = [line for line in metrics_text.split('\n') if line and not line.startswith('#')]
                print(f"✅ {service_name}: {len(metric_lines)} metrics")
                
                # Show some key metrics
                for line in metric_lines[:5]:  # Show first 5 metrics
                    if ' ' in line:
                        metric_name = line.split(' ')[0].split('{')[0]
                        value = line.split(' ')[-1]
                        print(f"   {metric_name}: {value}")
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: {str(e)}")
        print()

def demo_audit_endpoints(services):
    """Demo audit endpoints"""
    print("📝 Audit Endpoints Demo")
    print("-" * 30)
    
    for service_name, base_url in services.items():
        try:
            response = requests.get(f"{base_url}/audit", timeout=5)
            if response.status_code == 200:
                audit_data = response.json()
                print(f"✅ {service_name}: {audit_data['total_events']} total events, {audit_data['returned_events']} returned")
                
                # Show recent events
                events = audit_data['events'][-3:]  # Show last 3 events
                for event in events:
                    timestamp = event['timestamp'][:19]  # Remove microseconds
                    success_icon = "✅" if event['success'] else "❌"
                    print(f"   {success_icon} {timestamp}: {event['event_type']} - {event['action']}")
            else:
                print(f"❌ {service_name}: HTTP {response.status_code}")
        except Exception as e:
            print(f"❌ {service_name}: {str(e)}")
        print()

def trigger_events(services):
    """Trigger some events to generate audit logs"""
    print("🚀 Triggering Events for Audit Demo")
    print("-" * 30)
    
    for service_name, base_url in services.items():
        try:
            if service_name == 'integration-controller':
                # Trigger brief creation
                response = requests.post(f"{base_url}/api/briefs", json={"title": "Demo Brief"})
                if response.status_code in [200, 201]:
                    print(f"✅ {service_name}: Brief created")
                
                # Trigger integration connection
                response = requests.post(f"{base_url}/api/integrations/connect", json={"type": "slack"})
                if response.status_code in [200, 201]:
                    print(f"✅ {service_name}: Integration connected")
                    
            elif service_name == 'content-engine':
                # Trigger content generation
                response = requests.post(f"{base_url}/api/generate", json={"text": "Demo content"})
                if response.status_code in [200, 201]:
                    print(f"✅ {service_name}: Content generated")
                    
            elif service_name == 'media-engine':
                # Trigger audio generation
                response = requests.post(f"{base_url}/api/generate-audio", json={"text": "Demo audio"})
                if response.status_code in [200, 201]:
                    print(f"✅ {service_name}: Audio generated")
                    
            elif service_name == 'delivery-gateway':
                # Trigger message delivery
                response = requests.post(f"{base_url}/api/deliver", json={"message": "Demo message"})
                if response.status_code in [200, 201]:
                    print(f"✅ {service_name}: Message delivered")
                    
        except Exception as e:
            print(f"❌ {service_name}: {str(e)}")
    
    print()

def main():
    """Main demo function"""
    services = {
        'integration-controller': 'http://localhost:8001',
        'content-engine': 'http://localhost:8002',
        'media-engine': 'http://localhost:8003',
        'delivery-gateway': 'http://localhost:8004'
    }
    
    print("🚀 Person.ai Monitoring System - Quick Demo")
    print("=" * 50)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Wait for services
    print("⏳ Waiting for services to be ready...")
    for service_name, base_url in services.items():
        max_retries = 15
        for attempt in range(max_retries):
            try:
                response = requests.get(f"{base_url}/health", timeout=3)
                if response.status_code in [200, 503]:
                    print(f"✅ {service_name} is ready")
                    break
            except requests.exceptions.RequestException:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    print(f"❌ {service_name} not ready")
                    return
    
    print()
    
    # Demo all endpoints
    demo_health_endpoints(services)
    demo_metrics_endpoints(services)
    demo_audit_endpoints(services)
    
    # Trigger events
    trigger_events(services)
    
    # Show updated audit logs
    print("📝 Updated Audit Logs")
    print("-" * 30)
    demo_audit_endpoints(services)
    
    print("✅ Demo completed successfully!")
    print("\n📝 Next steps:")
    print("   • Run full test suite: python scripts/run_monitoring_tests.py")
    print("   • Run pytest: pytest tests/ -v")
    print("   • Check individual endpoints: curl http://localhost:8001/health")

if __name__ == '__main__':
    main()
