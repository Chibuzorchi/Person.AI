from flask import Flask, jsonify
import os
import time
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)

# Service configuration
SERVICE_NAME = os.getenv('SERVICE_NAME', 'integration-controller')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
START_TIME = time.time()

# Mock data for metrics and audit
request_count = 0
briefs_processed = 0
integrations_connected = 0

# Historical audit events
audit_events = [
    {
        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        "event_type": "user_login",
        "user_id": "user_123",
        "resource_id": "auth_system",
        "action": "login",
        "details": {"ip_address": "192.168.1.100", "user_agent": "Mozilla/5.0"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
        "event_type": "integration_connected",
        "user_id": "user_123",
        "resource_id": "slack_integration",
        "action": "connect",
        "details": {"integration_type": "slack", "workspace": "person-ai"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=45)).isoformat(),
        "event_type": "brief_created",
        "user_id": "user_123",
        "resource_id": "brief_456",
        "action": "create",
        "details": {"brief_type": "daily", "source_count": 5},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=20)).isoformat(),
        "event_type": "error_occurred",
        "user_id": "system",
        "resource_id": "gmail_api",
        "action": "fetch_emails",
        "details": {"error_code": "RATE_LIMIT", "retry_after": 60},
        "success": False
    }
]

def get_uptime():
    """Get service uptime in seconds"""
    return int(time.time() - START_TIME)

def get_memory_usage():
    """Get memory usage percentage"""
    return psutil.virtual_memory().percent

def get_cpu_usage():
    """Get CPU usage percentage"""
    return psutil.cpu_percent(interval=1)

def check_dependencies():
    """Check external dependencies"""
    return {
        "gmail_api": random.choice([True, True, True, False]),  # 75% success rate
        "slack_api": True,
        "quickbooks_api": random.choice([True, True, False]),  # 67% success rate
        "salesforce_api": True,
        "database": True
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health endpoint with comprehensive status"""
    dependencies = check_dependencies()
    all_healthy = all(dependencies.values())
    
    # Determine overall status
    if all_healthy:
        status = "healthy"
    elif sum(dependencies.values()) >= 3:  # At least 3 out of 5 dependencies
        status = "degraded"
    else:
        status = "unhealthy"
    
    health_data = {
        "status": status,
        "service": SERVICE_NAME,
        "version": SERVICE_VERSION,
        "uptime": get_uptime(),
        "timestamp": datetime.now().isoformat(),
        "dependencies": dependencies,
        "system": {
            "memory_usage_percent": get_memory_usage(),
            "cpu_usage_percent": get_cpu_usage(),
            "disk_usage_percent": psutil.disk_usage('/').percent
        },
        "queue_depth": random.randint(0, 10),
        "active_connections": random.randint(5, 25)
    }
    
    return jsonify(health_data), 200 if status == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus format metrics endpoint"""
    global request_count, briefs_processed, integrations_connected
    
    # Increment request count
    request_count += 1
    
    # Generate metrics in Prometheus format
    metrics_data = f"""# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{{service="{SERVICE_NAME}",method="GET",endpoint="/health"}} {request_count}
http_requests_total{{service="{SERVICE_NAME}",method="GET",endpoint="/metrics"}} {request_count}
http_requests_total{{service="{SERVICE_NAME}",method="GET",endpoint="/audit"}} {request_count // 3}

# HELP http_request_duration_seconds HTTP request duration in seconds
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.1"}} {request_count * 0.8}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.5"}} {request_count * 0.95}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="1.0"}} {request_count}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="+Inf"}} {request_count}
http_request_duration_seconds_sum{{service="{SERVICE_NAME}"}} {request_count * 0.3}
http_request_duration_seconds_count{{service="{SERVICE_NAME}"}} {request_count}

# HELP process_memory_usage_bytes Memory usage in bytes
# TYPE process_memory_usage_bytes gauge
process_memory_usage_bytes{{service="{SERVICE_NAME}"}} {psutil.Process().memory_info().rss}

# HELP process_cpu_seconds_total Total CPU time in seconds
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total{{service="{SERVICE_NAME}"}} {psutil.Process().cpu_times().user + psutil.Process().cpu_times().system}

# HELP service_uptime_seconds Service uptime in seconds
# TYPE service_uptime_seconds gauge
service_uptime_seconds{{service="{SERVICE_NAME}"}} {get_uptime()}

# HELP briefs_processed_total Total number of briefs processed
# TYPE briefs_processed_total counter
briefs_processed_total{{service="{SERVICE_NAME}"}} {briefs_processed}

# HELP integrations_connected_total Total number of integrations connected
# TYPE integrations_connected_total counter
integrations_connected_total{{service="{SERVICE_NAME}"}} {integrations_connected}

# HELP active_connections Current number of active connections
# TYPE active_connections gauge
active_connections{{service="{SERVICE_NAME}"}} {random.randint(5, 25)}

# HELP queue_depth Current queue depth
# TYPE queue_depth gauge
queue_depth{{service="{SERVICE_NAME}"}} {random.randint(0, 10)}
"""
    
    return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/audit', methods=['GET'])
def audit():
    """Audit endpoint with historical and recent events"""
    global audit_events
    
    # Add a new event occasionally
    if random.random() < 0.3:  # 30% chance
        new_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": random.choice(["user_login", "brief_created", "integration_connected", "error_occurred"]),
            "user_id": f"user_{random.randint(100, 999)}",
            "resource_id": f"resource_{random.randint(1000, 9999)}",
            "action": random.choice(["login", "create", "connect", "fetch", "process"]),
            "details": {"random_data": random.randint(1, 100)},
            "success": random.choice([True, True, True, False])  # 75% success rate
        }
        audit_events.append(new_event)
    
    # Return recent events (last 50)
    recent_events = audit_events[-50:]
    
    return jsonify({
        "service": SERVICE_NAME,
        "total_events": len(audit_events),
        "returned_events": len(recent_events),
        "events": recent_events
    }), 200

@app.route('/api/briefs', methods=['POST'])
def create_brief():
    """Simulate brief creation for audit events"""
    global briefs_processed
    briefs_processed += 1
    
    # Add audit event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "brief_created",
        "user_id": "user_123",
        "resource_id": f"brief_{briefs_processed}",
        "action": "create",
        "details": {"brief_type": "daily", "source_count": random.randint(3, 8)},
        "success": True
    }
    audit_events.append(new_event)
    
    return jsonify({"status": "success", "brief_id": f"brief_{briefs_processed}"}), 201

@app.route('/api/integrations/connect', methods=['POST'])
def connect_integration():
    """Simulate integration connection for audit events"""
    global integrations_connected
    integrations_connected += 1
    
    # Add audit event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "integration_connected",
        "user_id": "user_123",
        "resource_id": f"integration_{integrations_connected}",
        "action": "connect",
        "details": {"integration_type": "slack", "workspace": "person-ai"},
        "success": True
    }
    audit_events.append(new_event)
    
    return jsonify({"status": "success", "integration_id": f"integration_{integrations_connected}"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
