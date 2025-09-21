"""
Gmail API Mock Service
"""
import os
import json
import random
from datetime import datetime, timedelta
from flask import Flask, jsonify, request
from faker import Faker

app = Flask(__name__)
fake = Faker()

class GmailMockService:
    def __init__(self):
        self.emails = []
        self.generate_sample_emails()
    
    def generate_sample_emails(self):
        """Generate realistic sample emails"""
        email_count = int(os.getenv('MOCK_DATA_COUNT', 20))
        
        subjects = [
            "Daily Standup Meeting - Project Update",
            "Invoice #INV-2024-001 - Payment Due",
            "Client Meeting Scheduled for Tomorrow",
            "Quarterly Sales Report - Q1 2024",
            "New Feature Release - Version 2.1.0",
            "Budget Approval Required - Marketing Campaign",
            "Team Building Event - Next Friday",
            "Security Alert - Password Reset Required",
            "Contract Renewal - 30 Days Notice",
            "Performance Review - Annual Assessment",
            "Weekly Team Sync - Action Items",
            "Project Deadline Extension Request",
            "Client Feedback - Product Demo",
            "Monthly Revenue Report - March 2024",
            "New Employee Onboarding - Welcome"
        ]
        
        for i in range(email_count):
            email = {
                'id': f"gmail_{i:06d}",
                'thread_id': f"thread_{random.randint(1, 10):06d}",
                'subject': random.choice(subjects),
                'sender': fake.email(),
                'recipients': [fake.email() for _ in range(random.randint(1, 3))],
                'body': self._generate_email_body(),
                'date': self._random_date_in_range(7),
                'labels': random.sample(['INBOX', 'SENT', 'IMPORTANT', 'WORK', 'PERSONAL'], random.randint(1, 3)),
                'attachments': self._generate_attachments(),
                'importance': random.choice(['high', 'normal', 'low']),
                'read': random.choice([True, False]),
                'starred': random.choice([True, False])
            }
            self.emails.append(email)
    
    def _generate_email_body(self) -> str:
        """Generate realistic email body content"""
        templates = [
            "Hi team,\n\nI wanted to update you on the progress of {project}.\n\n{details}\n\nBest regards,\n{sender}",
            "Dear {recipient},\n\nPlease find attached the {document_type} for your review.\n\n{instructions}\n\nThank you,\n{sender}",
            "Hello,\n\nThis is a reminder that {action} is due by {deadline}.\n\n{additional_info}\n\nRegards,\n{sender}"
        ]
        template = random.choice(templates)
        return template.format(
            project=fake.catch_phrase(),
            details=fake.text(max_nb_chars=200),
            recipient=fake.name(),
            document_type=random.choice(['report', 'proposal', 'contract', 'invoice']),
            instructions=fake.sentence(),
            sender=fake.name(),
            action=random.choice(['payment', 'review', 'approval', 'submission']),
            deadline=fake.date(),
            additional_info=fake.sentence()
        )
    
    def _generate_attachments(self):
        """Generate realistic attachment data"""
        if random.random() < 0.3:  # 30% chance of attachments
            return [{
                'filename': f"document_{random.randint(1, 100)}.pdf",
                'size': random.randint(1000, 5000000),
                'mime_type': 'application/pdf'
            }]
        return []
    
    def _random_date_in_range(self, days_back: int) -> str:
        """Generate random date within specified range"""
        start_date = datetime.now() - timedelta(days=days_back)
        random_date = start_date + timedelta(days=random.randint(0, days_back))
        return random_date.isoformat()

# Initialize service
gmail_service = GmailMockService()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'gmail-mock',
        'timestamp': datetime.now().isoformat(),
        'email_count': len(gmail_service.emails)
    })

@app.route('/gmail/v1/users/me/messages', methods=['GET'])
def get_messages():
    """Get Gmail messages endpoint"""
    try:
        # Get query parameters
        max_results = int(request.args.get('maxResults', 10))
        q = request.args.get('q', '')
        
        # Filter emails based on query
        filtered_emails = gmail_service.emails
        if q:
            filtered_emails = [email for email in gmail_service.emails 
                             if q.lower() in email['subject'].lower() or 
                                q.lower() in email['body'].lower()]
        
        # Limit results
        filtered_emails = filtered_emails[:max_results]
        
        # Format response
        messages = []
        for email in filtered_emails:
            messages.append({
                'id': email['id'],
                'threadId': email['thread_id'],
                'labelIds': email['labels']
            })
        
        return jsonify({
            'messages': messages,
            'resultSizeEstimate': len(messages)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gmail/v1/users/me/messages/<message_id>', methods=['GET'])
def get_message(message_id):
    """Get specific Gmail message endpoint"""
    try:
        # Find email by ID
        email = next((e for e in gmail_service.emails if e['id'] == message_id), None)
        
        if not email:
            return jsonify({"error": "Message not found"}), 404
        
        # Format response
        return jsonify({
            'id': email['id'],
            'threadId': email['thread_id'],
            'labelIds': email['labels'],
            'snippet': email['body'][:100] + '...',
            'payload': {
                'headers': [
                    {'name': 'Subject', 'value': email['subject']},
                    {'name': 'From', 'value': email['sender']},
                    {'name': 'To', 'value': ', '.join(email['recipients'])},
                    {'name': 'Date', 'value': email['date']}
                ],
                'body': {
                    'data': email['body']
                }
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/gmail/v1/users/me/messages/<message_id>/attachments/<attachment_id>', methods=['GET'])
def get_attachment(message_id, attachment_id):
    """Get message attachment endpoint"""
    try:
        # Find email by ID
        email = next((e for e in gmail_service.emails if e['id'] == message_id), None)
        
        if not email:
            return jsonify({"error": "Message not found"}), 404
        
        # Return mock attachment data
        return jsonify({
            'data': 'mock_attachment_data',
            'size': 1024
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
