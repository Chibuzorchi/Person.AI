from flask import Flask, jsonify
import os
import time
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)

# Service configuration
SERVICE_NAME = os.getenv('SERVICE_NAME', 'content-engine')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
START_TIME = time.time()

# Mock data for metrics and audit
request_count = 0
content_generated = 0
openai_api_calls = 0

# Historical audit events
audit_events = [
    {
        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
        "event_type": "content_generated",
        "user_id": "user_123",
        "resource_id": "content_789",
        "action": "generate",
        "details": {"content_type": "daily_brief", "word_count": 450, "model": "gpt-4"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=2, minutes=15)).isoformat(),
        "event_type": "api_call",
        "user_id": "system",
        "resource_id": "openai_api",
        "action": "generate_text",
        "details": {"tokens_used": 1200, "model": "gpt-4", "cost": 0.024},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=30)).isoformat(),
        "event_type": "error_occurred",
        "user_id": "system",
        "resource_id": "openai_api",
        "action": "generate_text",
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
        "openai_api": random.choice([True, True, True, False]),  # 75% success rate
        "database": True,
        "redis_cache": random.choice([True, True, False]),  # 67% success rate
        "file_storage": True
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
        "queue_depth": random.randint(0, 5),
        "active_generations": random.randint(1, 8),
        "cache_hit_rate": random.uniform(0.7, 0.95)
    }
    
    return jsonify(health_data), 200 if status == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus format metrics endpoint"""
    global request_count, content_generated, openai_api_calls
    
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
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.1"}} {request_count * 0.6}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.5"}} {request_count * 0.9}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="1.0"}} {request_count}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="+Inf"}} {request_count}
http_request_duration_seconds_sum{{service="{SERVICE_NAME}"}} {request_count * 0.4}
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

# HELP content_generated_total Total number of content pieces generated
# TYPE content_generated_total counter
content_generated_total{{service="{SERVICE_NAME}"}} {content_generated}

# HELP openai_api_calls_total Total number of OpenAI API calls
# TYPE openai_api_calls_total counter
openai_api_calls_total{{service="{SERVICE_NAME}"}} {openai_api_calls}

# HELP active_generations Current number of active content generations
# TYPE active_generations gauge
active_generations{{service="{SERVICE_NAME}"}} {random.randint(1, 8)}

# HELP cache_hit_rate Cache hit rate
# TYPE cache_hit_rate gauge
cache_hit_rate{{service="{SERVICE_NAME}"}} {random.uniform(0.7, 0.95)}

# HELP queue_depth Current queue depth
# TYPE queue_depth gauge
queue_depth{{service="{SERVICE_NAME}"}} {random.randint(0, 5)}
"""
    
    return metrics_data, 200, {'Content-Type': 'text/plain; charset=utf-8'}

@app.route('/audit', methods=['GET'])
def audit():
    """Audit endpoint with historical and recent events"""
    global audit_events
    
    # Add a new event occasionally
    if random.random() < 0.4:  # 40% chance
        new_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": random.choice(["content_generated", "api_call", "error_occurred"]),
            "user_id": f"user_{random.randint(100, 999)}",
            "resource_id": f"content_{random.randint(1000, 9999)}",
            "action": random.choice(["generate", "cache", "process", "validate"]),
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

@app.route('/api/generate', methods=['POST'])
def generate_content():
    """Simulate content generation for audit events"""
    global content_generated, openai_api_calls
    content_generated += 1
    openai_api_calls += 1
    
    # Add audit event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "content_generated",
        "user_id": "user_123",
        "resource_id": f"content_{content_generated}",
        "action": "generate",
        "details": {"content_type": "daily_brief", "word_count": random.randint(300, 600), "model": "gpt-4"},
        "success": True
    }
    audit_events.append(new_event)
    
    return jsonify({"status": "success", "content_id": f"content_{content_generated}"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)
