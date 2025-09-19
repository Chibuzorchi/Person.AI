# Question 1: Slack Integration Mock/Sandbox Design

## Question
"If you needed to test our Slack integration without hitting the real Slack API, how would you design a mock or sandbox environment? Which tools or frameworks would you use, and how would you handle edge cases like expired tokens or rate limits?"

## Comprehensive Answer

### Architecture Overview
I would design a multi-layered mocking strategy that simulates the complete Slack API ecosystem while providing realistic testing scenarios for Person.ai's integration needs.

### Core Tools & Framework Stack

#### 1. **WireMock** - Primary API Mocking
```yaml
# docker-compose.yml for test environment
version: '3.8'
services:
  slack-mock:
    image: wiremock/wiremock:latest
    ports:
      - "8080:8080"
    volumes:
      - ./wiremock-mappings:/home/wiremock/mappings
      - ./wiremock-files:/home/wiremock/__files
    command: --global-response-templating --verbose
```

#### 2. **Slack SDK Mock** - WebSocket & Real-time Events
```python
# slack_mock_server.py
import asyncio
import json
from slack_sdk.web import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest

class SlackMockServer:
    def __init__(self):
        self.app_token = "xapp-mock-token"
        self.bot_token = "xoxb-mock-token"
        self.client = WebClient(token=self.bot_token)
        
    async def simulate_message_event(self, channel, text, user="U123456"):
        """Simulate incoming message events"""
        event = {
            "type": "message",
            "channel": channel,
            "user": user,
            "text": text,
            "ts": str(int(time.time()))
        }
        return await self.broadcast_event(event)
```

#### 3. **Test Data Factory** - Realistic Slack Data
```python
# test_data_factory.py
from faker import Faker
import random
from datetime import datetime, timedelta

class SlackDataFactory:
    def __init__(self):
        self.fake = Faker()
        
    def generate_workspace(self):
        return {
            "id": f"T{random.randint(1000000, 9999999)}",
            "name": self.fake.company(),
            "domain": self.fake.domain_name(),
            "is_org_shared": random.choice([True, False])
        }
    
    def generate_channels(self, count=10):
        channels = []
        for i in range(count):
            channel_type = random.choice(["public", "private", "im", "mpim"])
            channels.append({
                "id": f"C{random.randint(1000000, 9999999)}",
                "name": self.fake.slug() if channel_type != "im" else None,
                "type": channel_type,
                "is_member": random.choice([True, False]),
                "is_archived": random.choice([True, False]),
                "created": int((datetime.now() - timedelta(days=random.randint(1, 365))).timestamp())
            })
        return channels
    
    def generate_users(self, count=20):
        users = []
        for i in range(count):
            users.append({
                "id": f"U{random.randint(1000000, 9999999)}",
                "name": self.fake.user_name(),
                "real_name": self.fake.name(),
                "email": self.fake.email(),
                "is_bot": random.choice([True, False]),
                "is_admin": random.choice([True, False]),
                "is_owner": random.choice([True, False]),
                "profile": {
                    "image_24": self.fake.image_url(),
                    "image_32": self.fake.image_url(),
                    "image_48": self.fake.image_url(),
                    "image_72": self.fake.image_url(),
                    "image_192": self.fake.image_url()
                }
            })
        return users
```

### WireMock Mappings for Slack API

#### 1. **Chat Post Message** - Success Case
```json
{
  "request": {
    "method": "POST",
    "urlPath": "/api/chat.postMessage",
    "headers": {
      "Authorization": {
        "matches": "Bearer xoxb-.*"
      }
    },
    "bodyPatterns": [
      {
        "matchesJsonPath": "$.channel"
      }
    ]
  },
  "response": {
    "status": 200,
    "headers": {
      "Content-Type": "application/json"
    },
    "jsonBody": {
      "ok": true,
      "channel": "{{jsonPath request.body '$.channel'}}",
      "ts": "{{now 'epoch'}}.{{randomValue length=6 type='NUMERIC'}}",
      "message": {
        "type": "message",
        "subtype": "bot_message",
        "text": "{{jsonPath request.body '$.text'}}",
        "ts": "{{now 'epoch'}}.{{randomValue length=6 type='NUMERIC'}}",
        "username": "Person.ai Bot",
        "bot_id": "B{{randomValue length=8 type='ALPHANUMERIC'}}"
      }
    }
  }
}
```

#### 2. **Token Expiration** - 401 Response
```json
{
  "request": {
    "method": "POST",
    "urlPath": "/api/chat.postMessage",
    "headers": {
      "Authorization": {
        "matches": "Bearer xoxb-expired.*"
      }
    }
  },
  "response": {
    "status": 401,
    "headers": {
      "Content-Type": "application/json"
    },
    "jsonBody": {
      "ok": false,
      "error": "invalid_auth",
      "detail": "token_expired"
    }
  }
}
```

