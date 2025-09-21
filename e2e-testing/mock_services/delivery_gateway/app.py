"""
Delivery Gateway Mock Service (Slack, Email, SMS)
"""
import os
import json
import time
import uuid
from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

class DeliveryGatewayMock:
    def __init__(self):
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL', 'mock_webhook')
        self.email_smtp = os.getenv('EMAIL_SMTP_HOST', 'mock_smtp')
        self.delivery_logs = []
    
    def send_to_slack(self, content, audio_file=None):
        """Send brief to Slack"""
        try:
            message_id = f"slack_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Simulate Slack delivery
            delivery_result = {
                'channel': 'general',
                'message_id': message_id,
                'status': 'delivered',
                'delivery_time': time.time(),
                'text_delivered': True,
                'audio_delivered': audio_file is not None,
                'webhook_url': self.slack_webhook,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log delivery
            self.delivery_logs.append({
                'service': 'slack',
                'result': delivery_result,
                'timestamp': datetime.now().isoformat()
            })
            
            return delivery_result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'delivery_time': time.time()
            }
    
    def send_to_email(self, content, audio_file=None):
        """Send brief to email"""
        try:
            message_id = f"email_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Simulate email delivery
            delivery_result = {
                'recipient': 'user@example.com',
                'message_id': message_id,
                'status': 'delivered',
                'delivery_time': time.time(),
                'text_delivered': True,
                'audio_delivered': audio_file is not None,
                'smtp_host': self.email_smtp,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log delivery
            self.delivery_logs.append({
                'service': 'email',
                'result': delivery_result,
                'timestamp': datetime.now().isoformat()
            })
            
            return delivery_result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'delivery_time': time.time()
            }
    
    def send_to_sms(self, content):
        """Send brief to SMS"""
        try:
            message_id = f"sms_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            
            # Simulate SMS delivery
            delivery_result = {
                'recipient': '+1234567890',
                'message_id': message_id,
                'status': 'delivered',
                'delivery_time': time.time(),
                'text_delivered': True,
                'audio_delivered': False,  # SMS doesn't support audio
                'timestamp': datetime.now().isoformat()
            }
            
            # Log delivery
            self.delivery_logs.append({
                'service': 'sms',
                'result': delivery_result,
                'timestamp': datetime.now().isoformat()
            })
            
            return delivery_result
            
        except Exception as e:
            return {
                'status': 'failed',
                'error': str(e),
                'delivery_time': time.time()
            }

# Initialize service
delivery_gateway = DeliveryGatewayMock()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'delivery-gateway-mock',
        'timestamp': datetime.now().isoformat(),
        'delivery_count': len(delivery_gateway.delivery_logs)
    })

@app.route('/deliver/slack', methods=['POST'])
def deliver_slack():
    """Deliver to Slack endpoint"""
    try:
        data = request.json
        content = data.get('content', {})
        audio_file = data.get('audio_file')
        
        result = delivery_gateway.send_to_slack(content, audio_file)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'delivered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deliver/email', methods=['POST'])
def deliver_email():
    """Deliver to Email endpoint"""
    try:
        data = request.json
        content = data.get('content', {})
        audio_file = data.get('audio_file')
        
        result = delivery_gateway.send_to_email(content, audio_file)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'delivered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deliver/sms', methods=['POST'])
def deliver_sms():
    """Deliver to SMS endpoint"""
    try:
        data = request.json
        content = data.get('content', {})
        
        result = delivery_gateway.send_to_sms(content)
        
        return jsonify({
            'status': 'success',
            'result': result,
            'delivered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/deliver/all', methods=['POST'])
def deliver_all():
    """Deliver to all channels endpoint"""
    try:
        data = request.json
        content = data.get('content', {})
        audio_file = data.get('audio_file')
        
        results = {}
        
        # Deliver to Slack
        results['slack'] = delivery_gateway.send_to_slack(content, audio_file)
        
        # Deliver to Email
        results['email'] = delivery_gateway.send_to_email(content, audio_file)
        
        # Deliver to SMS
        results['sms'] = delivery_gateway.send_to_sms(content)
        
        return jsonify({
            'status': 'success',
            'results': results,
            'delivered_at': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/delivery-logs', methods=['GET'])
def get_delivery_logs():
    """Get delivery logs endpoint"""
    try:
        return jsonify({
            'status': 'success',
            'logs': delivery_gateway.delivery_logs,
            'total_deliveries': len(delivery_gateway.delivery_logs)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
