# Slack Integration Mock Server

A comprehensive mock server for testing Slack integrations without hitting the real Slack API. This implementation provides realistic API responses, WebSocket event simulation, and handles edge cases like expired tokens and rate limiting.

## Features

- **WireMock Integration**: RESTful API mocking with dynamic responses
- **WebSocket Support**: Real-time event simulation
- **Token Management**: Automatic token refresh simulation
- **Rate Limiting**: Configurable rate limiting per endpoint
- **Test Data Factory**: Realistic fake data generation
- **Docker Support**: Easy deployment with Docker Compose
- **CI/CD Ready**: GitHub Actions workflow included

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for local development)

### Using Docker Compose (Recommended)

1. **Start the mock servers:**
   ```bash
   docker-compose up -d
   ```

2. **Verify services are running:**
   ```bash
   # Check WireMock
   curl http://localhost:8080/__admin/health
   
   # Check WebSocket server
   curl http://localhost:8765
   ```

3. **Run the test client:**
   ```bash
   docker-compose exec slack-websocket python scripts/test_client.py
   ```

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start WireMock:**
   ```bash
   docker run -d -p 8080:8080 -v $(pwd)/wiremock-mappings:/home/wiremock/mappings wiremock/wiremock:latest
   ```

3. **Load WireMock mappings:**
   ```bash
   # Load all mappings
   for file in wiremock-mappings/*.json; do
     curl -X POST http://localhost:8080/__admin/mappings/import \
       -H "Content-Type: application/json" \
       -d @"$file"
   done
   ```

4. **Start WebSocket server:**
   ```bash
   python scripts/start_mock.py
   ```

5. **Run tests:**
   ```bash
   pytest tests/test_slack_integration.py -v
   ```

## API Endpoints

### WireMock (Port 8080)

- `POST /api/chat.postMessage` - Send messages
- `GET /api/conversations.list` - List channels
- `GET /api/users.list` - List users
- `GET /__admin/health` - Health check

### WebSocket (Port 8765)

- Connect to `ws://localhost:8765`
- Subscribe to events: `{"type": "subscribe", "events": ["message", "app_mention"]}`
- Send ping: `{"type": "ping"}`

## Test Scenarios

### 1. Successful Message Posting
```bash
curl -X POST http://localhost:8080/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-valid-token" \
  -H "Content-Type: application/json" \
  -d '{"channel": "C1234567890", "text": "Hello from Person.ai!"}'
```

### 2. Expired Token Handling
```bash
curl -X POST http://localhost:8080/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-expired-token" \
  -H "Content-Type: application/json" \
  -d '{"channel": "C1234567890", "text": "This will fail"}'
```

### 3. Rate Limiting
```bash
# First request succeeds
curl -X POST http://localhost:8080/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-rate-limited-token" \
  -H "Content-Type: application/json" \
  -d '{"channel": "C1234567890", "text": "Message 1"}'

# Second request is rate limited
curl -X POST http://localhost:8080/api/chat.postMessage \
  -H "Authorization: Bearer xoxb-rate-limited-token" \
  -H "Content-Type: application/json" \
  -d '{"channel": "C1234567890", "text": "Message 2"}'
```

## WebSocket Events

The WebSocket server can simulate various Slack events:

```python
# Simulate user message
await server.simulate_user_message("C1234567890", "Hello from user")

# Simulate app mention
await server.simulate_app_mention("C1234567890", "Hey @person.ai bot!")

# Simulate channel join
await server.simulate_channel_join("C1234567890", "U1234567890")
```

## Configuration

### Environment Variables

- `WIREMOCK_URL`: WireMock server URL (default: http://localhost:8080)
- `WEBSOCKET_PORT`: WebSocket server port (default: 8765)

### Rate Limiting

Configure rate limits in `slack_mock_server.py`:

```python
self.rate_limits = {
    'chat.postMessage': {'limit': 1, 'window': 1},  # 1 per second
    'conversations.list': {'limit': 2, 'window': 1},  # 2 per second
    'users.list': {'limit': 1, 'window': 1}  # 1 per second
}
```

## Testing

### Run All Tests
```bash
pytest tests/test_slack_integration.py -v
```

### Run Specific Test
```bash
pytest tests/test_slack_integration.py::TestSlackIntegration::test_successful_message_post -v
```

### Test Client
```bash
python scripts/test_client.py
```

## Integration with Person.ai

This mock server is designed to integrate seamlessly with Person.ai's testing infrastructure:

1. **Replace Slack API calls** with mock server URLs
2. **Use realistic test data** from the data factory
3. **Test edge cases** like token expiration and rate limiting
4. **Simulate real-time events** via WebSocket

## Monitoring

### Health Checks

- WireMock: `GET http://localhost:8080/__admin/health`
- WebSocket: Check connection status in logs

### Logs

- WireMock logs: `docker-compose logs slack-mock`
- WebSocket logs: `docker-compose logs slack-websocket`

## Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8080 and 8765 are available
2. **WireMock not responding**: Check if Docker container is running
3. **WebSocket connection failed**: Verify WebSocket server is started
4. **Rate limiting not working**: Check token format matches patterns

### Debug Mode

Start with debug logging:
```bash
python scripts/start_mock.py --log-level DEBUG
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
