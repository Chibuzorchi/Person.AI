"""
Salesforce API Mock Server
"""
import os
import json
import psycopg2
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Database connection
def get_db_connection():
    database_url = os.getenv('DATABASE_URL', 'postgresql://test_user:test_password@localhost:5432/test_data')
    return psycopg2.connect(database_url)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'salesforce-mock',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/services/data/v52.0/sobjects/Account', methods=['GET'])
def get_accounts():
    """Get accounts endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('limit', 100)
        offset = request.args.get('offset', 0)
        
        cursor.execute('''
            SELECT id, name, type, industry, annual_revenue, number_of_employees, phone, website,
                   billing_address, shipping_address, description, created_date, last_modified, 
                   owner_id, is_active
            FROM sf_accounts
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        ''', (int(limit), int(offset)))
        
        rows = cursor.fetchall()
        accounts = []
        
        for row in rows:
            accounts.append({
                "Id": row[0],
                "Name": row[1],
                "Type": row[2],
                "Industry": row[3],
                "AnnualRevenue": float(row[4]) if row[4] else 0,
                "NumberOfEmployees": row[5],
                "Phone": row[6],
                "Website": row[7],
                "BillingAddress": row[8] if row[8] else None,
                "ShippingAddress": row[9] if row[9] else None,
                "Description": row[10],
                "CreatedDate": row[11].isoformat() if hasattr(row[11], 'isoformat') else str(row[11]) if row[11] else None,
                "LastModifiedDate": row[12].isoformat() if hasattr(row[12], 'isoformat') else str(row[12]) if row[12] else None,
                "OwnerId": row[13],
                "IsActive": row[14]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "totalSize": len(accounts),
            "done": True,
            "records": accounts
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/services/data/v52.0/sobjects/Contact', methods=['GET'])
def get_contacts():
    """Get contacts endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('limit', 100)
        offset = request.args.get('offset', 0)
        
        cursor.execute('''
            SELECT id, first_name, last_name, email, phone, mobile_phone, title, department,
                   account_id, account_name, mailing_address, description, created_date, 
                   last_modified, owner_id, is_active
            FROM sf_contacts
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        ''', (int(limit), int(offset)))
        
        rows = cursor.fetchall()
        contacts = []
        
        for row in rows:
            contacts.append({
                "Id": row[0],
                "FirstName": row[1],
                "LastName": row[2],
                "Email": row[3],
                "Phone": row[4],
                "MobilePhone": row[5],
                "Title": row[6],
                "Department": row[7],
                "AccountId": row[8],
                "Account": {"Name": row[9]} if row[9] else None,
                "MailingAddress": row[10] if row[10] else None,
                "Description": row[11],
                "CreatedDate": row[12].isoformat() if row[12] else None,
                "LastModifiedDate": row[13].isoformat() if row[13] else None,
                "OwnerId": row[14],
                "IsActive": row[15]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "totalSize": len(contacts),
            "done": True,
            "records": contacts
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/services/data/v52.0/sobjects/Opportunity', methods=['GET'])
def get_opportunities():
    """Get opportunities endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('limit', 100)
        offset = request.args.get('offset', 0)
        
        cursor.execute('''
            SELECT id, name, account_id, account_name, amount, stage_name, probability, close_date,
                   lead_source, type, forecast_category, description, next_step, created_date,
                   last_modified, owner_id, is_won, is_closed
            FROM sf_opportunities
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        ''', (int(limit), int(offset)))
        
        rows = cursor.fetchall()
        opportunities = []
        
        for row in rows:
            opportunities.append({
                "Id": row[0],
                "Name": row[1],
                "AccountId": row[2],
                "Account": {"Name": row[3]} if row[3] else None,
                "Amount": float(row[4]) if row[4] else 0,
                "StageName": row[5],
                "Probability": row[6],
                "CloseDate": row[7].isoformat() if row[7] else None,
                "LeadSource": row[8],
                "Type": row[9],
                "ForecastCategoryName": row[10],
                "Description": row[11],
                "NextStep": row[12],
                "CreatedDate": row[13].isoformat() if row[13] else None,
                "LastModifiedDate": row[14].isoformat() if row[14] else None,
                "OwnerId": row[15],
                "IsWon": row[16],
                "IsClosed": row[17]
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "totalSize": len(opportunities),
            "done": True,
            "records": opportunities
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/services/data/v52.0/sobjects/Account', methods=['POST'])
def create_account():
    """Create account endpoint"""
    try:
        account_data = request.json
        
        # Simulate account creation
        new_account = {
            "Id": f"ACC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "Name": account_data.get('Name', 'New Account'),
            "Type": account_data.get('Type'),
            "Industry": account_data.get('Industry'),
            "AnnualRevenue": account_data.get('AnnualRevenue', 0),
            "NumberOfEmployees": account_data.get('NumberOfEmployees', 0),
            "Phone": account_data.get('Phone'),
            "Website": account_data.get('Website'),
            "BillingAddress": account_data.get('BillingAddress'),
            "ShippingAddress": account_data.get('ShippingAddress'),
            "Description": account_data.get('Description'),
            "CreatedDate": datetime.now().isoformat(),
            "LastModifiedDate": datetime.now().isoformat(),
            "OwnerId": account_data.get('OwnerId'),
            "IsActive": account_data.get('IsActive', True)
        }
        
        return jsonify(new_account), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/services/data/v52.0/sobjects/Contact', methods=['POST'])
def create_contact():
    """Create contact endpoint"""
    try:
        contact_data = request.json
        
        # Simulate contact creation
        new_contact = {
            "Id": f"CON-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "FirstName": contact_data.get('FirstName', 'New'),
            "LastName": contact_data.get('LastName', 'Contact'),
            "Email": contact_data.get('Email'),
            "Phone": contact_data.get('Phone'),
            "MobilePhone": contact_data.get('MobilePhone'),
            "Title": contact_data.get('Title'),
            "Department": contact_data.get('Department'),
            "AccountId": contact_data.get('AccountId'),
            "Account": {"Name": contact_data.get('Account', {}).get('Name')} if contact_data.get('Account') else None,
            "MailingAddress": contact_data.get('MailingAddress'),
            "Description": contact_data.get('Description'),
            "CreatedDate": datetime.now().isoformat(),
            "LastModifiedDate": datetime.now().isoformat(),
            "OwnerId": contact_data.get('OwnerId'),
            "IsActive": contact_data.get('IsActive', True)
        }
        
        return jsonify(new_contact), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/services/data/v52.0/sobjects/Opportunity', methods=['POST'])
def create_opportunity():
    """Create opportunity endpoint"""
    try:
        opportunity_data = request.json
        
        # Simulate opportunity creation
        new_opportunity = {
            "Id": f"OPP-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "Name": opportunity_data.get('Name', 'New Opportunity'),
            "AccountId": opportunity_data.get('AccountId'),
            "Account": {"Name": opportunity_data.get('Account', {}).get('Name')} if opportunity_data.get('Account') else None,
            "Amount": opportunity_data.get('Amount', 0),
            "StageName": opportunity_data.get('StageName', 'Prospecting'),
            "Probability": opportunity_data.get('Probability', 10),
            "CloseDate": opportunity_data.get('CloseDate'),
            "LeadSource": opportunity_data.get('LeadSource'),
            "Type": opportunity_data.get('Type'),
            "ForecastCategoryName": opportunity_data.get('ForecastCategoryName', 'Pipeline'),
            "Description": opportunity_data.get('Description'),
            "NextStep": opportunity_data.get('NextStep'),
            "CreatedDate": datetime.now().isoformat(),
            "LastModifiedDate": datetime.now().isoformat(),
            "OwnerId": opportunity_data.get('OwnerId'),
            "IsWon": opportunity_data.get('IsWon', False),
            "IsClosed": opportunity_data.get('IsClosed', False)
        }
        
        return jsonify(new_opportunity), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
