# Person.ai QA Engineer Interview Responses

## Role Overview
Person.ai is an AI-powered daily briefing platform that integrates with business services (Slack, QuickBooks, Gmail, Salesforce, etc.) and transforms data into concise text and audio briefings. The tech stack includes Bubble frontend, middleware connectors (Apideck, Merge, Paragon), custom APIs, and observability layers (Prometheus, Grafana, Loki).

## Interview Questions & Answers

### 1. Slack Integration Mock/Sandbox Design

**Question:** If you needed to test our Slack integration without hitting the real Slack API, how would you design a mock or sandbox environment? Which tools or frameworks would you use, and how would you handle edge cases like expired tokens or rate limits?

**Answer:**

**Tools & Framework:**
- **WireMock** for API mocking with dynamic responses
- **Slack SDK Mock** for WebSocket events simulation
- **Docker containers** for isolated test environments
- **Postman/Newman** for API contract testing

**Implementation:**
```python
# Mock Slack API responses
def setup_slack_mock():
    wiremock.stub_for(
        post(url_path_matching("/api/chat.postMessage"))
        .will_return(
            a_response()
            .with_status(200)
            .with_header("Content-Type", "application/json")
            .with_body('{"ok": true, "ts": "1234567890.123456"}')
        )
    )
```

**Edge Case Handling:**
- **Expired tokens**: Mock 401 responses, test token refresh flow
- **Rate limits**: Simulate 429 responses with retry-after headers
- **Webhook failures**: Mock delayed/failed delivery responses
- **Channel permissions**: Test various access scenarios

---

### 2. QuickBooks & Salesforce Test Data Seeding

**Question:** Suppose we want to QA QuickBooks and Salesforce connectors, but no real customer data is available. How would you seed realistic fake datasets (e.g., invoices, opportunities, contacts) so that automated regression tests remain useful?

**Answer:**

**Data Generation Strategy:**
```python
# Realistic test data factory
class TestDataFactory:
    def generate_invoices(self, count=100):
        return [{
            "id": f"INV-{i:06d}",
            "amount": random.uniform(100, 10000),
            "due_date": datetime.now() + timedelta(days=random.randint(1, 30)),
            "customer": self.generate_customer(),
            "line_items": self.generate_line_items()
        } for i in range(count)]
    
    def generate_opportunities(self, count=50):
        return [{
            "id": f"OPP-{i:06d}",
            "amount": random.uniform(1000, 100000),
            "stage": random.choice(["Prospecting", "Qualification", "Proposal"]),
            "close_date": datetime.now() + timedelta(days=random.randint(7, 90))
        } for i in range(count)]
```

**Tools:**
- **Faker library** for realistic data generation
- **CSV/JSON seed files** for consistent test datasets
- **Database fixtures** with pytest fixtures
- **API seeding scripts** to populate test environments

---

### 3. End-to-End Brief Generation Test

**Question:** A new daily brief should: pull data from Gmail, generate narrative texts, and deliver it to Slack. How would you design an end-to-end test to validate that all four stages succeeded, including both text and audio delivery?

**Answer:**

**Test Architecture:**
```python
@pytest.mark.e2e
def test_daily_brief_generation():
    # Stage 1: Gmail data pull
    gmail_data = mock_gmail_api.get_emails()
    assert len(gmail_data) > 0
    
    # Stage 2: Content generation
    content = content_engine.generate_brief(gmail_data)
    assert content.text_content is not None
    assert content.audio_content is not None
    
    # Stage 3: Media processing
    audio_file = media_engine.process_audio(content.audio_content)
    assert os.path.exists(audio_file)
    
    # Stage 4: Delivery validation
    slack_delivery = delivery_gateway.send_to_slack(content, audio_file)
    assert slack_delivery.status == "delivered"
    
    # Verify both text and audio in Slack
    slack_message = slack_api.get_message(slack_delivery.message_id)
    assert slack_message.text == content.text_content
    assert slack_message.audio_attachment is not None
```

**Validation Points:**
- Data extraction accuracy from Gmail
- Content generation quality and format
- Audio processing and ElevenLabs integration
- Multi-channel delivery (Slack, Email, SMS)
- Error handling and retry mechanisms

---

### 4. Health/Metrics/Audit Endpoint Verification

