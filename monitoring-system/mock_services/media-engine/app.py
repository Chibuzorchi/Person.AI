from flask import Flask, jsonify
import os
import time
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any

app = Flask(__name__)

# Service configuration
SERVICE_NAME = os.getenv('SERVICE_NAME', 'media-engine')
SERVICE_VERSION = os.getenv('SERVICE_VERSION', '1.0.0')
START_TIME = time.time()

# Mock data for metrics and audit
request_count = 0
audio_files_generated = 0
elevenlabs_api_calls = 0

# Historical audit events
audit_events = [
    {
        "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
        "event_type": "audio_generated",
        "user_id": "user_123",
        "resource_id": "audio_456",
        "action": "generate",
        "details": {"duration_seconds": 45, "voice_id": "voice_001", "format": "mp3"},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(hours=2, minutes=30)).isoformat(),
        "event_type": "api_call",
        "user_id": "system",
        "resource_id": "elevenlabs_api",
        "action": "text_to_speech",
        "details": {"characters": 1200, "voice_id": "voice_001", "cost": 0.012},
        "success": True
    },
    {
        "timestamp": (datetime.now() - timedelta(minutes=15)).isoformat(),
        "event_type": "error_occurred",
        "user_id": "system",
        "resource_id": "elevenlabs_api",
        "action": "text_to_speech",
        "details": {"error_code": "QUOTA_EXCEEDED", "retry_after": 3600},
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
        "elevenlabs_api": random.choice([True, True, True, False]),  # 75% success rate
        "file_storage": True,
        "redis_cache": random.choice([True, True, False]),  # 67% success rate
        "cdn": True
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
        "queue_depth": random.randint(0, 3),
        "active_processing": random.randint(0, 5),
        "storage_usage_gb": random.uniform(10.5, 25.8)
    }
    
    return jsonify(health_data), 200 if status == "healthy" else 503

@app.route('/metrics', methods=['GET'])
def metrics():
    """Prometheus format metrics endpoint"""
    global request_count, audio_files_generated, elevenlabs_api_calls
    
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
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.1"}} {request_count * 0.5}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="0.5"}} {request_count * 0.8}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="1.0"}} {request_count * 0.95}
http_request_duration_seconds_bucket{{service="{SERVICE_NAME}",le="+Inf"}} {request_count}
http_request_duration_seconds_sum{{service="{SERVICE_NAME}"}} {request_count * 0.6}
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

# HELP audio_files_generated_total Total number of audio files generated
# TYPE audio_files_generated_total counter
audio_files_generated_total{{service="{SERVICE_NAME}"}} {audio_files_generated}

# HELP elevenlabs_api_calls_total Total number of ElevenLabs API calls
# TYPE elevenlabs_api_calls_total counter
elevenlabs_api_calls_total{{service="{SERVICE_NAME}"}} {elevenlabs_api_calls}

# HELP active_processing Current number of active audio processing jobs
# TYPE active_processing gauge
active_processing{{service="{SERVICE_NAME}"}} {random.randint(0, 5)}

# HELP storage_usage_bytes Storage usage in bytes
# TYPE storage_usage_bytes gauge
storage_usage_bytes{{service="{SERVICE_NAME}"}} {random.randint(10 * 1024**3, 30 * 1024**3)}

# HELP queue_depth Current queue depth
# TYPE queue_depth gauge
queue_depth{{service="{SERVICE_NAME}"}} {random.randint(0, 3)}
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
            "event_type": random.choice(["audio_generated", "api_call", "error_occurred"]),
            "user_id": f"user_{random.randint(100, 999)}",
            "resource_id": f"audio_{random.randint(1000, 9999)}",
            "action": random.choice(["generate", "process", "upload", "validate"]),
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

@app.route('/api/generate-audio', methods=['POST'])
def generate_audio():
    """Simulate audio generation for audit events"""
    global audio_files_generated, elevenlabs_api_calls
    audio_files_generated += 1
    elevenlabs_api_calls += 1
    
    # Add audit event
    new_event = {
        "timestamp": datetime.now().isoformat(),
        "event_type": "audio_generated",
        "user_id": "user_123",
        "resource_id": f"audio_{audio_files_generated}",
        "action": "generate",
        "details": {"duration_seconds": random.randint(30, 120), "voice_id": "voice_001", "format": "mp3"},
        "success": True
    }
    audit_events.append(new_event)
    
    return jsonify({"status": "success", "audio_id": f"audio_{audio_files_generated}"}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8003, debug=True)
