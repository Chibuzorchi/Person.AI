# 🚀 Person.ai Testing System - Complete Walkthrough

*This document explains each testing component for live demo purposes. Perfect for walking through the system during interviews.*

---

## 📋 Table of Contents

1. [Bubble Frontend Mock](#bubble-frontend-mock)
2. [Contract Testing](#contract-testing)
3. [E2E Testing](#e2e-testing)
4. [Monitoring System](#monitoring-system)
5. [Slack Mock](#slack-mock)
6. [Test Data Seeding](#test-data-seeding)

---

## 🎨 Bubble Frontend Mock

*Simulates the Person.ai web interface that users interact with to schedule briefings and manage integrations.*

### File-by-File Explanation

#### **Frontend Files (What Users See)**
- **`frontend/index.html`** - The main web page with login, dashboard, and settings
  - *Demo edit*: Change the welcome message, add new UI elements
- **`frontend/app.js`** - JavaScript that makes the page interactive
  - *Demo edit*: Change API endpoints, modify form behavior, add new features
- **`frontend/styles.css`** - Makes the page look professional
  - *Demo edit*: Change colors, fonts, layout

#### **Backend API Files**
- **`api/app.py`** - Mock API server that handles login, briefings, integrations
  - *Demo edit*: Change user credentials, add new API endpoints, modify responses
- **`api/requirements.txt`** - Python dependencies for the API

#### **Testing Files**
- **`tests/test_bubble_ui.py`** - Tests the web interface with a real browser
- **`tests/test_bubble_api.py`** - Tests the API endpoints
- **`run_headful_demo.py`** - Shows the browser automation in action

#### **Configuration Files**
- **`docker-compose.yml`** - Runs both frontend and API together
- **`requirements.txt`** - Python dependencies

#### **Utility Scripts**
- **`bubble_simple_test.py`** - Quick health check script for frontend and API
  - *Demo edit*: Modify test credentials, add new endpoint checks
- **`run_headful_demo.py`** - Runs UI tests in visible browser mode for demos

### How to Test

```bash
# Start the services
cd bubble-frontend-mock
docker-compose up -d

# Run the headful demo (shows browser automation)
python3 run_headful_demo.py

# Run tests
python3 -m pytest tests/ -v

# Clean up
docker-compose down
```

**Quick Demo**: 
- Open http://localhost:8081 in browser, login with `test@personai.com` / `test_password`
- Or run: `python3 bubble_simple_test.py` for automated health check

### Workflow & Dependencies

- **Input**: User interactions (clicks, form submissions)
- **Output**: API calls to schedule briefings, manage integrations
- **Connects to**: E2E testing (provides user scenarios), Monitoring system (tracks user actions)
- **Business Context**: This is what Person.ai users see - they schedule daily briefings here

### Demo-Time Editability

**Easy Live Edits:**
1. **Change login credentials** in `api/app.py` line 13-16
2. **Modify the welcome message** in `frontend/index.html`
3. **Add a new integration type** in `frontend/app.js` around line 200

### Extra Notes

- **Ports**: Frontend on 8081, API on 5001
- **Credentials**: `test@personai.com` / `test_password`
- **CI/CD**: Tests run in GitHub Actions with Playwright
- **Pitfall**: Browser tests need time to load - wait 3-5 seconds between actions

---

## 🤝 Contract Testing

*Ensures API responses match expected formats across all integrations (Slack, QuickBooks, Salesforce).*

### File-by-File Explanation

#### **Core System Files**
- **`schema_validator.py`** - The main contract validation engine
  - *Demo edit*: Add new validation rules, change error messages
- **`safe_integration.py`** - Wrapper that handles missing dependencies gracefully
  - *Demo edit*: Add new connector types, modify fallback behavior

#### **Contract Definitions**
- **`contracts/slack_chat_postMessage_POST.json`** - Defines what Slack message responses should look like
  - *Demo edit*: Add new required fields, change response structure
- **`contracts/quickbooks_customers_GET.json`** - Defines QuickBooks customer data format
- **`contracts/salesforce_accounts_GET.json`** - Defines Salesforce account data format

#### **Testing Files**
- **`tests/test_contract_standalone.py`** - Tests contract validation logic
- **`test_safe_integration.py`** - Tests the integration wrapper

### How to Test

```bash
# Install dependencies
cd contract-testing
pip3 install -r requirements.txt

# Test the safe integration
python3 safe_integration.py

# Run tests
python3 -m pytest tests/ -v

# Test schema validator directly
python3 -c "from schema_validator import SchemaValidator; v = SchemaValidator(); v.load_contracts(); print(f'Loaded {len(v.contracts)} contracts')"
```

**Quick Demo**: Run `python3 safe_integration.py` to see contract validation in action

### Workflow & Dependencies

- **Input**: API responses from Slack, QuickBooks, Salesforce
- **Output**: Validation results, drift detection alerts
- **Connects to**: All other systems (validates their API contracts)
- **Business Context**: Prevents broken integrations when APIs change - critical for 150+ integrations

### Demo-Time Editability

**Easy Live Edits:**
1. **Add a new field requirement** in `contracts/slack_chat_postMessage_POST.json`
2. **Change validation rules** in `schema_validator.py` around line 100
3. **Add a new connector type** in `safe_integration.py`

### Extra Notes

- **Dependencies**: jsonschema, requests, PyYAML
- **CI/CD**: Runs in GitHub Actions as part of integration tests
- **Pitfall**: Contract files must be valid JSON - syntax errors break validation

---

## 🔄 E2E Testing

*Tests the complete Person.ai pipeline: Gmail → Content Engine → Audio → Delivery.*

### File-by-File Explanation

#### **Mock Services (Simulates Real APIs)**
- **`mock_services/gmail/app.py`** - Fake Gmail that provides email data
  - *Demo edit*: Change email content, add new email types, modify sender info
- **`mock_services/content_engine/app.py`** - Simulates AI content generation
  - *Demo edit*: Change summary format, add new content types, modify AI responses
- **`mock_services/media_engine/app.py`** - Simulates audio generation
  - *Demo edit*: Change audio duration, add new voice options, modify file formats
- **`mock_services/delivery_gateway/app.py`** - Simulates message delivery
  - *Demo edit*: Add new delivery channels, change success rates, modify delivery formats

#### **Test Runner**
- **`test_runner/e2e_test_runner.py`** - Orchestrates the entire pipeline test
  - *Demo edit*: Change test data, modify pipeline steps, add new validations

#### **AI Quality Validation**
- **`ai_quality_validation.py`** - Validates AI-generated content quality
  - *Demo edit*: Change quality thresholds, add new validation rules

### How to Test

```bash
# Start all services
cd e2e-testing
docker-compose up -d

# Run quick demo
python3 scripts/quick_demo.py

# Run full E2E test
python3 test_runner/e2e_test_runner.py

# Run tests
python3 -m pytest tests/ -v

# Clean up
docker-compose down
```

**Quick Demo**: Run `python3 scripts/quick_demo.py` to see the full pipeline in action

### Workflow & Dependencies

- **Input**: Gmail emails (from test-data-seeding)
- **Output**: Delivered briefings to Slack/Email/SMS
- **Connects to**: All other systems (uses their data and services)
- **Business Context**: This is the core Person.ai value - turning emails into daily briefings

### Demo-Time Editability

**Easy Live Edits:**
1. **Change email content** in `mock_services/gmail/app.py` around line 50
2. **Modify AI summary format** in `mock_services/content_engine/app.py`
3. **Add new delivery channel** in `mock_services/delivery_gateway/app.py`

### Extra Notes

- **Ports**: Gmail(5004), Content(5005), Media(5006), Delivery(5007)
- **CI/CD**: Runs in GitHub Actions with Docker
- **Pitfall**: Services need 30-60 seconds to start - check health endpoints first

---

## 📊 Monitoring System

*Tracks health, performance, and audit logs across all Person.ai services.*

### File-by-File Explanation

#### **Mock Services (Simulates Real Monitoring)**
- **`mock_services/integration-controller/app.py`** - Main service that coordinates everything
  - *Demo edit*: Change health status, modify dependency checks, add new metrics
- **`mock_services/content-engine/app.py`** - Content generation service monitoring
- **`mock_services/media-engine/app.py`** - Audio generation service monitoring
- **`mock_services/delivery-gateway/app.py`** - Message delivery service monitoring

#### **Monitoring Tools**
- **`schema_drift_detection.py`** - Detects when API schemas change unexpectedly
  - *Demo edit*: Change drift thresholds, add new detection rules
- **`scripts/quick_demo.py`** - Shows all monitoring endpoints working

#### **Test Files**
- **`tests/test_health_endpoints.py`** - Tests /health endpoints
- **`tests/test_metrics_endpoints.py`** - Tests /metrics endpoints (Prometheus format)
- **`tests/test_audit_endpoints.py`** - Tests /audit endpoints

### How to Test

```bash
# Start monitoring services
cd monitoring-system
docker-compose up -d

# Run monitoring demo
python3 scripts/quick_demo.py

# Run tests
python3 -m pytest tests/ -v

# Test individual endpoints
curl http://localhost:8001/health
curl http://localhost:8002/metrics

# Clean up
docker-compose down
```

**Quick Demo**: Run `python3 scripts/quick_demo.py` to see health, metrics, and audit data

### Workflow & Dependencies

- **Input**: Service health data, performance metrics, user actions
- **Output**: Health dashboards, performance reports, audit logs
- **Connects to**: All other systems (monitors their health and performance)
- **Business Context**: Ensures Person.ai services are reliable and performing well

### Demo-Time Editability

**Easy Live Edits:**
1. **Simulate unhealthy service** in any `mock_services/*/app.py` - change health response
2. **Add new metric** in `mock_services/*/app.py` around the metrics section
3. **Generate new audit event** by calling the audit endpoint

### Extra Notes

- **Ports**: Integration(8001), Content(8002), Media(8003), Delivery(8004)
- **Metrics Format**: Prometheus (compatible with Grafana)
- **CI/CD**: Runs health checks in GitHub Actions
- **Pitfall**: Some services may show "degraded" status - this is realistic for demos

---

## 💬 Slack Mock

*Simulates Slack API for testing Person.ai's Slack integration without hitting real Slack.*

### File-by-File Explanation

#### **WireMock Mappings (API Response Templates)**
- **`wiremock-mappings/chat-postmessage-success.json`** - Successful message posting response
  - *Demo edit*: Change message format, add new fields, modify response structure
- **`wiremock-mappings/chat-postmessage-expired-token.json`** - Expired token error
  - *Demo edit*: Change error message, modify error codes
- **`wiremock-mappings/chat-postmessage-rate-limited.json`** - Rate limiting error
  - *Demo edit*: Change rate limit duration, modify retry logic
- **`wiremock-mappings/conversations-list.json`** - Channel list response
- **`wiremock-mappings/users-list.json`** - User list response

#### **Contract Testing**
- **`contract_testing.py`** - Validates Slack API responses match expected format
  - *Demo edit*: Add new validation rules, change contract requirements

#### **Test Files**
- **`tests/test_slack_integration.py`** - Tests actual Slack API calls
- **`tests/test_slack_standalone.py`** - Tests without external dependencies
- **`quick_test.py`** - Quick demo of Slack API functionality

### How to Test

```bash
# Start Slack mock
cd slack-mock
docker-compose up -d

# Run quick test
python3 quick_test.py

# Run comprehensive tests
python3 -m pytest tests/ -v

# Test contract validation
python3 contract_testing.py

# Test individual endpoints
curl -X POST http://localhost:8080/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-test-token" \
  -H "Content-Type: application/json" \
  -d '{"channel":"C1234567890","text":"Hello from Person.ai!"}'

# Clean up
docker-compose down
```

**Quick Demo**: Run `python3 quick_test.py` to see message posting, rate limiting, and error handling

### Workflow & Dependencies

- **Input**: Person.ai briefing messages
- **Output**: Slack channel messages, user notifications
- **Connects to**: E2E testing (receives final briefings), Contract testing (validates responses)
- **Business Context**: This is how Person.ai delivers daily briefings to users in Slack

### Demo-Time Editability

**Easy Live Edits:**
1. **Change message format** in `wiremock-mappings/chat-postmessage-success.json`
2. **Modify rate limit behavior** in `wiremock-mappings/chat-postmessage-rate-limited.json`
3. **Add new channel** in `wiremock-mappings/conversations-list.json`

### Extra Notes

- **Port**: 8080 (WireMock server)
- **Token Format**: `xoxb-test-token` (any token starting with `xoxb-` works)
- **CI/CD**: Runs in GitHub Actions with Docker
- **Pitfall**: WireMock needs a few seconds to load mappings

---

## 🌱 Test Data Seeding

*Generates realistic fake data for QuickBooks and Salesforce to test Person.ai's integrations.*

### File-by-File Explanation

#### **Data Generators (Creates Fake Data)**
- **`data_generators/quickbooks_factory.py`** - Generates fake QuickBooks customers and invoices
  - *Demo edit*: Change company names, modify invoice amounts, add new data fields
- **`data_generators/salesforce_factory.py`** - Generates fake Salesforce accounts and opportunities
  - *Demo edit*: Change account types, modify opportunity amounts, add new industries
- **`data_generators/base_factory.py`** - Common data generation utilities
  - *Demo edit*: Change name patterns, modify address formats

#### **API Mocks (Serves the Fake Data)**
- **`api_mocks/quickbooks/app.py`** - Mock QuickBooks API server
  - *Demo edit*: Add new endpoints, change response formats, modify business logic
- **`api_mocks/salesforce/app.py`** - Mock Salesforce API server
  - *Demo edit*: Add new object types, change query responses

#### **Priority Testing**
- **`priority_testing.py`** - Tests 150+ integrations with different priorities
  - *Demo edit*: Change test priorities, modify integration counts, add new connectors

### How to Test

```bash
# Start data seeding services
cd test-data-seeding
docker-compose up -d

# Run quick demo
python3 scripts/quick_demo.py

# Run priority testing
python3 priority_testing.py

# Run tests
python3 -m pytest tests/ -v

# Test individual APIs
curl http://localhost:5002/health
curl http://localhost:5003/health

# Clean up
docker-compose down
```

**Quick Demo**: Run `python3 scripts/quick_demo.py` to see fake customers, invoices, and accounts

### Workflow & Dependencies

- **Input**: Configuration for data generation
- **Output**: Realistic fake data for testing integrations
- **Connects to**: E2E testing (provides test data), Contract testing (validates data formats)
- **Business Context**: Person.ai needs to process real business data - this creates realistic test scenarios

### Demo-Time Editability

**Easy Live Edits:**
1. **Change company names** in `data_generators/quickbooks_factory.py` around line 20
2. **Modify invoice amounts** in `data_generators/quickbooks_factory.py` around line 60
3. **Add new industry types** in `data_generators/salesforce_factory.py`

### Extra Notes

- **Ports**: QuickBooks(5002), Salesforce(5003), PostgreSQL(5433)
- **Data Volume**: 100+ customers, 200+ invoices by default
- **CI/CD**: Runs in GitHub Actions with Docker
- **Pitfall**: PostgreSQL needs time to initialize - wait for health checks

---

## 🎯 Overall System Flow

```
1. Test Data Seeding → Generates fake business data
2. Slack Mock → Simulates Slack API responses  
3. E2E Testing → Processes data through full pipeline
4. Monitoring System → Tracks health and performance
5. Contract Testing → Validates API response formats
6. Bubble Frontend → Provides user interface
```

**Business Context**: This simulates the complete Person.ai experience - from generating realistic business data to delivering AI-powered daily briefings to users in Slack.

---

## 🚀 Quick Demo Commands

**Start everything:**
```bash
# Start all services
cd slack-mock && docker-compose up -d
cd ../test-data-seeding && docker-compose up -d  
cd ../e2e-testing && docker-compose up -d
cd ../monitoring-system && docker-compose up -d
cd ../bubble-frontend-mock && docker-compose up -d
```

**Run demos:**
```bash
# Show each system working
cd slack-mock && python3 quick_test.py
cd ../test-data-seeding && python3 scripts/quick_demo.py
cd ../e2e-testing && python3 scripts/quick_demo.py
cd ../monitoring-system && python3 scripts/quick_demo.py
cd ../bubble-frontend-mock && python3 run_headful_demo.py
```

**Clean up:**
```bash
# Stop all services
docker-compose down
```

---

*This system demonstrates enterprise-grade testing capabilities that would be essential for Person.ai's success with 150+ integrations and reliable daily briefing delivery.*
