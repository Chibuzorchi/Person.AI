from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import time
from datetime import datetime
from typing import Dict, Any

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

# Mock database
users_db = {
    "test@personai.com": {
        "user_id": "user_123",
        "email": "test@personai.com",
        "password": "test_password",
        "name": "Test User",
        "preferences": {
            "slack_notifications": True,
            "email_notifications": True,
            "sms_notifications": False
        }
    }
}

sessions_db = {}
briefings_db = {}
integrations_db = {}

@app.route('/api/user/login', methods=['POST'])
def user_login():
    """Mock user login endpoint"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400
        
        # Check credentials
        if email in users_db and users_db[email]['password'] == password:
            user = users_db[email].copy()
            del user['password']  # Don't return password
            
            # Create session
            session_token = str(uuid.uuid4())
            sessions_db[session_token] = {
                'user_id': user['user_id'],
                'email': email,
                'created_at': datetime.now().isoformat()
            }
            
            return jsonify({
                "success": True,
                "user": user,
                "session_token": session_token,
                "message": "Login successful"
            }), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/me', methods=['GET'])
def get_current_user():
    """Get current user info"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization header required"}), 401
        
        session_token = auth_header.split(' ')[1]
        
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        session = sessions_db[session_token]
        user_email = session['email']
        
        if user_email in users_db:
            user = users_db[user_email].copy()
            del user['password']
            return jsonify(user), 200
        else:
            return jsonify({"error": "User not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/briefings/schedule', methods=['POST'])
def schedule_briefing():
    """Mock briefing scheduling endpoint"""
    try:
        # Check authentication
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        data = request.get_json()
        briefing_id = str(uuid.uuid4())
        schedule_id = str(uuid.uuid4())
        
        briefing = {
            "briefing_id": briefing_id,
            "schedule_id": schedule_id,
            "user_id": sessions_db[session_token]['user_id'],
            "title": data.get('title'),
            "time": data.get('time'),
            "frequency": data.get('frequency'),
            "channels": data.get('channels', []),
            "enabled": True,
            "created_at": datetime.now().isoformat()
        }
        
        briefings_db[briefing_id] = briefing
        
        return jsonify({
            "success": True,
            "briefing_id": briefing_id,
            "schedule_id": schedule_id,
            "message": "Briefing scheduled successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/preferences', methods=['GET'])
def get_preferences():
    """Get user preferences"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        session = sessions_db[session_token]
        user_email = session['email']
        
        if user_email in users_db:
            preferences = users_db[user_email]['preferences']
            return jsonify(preferences), 200
        else:
            return jsonify({"error": "User not found"}), 404
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/user/preferences', methods=['PUT'])
def update_preferences():
    """Update user preferences"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        session = sessions_db[session_token]
        user_email = session['email']
        
        if user_email not in users_db:
            return jsonify({"error": "User not found"}), 404
        
        data = request.get_json()
        
        # Update preferences
        users_db[user_email]['preferences'].update(data)
        
        return jsonify({
            "success": True,
            "preferences": users_db[user_email]['preferences'],
            "message": "Preferences updated successfully"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/integrations/connect', methods=['POST'])
def connect_integration():
    """Mock integration connection endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        data = request.get_json()
        integration_type = data.get('integration_type')
        config = data.get('config', {})
        
        integration_id = str(uuid.uuid4())
        
        integration = {
            "integration_id": integration_id,
            "user_id": sessions_db[session_token]['user_id'],
            "integration_type": integration_type,
            "config": config,
            "status": "connected",
            "created_at": datetime.now().isoformat()
        }
        
        integrations_db[integration_id] = integration
        
        return jsonify({
            "success": True,
            "integration_id": integration_id,
            "status": "connected",
            "message": f"{integration_type} integration connected successfully"
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/integrations/test', methods=['POST'])
def test_integration():
    """Mock integration test endpoint"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        data = request.get_json()
        integration_type = data.get('integration_type')
        config = data.get('config', {})
        
        # Simulate connection test
        time.sleep(1)  # Simulate network delay
        
        # Mock test results based on integration type
        if integration_type == 'slack':
            webhook_url = config.get('webhook_url', '')
            if webhook_url and 'hooks.slack.com' in webhook_url:
                return jsonify({
                    "success": True,
                    "message": "Slack connection successful"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid Slack webhook URL"
                }), 400
                
        elif integration_type == 'email':
            smtp_server = config.get('smtp_server', '')
            if smtp_server and 'smtp' in smtp_server:
                return jsonify({
                    "success": True,
                    "message": "Email connection successful"
                }), 200
            else:
                return jsonify({
                    "success": False,
                    "error": "Invalid SMTP server"
                }), 400
        
        return jsonify({
            "success": True,
            "message": f"{integration_type} connection test successful"
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "bubble-frontend-api",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }), 200

@app.route('/api/briefings', methods=['GET'])
def get_briefings():
    """Get user's briefings"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        user_id = sessions_db[session_token]['user_id']
        user_briefings = [b for b in briefings_db.values() if b['user_id'] == user_id]
        
        return jsonify({
            "briefings": user_briefings,
            "count": len(user_briefings)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/integrations', methods=['GET'])
def get_integrations():
    """Get user's integrations"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Authorization required"}), 401
        
        session_token = auth_header.split(' ')[1]
        if session_token not in sessions_db:
            return jsonify({"error": "Invalid session"}), 401
        
        user_id = sessions_db[session_token]['user_id']
        user_integrations = [i for i in integrations_db.values() if i['user_id'] == user_id]
        
        return jsonify({
            "integrations": user_integrations,
            "count": len(user_integrations)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Person.ai Mock API Server...")
    print("📡 API available at: http://localhost:5000")
    print("🔗 Frontend should connect to: http://localhost:5000/api")
    print("👤 Test credentials: test@personai.com / test_password")
    app.run(host='0.0.0.0', port=5000, debug=True)
