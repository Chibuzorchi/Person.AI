from flask import Flask, jsonify
import os
import time
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)

# Service configuration
SERVICE_NAME = os.getenv('SERVICE_NAME', 'delivery-gateway')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
START_TIME = time.time()

# Mock data for metrics and audit
request_count = 0
messages_delivered = 0
delivery_attempts = 0

# Historical audit events
audit_events = [
    {
        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
        "event_type": "message_delivered",
        "user_id": "user_123",
        "resource_id": "message_789",
        "action": "deliver",
        "details": {"channel": "slack", "recipient": "general", "message_type": "brief"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=3, minutes=45)).isoformat(),
        "event_type": "message_delivered",
        "user_id": "user_123",
        "resource_id": "message_790",
        "action": "deliver",
        "details": {"channel": "email", "recipient": "user@example.com", "message_type": "brief"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=25)).isoformat(),
        "event_type": "delivery_failed",
        "user_id": "system",
        "resource_id": "message_791",
        "action": "deliver",
        "details": {"channel": "sms", "recipient": "+1234567890", "error": "INVALID_NUMBER"},
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
        "slack_api": random.choice([True, True, True, False]),  # 75% success rate
        "email_smtp": True,
        "sms_provider": random.choice([True, True, False]),  # 67% success rate
        "webhook_service": True
    }

@app.route('/health', methods=['GET'])
def health_check():
    """Health endpoint with comprehensive status"""
    dependencies = check_dependencies()
    all_healthy = all(dependencies.values())
    
    # Determine overall status
    if all_healthy:
        status = "healthy"
    elif sum(dependencies.values()) >= 2:  # At least 2 out of 4 dependencies
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
        "queue_depth": random.randint(0, 8),
        "active_deliveries": random.randint(2, 12),
        "delivery_success_rate": random.uniform(0.85, 0.98)
    }
    
    return jsonify(health_data), 200 if status == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus format metrics endpoint"""
    global request_count, messages_delivered, delivery_attempts
    
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
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.1"}} {request_count * 0.7}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.5"}} {request_count * 0.9}
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

# HELP messages_delivered_total Total number of messages delivered
# TYPE messages_delivered_total counter
messages_delivered_total{{service="{SERVICE_NAME}"}} {messages_delivered}

# HELP delivery_attempts_total Total number of delivery attempts
# TYPE delivery_attempts_total counter
delivery_attempts_total{{service="{SERVICE_NAME}"}} {delivery_attempts}

# HELP active_deliveries Current number of active deliveries
# TYPE active_deliveries gauge
active_deliveries{{service="{SERVICE_NAME}"}} {random.randint(2, 12)}

# HELP delivery_success_rate Delivery success rate
# TYPE delivery_success_rate gauge
delivery_success_rate{{service="{SERVICE_NAME}"}} {random.uniform(0.85, 0.98)}

# HELP queue_depth Current queue depth
# TYPE queue_depth gauge
queue_depth{{service="{SERVICE_NAME}"}} {random.randint(0, 8)}
"""
    
    return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/audit', methods=['GET'])
def audit():
    """Audit endpoint with historical and recent events"""
    global audit_events
    
    # Add a new event occasionally
    if random.random() < 0.5:  # 50% chance
        new_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": random.choice(["message_delivered", "delivery_failed", "webhook_called"]),
            "user_id": f"user_{random.randint(100, 999)}",
            "resource_id": f"message_{random.randint(1000, 9999)}",
            "action": random.choice(["deliver", "retry", "fail", "webhook"]),
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

@app.route('/api/deliver', methods=['POST'])
def deliver_message():
    """Simulate message delivery for audit events"""
    global messages_delivered, delivery_attempts
    delivery_attempts += 1
    
    # Simulate delivery success/failure
    success = random.choice([True, True, True, False])  # 75% success rate
    
    if success:
        messages_delivered += 1
        event_type = "message_delivered"
    else:
        event_type = "delivery_failed"
    
    # Add audit event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "user_id": "user_123",
        "resource_id": f"message_{delivery_attempts}",
        "action": "deliver",
        "details": {"channel": "slack", "recipient": "general", "message_type": "brief"},
        "success": success
    }
    audit_events.append(new_event)
    
    return jsonify({"status": "success" if success else "failed", "message_id": f"message_{delivery_attempts}"}), 201 if success else 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8004, debug=True)
