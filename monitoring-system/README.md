# Person.ai Monitoring System

A comprehensive monitoring and testing framework for Person.ai's health, metrics, and audit endpoints. This system provides realistic mock services that mirror Person.ai's actual architecture and includes comprehensive test suites for CI/CD integration.

## 🏗️ Architecture

The monitoring system consists of **4 mock services**, each exposing three critical endpoints:

- **`integration-controller`** (port 8001): Manages integrations and brief creation
- **`content-engine`** (port 8002): Handles content generation and AI processing  
- **`media-engine`** (port 8003): Manages audio generation and media processing
- **`delivery-gateway`** (port 8004): Handles multi-channel message delivery

Each service exposes:
- **`/health`**: Service health status with dependencies and system metrics
- **`/metrics`**: Prometheus-format metrics for monitoring
- **`/audit`**: Audit logs with historical and real-time events

## 🚀 Quick Start

### 1. Start the Services

```bash
cd monitoring-system
docker-compose up -d
```

### 2. Run Quick Demo

```bash
python scripts/quick_demo.py
```

### 3. Run Full Test Suite

```bash
python scripts/run_monitoring_tests.py
```

### 4. Run Pytest Tests

```bash
pytest tests/ -v
```

## 📊 Health Endpoints

Each service's `/health` endpoint returns comprehensive status information:

```json
{
  "status": "healthy|degraded|unhealthy",
  "service": "integration-controller",
  "version": "1.2.3",
  "uptime": 3600,
  "timestamp": "2025-09-21T04:00:00Z",
  "dependencies": {
    "gmail_api": true,
    "slack_api": true,
    "quickbooks_api": false,
    "salesforce_api": true,
    "database": true
  },
  "system": {
    "memory_usage_percent": 65.5,
    "cpu_usage_percent": 23.1,
    "disk_usage_percent": 45.2
  },
  "queue_depth": 3,
  "active_connections": 15
}
```

### Health Check Features

- **Dependency Monitoring**: Checks external API connectivity
- **System Metrics**: Memory, CPU, and disk usage
- **Service Status**: Healthy, degraded, or unhealthy states
- **Performance Metrics**: Response times and queue depths
- **Realistic Simulation**: 75% success rate for external dependencies

## 📈 Metrics Endpoints

All services expose Prometheus-format metrics at `/metrics`:

```
# HELP http_requests_total Total number of HTTP requests
# TYPE http_requests_total counter
http_requests_total{service="integration-controller",method="GET",endpoint="/health"} 42

# HELP process_memory_usage_bytes Memory usage in bytes
# TYPE process_memory_usage_bytes gauge
process_memory_usage_bytes{service="integration-controller"} 1073741824

# HELP service_uptime_seconds Service uptime in seconds
# TYPE service_uptime_seconds gauge
service_uptime_seconds{service="integration-controller"} 3600
```

### Metrics Categories

- **HTTP Metrics**: Request counts, durations, status codes
- **System Metrics**: Memory, CPU, disk usage
- **Business Metrics**: Briefs processed, integrations connected, messages delivered
- **Performance Metrics**: Queue depths, active connections, success rates

## 📝 Audit Endpoints

Each service maintains audit logs at `/audit` with historical and real-time events:

```json
{
  "service": "integration-controller",
  "total_events": 150,
  "returned_events": 50,
  "events": [
    {
      "timestamp": "2025-09-21T04:00:00Z",
      "event_type": "user_login",
      "user_id": "user_123",
      "resource_id": "auth_system",
      "action": "login",
      "details": {"ip_address": "192.168.1.100"},
      "success": true
    }
  ]
}
```

### Audit Event Types

- **`user_login`**: User authentication events
- **`brief_created`**: Daily brief generation
- **`integration_connected`**: External service connections
- **`content_generated`**: AI content creation
- **`audio_generated`**: Media processing
- **`message_delivered`**: Multi-channel delivery
- **`error_occurred`**: System errors and failures

## 🧪 Testing Framework