#### 3. **Rate Limiting** - 429 Response
```json
{
  "request": {
    "method": "POST",
    "urlPath": "/api/chat.postMessage",
    "headers": {
      "Authorization": {
        "matches": "Bearer xoxb-rate-limited.*"
      }
    }
  },
  "response": {
    "status": 429,
    "headers": {
      "Content-Type": "application/json",
      "Retry-After": "60"
    },
    "jsonBody": {
      "ok": false,
      "error": "ratelimited",
      "retry_after": 60
    }
  }
}
```

### Edge Case Handling Implementation

#### 1. **Token Management & Refresh Flow**
```python
# token_manager.py
import time
from typing import Optional, Dict, Any

class SlackTokenManager:
    def __init__(self, mock_server_url: str):
        self.mock_server_url = mock_server_url
        self.tokens = {}
        
    def get_valid_token(self, user_id: str) -> str:
        """Get a valid token, refreshing if necessary"""
        token_data = self.tokens.get(user_id, {})
        
        if not token_data or self._is_token_expired(token_data):
            return self._refresh_token(user_id)
        
        return token_data['access_token']
    
    def _is_token_expired(self, token_data: Dict[str, Any]) -> bool:
        """Check if token is expired"""
        if not token_data.get('expires_at'):
            return True
        return time.time() > token_data['expires_at']
    
    def _refresh_token(self, user_id: str) -> str:
        """Simulate token refresh"""
        new_token = f"xoxb-refreshed-{int(time.time())}"
        self.tokens[user_id] = {
            'access_token': new_token,
            'expires_at': time.time() + 3600,  # 1 hour
            'refresh_token': f"xoxr-{int(time.time())}"
        }
        return new_token
```

#### 2. **Rate Limiting Simulation**
```python
# rate_limiter.py
import time
from collections import defaultdict, deque
from typing import Dict

class SlackRateLimiter:
    def __init__(self):
        self.requests = defaultdict(deque)
        self.rate_limits = {
            'chat.postMessage': {'limit': 1, 'window': 1},  # 1 per second
            'conversations.list': {'limit': 2, 'window': 1},  # 2 per second
            'users.list': {'limit': 1, 'window': 1}  # 1 per second
        }
    
    def is_rate_limited(self, endpoint: str, token: str) -> bool:
        """Check if request would be rate limited"""
        now = time.time()
        window = self.rate_limits.get(endpoint, {}).get('window', 1)
        limit = self.rate_limits.get(endpoint, {}).get('limit', 1)
        
        key = f"{token}:{endpoint}"
        requests = self.requests[key]
        
        # Remove old requests outside the window
        while requests and requests[0] < now - window:
            requests.popleft()
        
        return len(requests) >= limit
    
    def record_request(self, endpoint: str, token: str):
        """Record a request for rate limiting"""
        key = f"{token}:{endpoint}"
        self.requests[key].append(time.time())
```

### Test Implementation

#### 1. **Integration Test Suite**
```python
# test_slack_integration.py
import pytest
import requests
from unittest.mock import patch
from slack_mock_server import SlackMockServer
from test_data_factory import SlackDataFactory

class TestSlackIntegration:
    @pytest.fixture(autouse=True)
    def setup_mock(self):
        """Setup mock server before each test"""
        self.mock_server = SlackMockServer()
        self.data_factory = SlackDataFactory()
        self.base_url = "http://localhost:8080"
        
    def test_successful_message_post(self):
        """Test successful message posting"""
        response = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-valid-token"},
            json={
                "channel": "C1234567890",
                "text": "Test message from Person.ai"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "ts" in data
        assert data["message"]["text"] == "Test message from Person.ai"
    
    def test_expired_token_handling(self):
        """Test handling of expired tokens"""
        response = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-expired-token"},
            json={
                "channel": "C1234567890",
                "text": "Test message"
            }
        )
        
        assert response.status_code == 401
        data = response.json()
        assert data["ok"] is False
        assert data["error"] == "invalid_auth"
    
    def test_rate_limiting_handling(self):
        """Test rate limiting behavior"""
        # First request should succeed
        response1 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Message 1"}
        )
        assert response1.status_code == 200
        
        # Immediate second request should be rate limited
        response2 = requests.post(
            f"{self.base_url}/api/chat.postMessage",
            headers={"Authorization": "Bearer xoxb-rate-limited-token"},
            json={"channel": "C1234567890", "text": "Message 2"}
        )
        assert response2.status_code == 429
        assert "Retry-After" in response2.headers
    
    def test_webhook_delivery_simulation(self):
        """Test webhook delivery simulation"""
        # Simulate incoming webhook
        webhook_data = {
            "type": "event_callback",
            "event": {
                "type": "message",
                "channel": "C1234567890",
                "user": "U1234567890",
                "text": "Hello from user",
                "ts": "1234567890.123456"
            }
        }
        
        # This would be handled by the webhook endpoint
        response = requests.post(
            f"{self.base_url}/webhook/slack",
            json=webhook_data
        )
        
        assert response.status_code == 200
```