**Question:** Our services must expose /health, /metrics, and /audit endpoints. What would you verify at each endpoint during QA, and how would you automate those checks to catch failures in CI/CD?

**Answer:**

**Health Endpoint Checks:**
```python
def test_health_endpoints():
    services = ["integration-controller", "content-engine", "media-engine", "delivery-gateway"]
    
    for service in services:
        response = requests.get(f"{service}/health")
        assert response.status_code == 200
        health_data = response.json()
        assert health_data["status"] == "healthy"
        assert "uptime" in health_data
        assert "version" in health_data
```

**Metrics Endpoint Validation:**
```python
def test_metrics_endpoints():
    response = requests.get("/metrics")
    assert response.status_code == 200
    
    # Verify Prometheus format
    metrics = response.text
    assert "http_requests_total" in metrics
    assert "process_cpu_seconds_total" in metrics
    assert "go_memstats_alloc_bytes" in metrics
```

**Audit Endpoint Testing:**
```python
def test_audit_endpoints():
    # Trigger an action that should be audited
    create_brief()
    
    # Check audit logs
    audit_response = requests.get("/audit")
    assert audit_response.status_code == 200
    
    audit_logs = audit_response.json()
    assert any(log["action"] == "brief_created" for log in audit_logs)
```

**CI/CD Integration:**
```yaml
# GitHub Actions workflow
- name: Health Check Tests
  run: |
    pytest tests/integration/test_health_endpoints.py
    pytest tests/integration/test_metrics_endpoints.py
    pytest tests/integration/test_audit_endpoints.py
```

---

### 5. Bubble Frontend Testing Strategy

**Question:** Our front-end is built in Bubble. How would you structure automated tests for workflows (e.g., scheduling a briefing, toggling preferences) given that Bubble doesn't expose a traditional codebase? What tools or approaches would you use?

**Answer:**

**Approach for No-Code Platform:**
Since Bubble doesn't expose traditional code, I'd use:

**1. API-Level Testing:**
```python
# Test Bubble's internal APIs
def test_briefing_scheduling():
    # Use Bubble's API connector
    response = bubble_api.post("/api/workflow/schedule_briefing", {
        "time": "09:00",
        "frequency": "daily",
        "channels": ["slack", "email"]
    })
    assert response.status_code == 200
```

**2. Browser Automation:**
```python
# Playwright for UI workflows
def test_briefing_preferences():
    page.goto("/dashboard/preferences")
    page.click("[data-testid='toggle-slack-notifications']")
    page.click("[data-testid='save-preferences']")
    
    # Verify state change via API
    preferences = bubble_api.get("/api/user/preferences")
    assert preferences["slack_notifications"] == True
```

**3. Visual Regression Testing:**
```python
# Screenshot comparison for UI consistency
def test_dashboard_rendering():
    page.goto("/dashboard")
    page.screenshot(path="dashboard.png")
    expect(page).to_have_screenshot("dashboard-baseline.png")
```

**4. Data-Driven Testing:**
```python
# Test various user scenarios
@pytest.mark.parametrize("user_type,expected_features", [
    ("free", ["basic_briefs"]),
    ("premium", ["advanced_briefs", "custom_channels"]),
    ("enterprise", ["all_features", "custom_integrations"])
])
def test_user_workflows(user_type, expected_features):
    # Test user-specific functionality
    pass
```

**Tools & Framework:**
- **Playwright** for UI automation
- **Bubble API Connector** for backend testing
- **Percy/Chromatic** for visual regression
- **Postman** for API contract testing
- **Custom data attributes** in Bubble for reliable element selection

---

## Additional Considerations

### Test Data Management
- Use realistic but anonymized data for testing
- Implement data cleanup between test runs
- Version control test datasets
- Create data factories for different user personas

### CI/CD Pipeline Integration
- Run smoke tests on every commit
- Execute full regression suite nightly
- Generate comprehensive test reports
- Implement test result notifications

### Monitoring & Observability
- Track test execution metrics
- Monitor test stability and flakiness
- Set up alerts for test failures
- Generate test coverage reports

### Collaboration
- Document test strategies and patterns
- Conduct regular test reviews
- Share knowledge with development teams
- Maintain test documentation

This comprehensive approach ensures thorough testing across Person.ai's entire stack while maintaining maintainability and scalability.