### Test Categories

1. **Health Endpoint Tests** (`test_health_endpoints.py`)
   - Service availability and response times
   - Health response structure validation
   - Dependency status verification
   - System metrics validation

2. **Metrics Endpoint Tests** (`test_metrics_endpoints.py`)
   - Prometheus format validation
   - Required metrics presence
   - Metric value reasonableness
   - Counter monotonicity checks

3. **Audit Endpoint Tests** (`test_audit_endpoints.py`)
   - Audit data structure validation
   - Event generation and logging
   - Timestamp validation
   - Event coverage verification

### Test Features

- **Response Time Validation**: Health < 500ms, Metrics < 5s, Audit < 5s
- **Comprehensive Coverage**: All services and endpoint types
- **Realistic Data**: Mock services generate realistic test data
- **Error Simulation**: Tests handle both success and failure scenarios
- **Performance Testing**: Validates system performance under load

## 🔧 Configuration

### Environment Variables

Each service supports the following environment variables:

```bash
SERVICE_NAME=integration-controller
SERVICE_VERSION=1.2.3
HEALTH_CHECK_INTERVAL=30s
METRICS_ENABLED=true
AUDIT_ENABLED=true
```

### Service-Specific Features

- **Integration Controller**: Brief creation, integration management
- **Content Engine**: AI content generation, OpenAI API simulation
- **Media Engine**: Audio generation, ElevenLabs API simulation
- **Delivery Gateway**: Multi-channel delivery (Slack, Email, SMS)

## 🚀 CI/CD Integration

### GitHub Actions Workflow

The system includes a comprehensive GitHub Actions workflow that:

- Runs on every push and pull request
- Executes scheduled tests every 6 hours
- Tests all health, metrics, and audit endpoints
- Generates HTML test reports
- Uploads artifacts for analysis
- Provides failure alerts

### Docker Integration

All services are containerized and can be deployed independently:

```bash
# Build individual service
docker build -t personai/integration-controller ./mock_services/integration-controller

# Run service
docker run -p 8001:8001 personai/integration-controller
```

## 📊 Monitoring Dashboard

### Health Status Overview

```bash
# Check all services health
curl http://localhost:8001/health
curl http://localhost:8002/health  
curl http://localhost:8003/health
curl http://localhost:8004/health
```

### Metrics Collection

```bash
# Collect metrics for Prometheus
curl http://localhost:8001/metrics
curl http://localhost:8002/metrics
curl http://localhost:8003/metrics
curl http://localhost:8004/metrics
```

### Audit Log Analysis

```bash
# Get recent audit events
curl http://localhost:8001/audit | jq '.events[-5:]'
```

## 🔍 Troubleshooting

### Common Issues

1. **Service Not Ready**: Wait for health checks to pass
2. **Port Conflicts**: Ensure ports 8001-8004 are available
3. **Dependency Failures**: Check external API connectivity
4. **Test Failures**: Review test logs and service status

### Debug Commands

```bash
# Check service logs
docker-compose logs integration-controller

# Test individual endpoints
curl -v http://localhost:8001/health

# Run specific test
pytest tests/test_health_endpoints.py::TestHealthEndpoints::test_all_services_healthy -v
```

## 🎯 Integration with E2E Testing

This monitoring system integrates seamlessly with the existing E2E testing framework:

- **Shared Architecture**: Same service structure and endpoints
- **Complementary Testing**: Health/metrics/audit + functional testing
- **Unified CI/CD**: Combined test execution and reporting
- **Realistic Simulation**: Mirrors actual Person.ai service behavior

## 📈 Future Enhancements

### Phase 2: Fault Injection
- Simulate database failures
- Test expired token scenarios
- Network partition simulation
- Load testing capabilities

### Phase 3: Advanced Monitoring
- Grafana dashboard integration
- Alert rule configuration
- Performance benchmarking
- Capacity planning metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This monitoring system is part of the Person.ai testing framework and follows the same licensing terms.
