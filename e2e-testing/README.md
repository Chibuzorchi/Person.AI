# E2E Testing System for Person.ai Pipeline

A comprehensive end-to-end testing system that validates the complete Person.ai pipeline: Gmail data extraction → Content generation → Audio processing → Multi-channel delivery.

## 🏗️ Architecture

This system provides:
- **Gmail Mock Service** (port 5004): Realistic email data generation
- **Content Engine Mock** (port 5005): OpenAI-style text generation
- **Media Engine Mock** (port 5006): ElevenLabs-style audio generation with real audio files
- **Delivery Gateway Mock** (port 5007): Multi-channel delivery (Slack, Email, SMS)
- **E2E Test Runner**: Orchestrates the complete pipeline

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.9+ (for local development)

### 1. Start the System
```bash
# Start all services
docker-compose up -d

# Check service status
docker-compose ps
```

### 2. Test Individual Services
```bash
# Run quick demo
python scripts/quick_demo.py

# Or test individual endpoints
curl http://localhost:5004/health  # Gmail Mock
curl http://localhost:5005/health  # Content Engine
curl http://localhost:5006/health  # Media Engine
curl http://localhost:5007/health  # Delivery Gateway
```

### 3. Run Complete E2E Test
```bash
# Run full E2E test
docker-compose run e2e-test-runner

# Or run locally
python test_runner/e2e_test_runner.py
```

## 📊 Test Pipeline

### Stage 1: Gmail Data Extraction
- Generates realistic email data (20 emails by default)
- Simulates Gmail API calls
- Extracts email content, subjects, senders, etc.

### Stage 2: Content Generation
- Processes Gmail data using OpenAI-style API
- Generates text brief and audio script
- Provides confidence scores and metadata

### Stage 3: Media Processing
- Converts audio script to actual audio files
- Uses pyttsx3 for real audio generation
- Supports multiple voice options and formats

### Stage 4: Multi-Channel Delivery
- Delivers to Slack, Email, and SMS
- Tracks delivery status and logs
- Provides delivery verification

### Stage 5: Verification
- Validates all stages completed successfully
- Checks data integrity and quality
- Generates comprehensive test reports

## 🔧 Configuration

### Environment Variables
```bash
# Service URLs
GMAIL_MOCK_URL=http://localhost:5004
CONTENT_ENGINE_URL=http://localhost:5005
MEDIA_ENGINE_URL=http://localhost:5006
DELIVERY_GATEWAY_URL=http://localhost:5007

# Mock Data
MOCK_DATA_COUNT=20
OPENAI_API_KEY=mock_key
ELEVENLABS_API_KEY=mock_key
SLACK_WEBHOOK_URL=mock_webhook
EMAIL_SMTP_HOST=mock_smtp
```

### Customizing Test Data
```python
# Modify mock_services/gmail/app.py
# Change email count, subjects, content, etc.
email_count = int(os.getenv('MOCK_DATA_COUNT', 20))
```

## 🧪 Testing

### Run All Tests
```bash
# Using Docker
docker-compose run e2e-test-runner

# Or locally
python test_runner/e2e_test_runner.py
```

### Test Categories
- **Gmail Extraction**: Tests email data retrieval and processing
- **Content Generation**: Tests OpenAI-style text generation
- **Media Processing**: Tests audio file generation
- **Delivery**: Tests multi-channel delivery
- **Verification**: Tests end-to-end validation

## 📡 API Endpoints

### Gmail Mock (Port 5004)
```
GET  /health                                    # Health check
GET  /gmail/v1/users/me/messages               # List messages
GET  /gmail/v1/users/me/messages/{id}          # Get message details
GET  /gmail/v1/users/me/messages/{id}/attachments/{aid}  # Get attachment
```

### Content Engine (Port 5005)
```
GET  /health                    # Health check
POST /v1/chat/completions       # OpenAI-style chat completions
POST /generate-brief            # Generate daily brief
```

### Media Engine (Port 5006)
```
GET  /health                           # Health check
POST /v1/text-to-speech/{voice_id}     # ElevenLabs-style TTS
POST /generate-audio                   # Generate audio from text
GET  /audio/{filename}                 # Download audio file
```

### Delivery Gateway (Port 5007)
```
GET  /health                    # Health check
POST /deliver/slack             # Deliver to Slack
POST /deliver/email             # Deliver to Email
POST /deliver/sms               # Deliver to SMS
POST /deliver/all               # Deliver to all channels
GET  /delivery-logs             # Get delivery logs
```

## 📈 Test Results

### Output Files
- **Test Results**: `/app/output/e2e_test_results_{test_id}.json`
- **Test Logs**: `/app/output/e2e_logs_{test_id}.txt`
- **Audio Files**: `/app/output/brief_{id}.wav`

### Sample Test Result
```json
{
  "test_id": "e2e_1234567890",
  "start_time": "2024-01-01T00:00:00",
  "overall_success": true,
  "duration": 45.2,
  "stages": {
    "gmail_extraction": {"success": true, "duration": 2.1},
    "content_generation": {"success": true, "duration": 3.5},
    "media_processing": {"success": true, "duration": 8.2},
    "delivery": {"success": true, "duration": 1.8},
    "verification": {"success": true, "duration": 0.5}
  }
}
```

## 🔄 CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests
on: [push, pull_request]
jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run E2E tests
        run: docker-compose up -d && docker-compose run e2e-test-runner
```

## 🛠️ Development

### Local Development
```bash
# Start services
docker-compose up -d

# Run tests
python test_runner/e2e_test_runner.py

# Check logs
docker-compose logs gmail-mock
docker-compose logs content-engine
docker-compose logs media-engine
docker-compose logs delivery-gateway
```

### Adding New Test Scenarios
1. Modify mock services in `mock_services/`
2. Update test runner in `test_runner/e2e_test_runner.py`
3. Add new test cases in `tests/`
4. Update documentation

## 🐛 Troubleshooting

### Common Issues
1. **Services not starting**: Check Docker logs and port conflicts
2. **Audio generation fails**: Ensure pyttsx3 dependencies are installed
3. **Delivery failures**: Check mock service configurations
4. **Test timeouts**: Increase timeout values in configuration

### Debug Commands
```bash
# Check service health
curl http://localhost:5004/health
curl http://localhost:5005/health
curl http://localhost:5006/health
curl http://localhost:5007/health

# Check delivery logs
curl http://localhost:5007/delivery-logs

# View test output
ls -la /app/output/
```

## 📝 License

This project is part of Person.ai's E2E testing framework.

---

**Built for Person.ai E2E Testing** 🚀