#### 2. **CI/CD Integration**
```yaml
# .github/workflows/slack-integration-tests.yml
name: Slack Integration Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  slack-mock-tests:
    runs-on: ubuntu-latest
    
    services:
      slack-mock:
        image: wiremock/wiremock:latest
        ports:
          - 8080:8080
        options: >-
          --health-cmd "curl -f http://localhost:8080/__admin/health || exit 1"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-asyncio requests faker
    
    - name: Wait for WireMock
      run: |
        timeout 60 bash -c 'until curl -f http://localhost:8080/__admin/health; do sleep 2; done'
    
    - name: Load WireMock mappings
      run: |
        curl -X POST http://localhost:8080/__admin/mappings/import \
          -H "Content-Type: application/json" \
          -d @wiremock-mappings/slack-api-mappings.json
    
    - name: Run Slack integration tests
      run: |
        pytest tests/integration/test_slack_integration.py -v --tb=short
    
    - name: Generate test report
      if: always()
      run: |
        pytest --html=report.html --self-contained-html
        echo "Test report generated: report.html"
```

### Advanced Features

#### 1. **Dynamic Response Generation**
```python
# dynamic_responses.py
from jinja2 import Template
import json
import random

class DynamicSlackResponse:
    def __init__(self):
        self.templates = {
            'message_response': Template('''
            {
                "ok": true,
                "channel": "{{ channel }}",
                "ts": "{{ timestamp }}.{{ random_digits }}",
                "message": {
                    "type": "message",
                    "text": "{{ text }}",
                    "user": "{{ bot_user_id }}",
                    "ts": "{{ timestamp }}.{{ random_digits }}"
                }
            }
            ''')
        }
    
    def generate_message_response(self, channel, text, bot_user_id="U1234567890"):
        """Generate dynamic message response"""
        template = self.templates['message_response']
        return json.loads(template.render(
            channel=channel,
            text=text,
            timestamp=int(time.time()),
            random_digits=random.randint(100000, 999999),
            bot_user_id=bot_user_id
        ))
```

#### 2. **WebSocket Event Simulation**
```python
# websocket_simulator.py
import asyncio
import websockets
import json
from typing import List, Dict, Any

class SlackWebSocketSimulator:
    def __init__(self, port=8765):
        self.port = port
        self.clients = set()
        
    async def register_client(self, websocket, path):
        """Register new WebSocket client"""
        self.clients.add(websocket)
        try:
            await websocket.wait_closed()
        finally:
            self.clients.remove(websocket)
    
    async def broadcast_event(self, event: Dict[str, Any]):
        """Broadcast event to all connected clients"""
        if self.clients:
            message = json.dumps(event)
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def simulate_user_message(self, channel: str, text: str, user: str = "U1234567890"):
        """Simulate a user sending a message"""
        event = {
            "type": "message",
            "channel": channel,
            "user": user,
            "text": text,
            "ts": str(int(time.time()))
        }
        await self.broadcast_event(event)
    
    async def start_server(self):
        """Start WebSocket server"""
        start_server = websockets.serve(self.register_client, "localhost", self.port)
        await start_server
        print(f"WebSocket server started on ws://localhost:{self.port}")
```

### Monitoring & Observability

#### 1. **Test Metrics Collection**
```python
# test_metrics.py
import time
from prometheus_client import Counter, Histogram, Gauge, start_http_server

class SlackTestMetrics:
    def __init__(self):
        self.api_requests = Counter('slack_api_requests_total', 'Total API requests', ['endpoint', 'status'])
        self.response_time = Histogram('slack_api_response_time_seconds', 'API response time')
        self.active_connections = Gauge('slack_websocket_connections_active', 'Active WebSocket connections')
        self.mock_errors = Counter('slack_mock_errors_total', 'Mock server errors', ['error_type'])
    
    def record_request(self, endpoint: str, status: str, duration: float):
        """Record API request metrics"""
        self.api_requests.labels(endpoint=endpoint, status=status).inc()
        self.response_time.observe(duration)
    
    def record_error(self, error_type: str):
        """Record mock server error"""
        self.mock_errors.labels(error_type=error_type).inc()
```

This comprehensive approach provides a robust, scalable mocking environment that accurately simulates Slack's API behavior while handling all the edge cases Person.ai would encounter in production.
