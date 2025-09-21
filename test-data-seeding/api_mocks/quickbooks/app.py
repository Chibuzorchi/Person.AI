"""
QuickBooks API Mock Server
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
        'service': 'quickbooks-mock',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to debug the issue"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email FROM qb_customers LIMIT 1')
        row = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'id': row[0],
            'name': row[1], 
            'email': row[2]
        })
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/v3/company/<company_id>/customers', methods=['GET'])
def get_customers(company_id):
    """Get customers endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('maxResults', 100)
        offset = request.args.get('startPosition', 0)
        
        cursor.execute('''
            SELECT id, name, email, phone, website, billing_address, shipping_address,
                   tax_id, currency, payment_terms, credit_limit, balance, is_active,
                   created_date, last_modified
            FROM qb_customers
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        ''', (int(limit), int(offset)))
        
        rows = cursor.fetchall()
        customers = []
        
        for row in rows:
            customers.append({
                "Id": row[0],
                "Name": row[1],
                "Email": row[2],
                "Phone": row[3],
                "Website": row[4],
                "BillAddr": row[5] if row[5] else None,
                "ShipAddr": row[6] if row[6] else None,
                "TaxIdentifier": row[7],
                "CurrencyRef": {"value": row[8]} if row[8] else None,
                "PaymentTermsRef": {"value": row[9]} if row[9] else None,
                "CreditLimit": float(row[10]) if row[10] else 0,
                "Balance": float(row[11]) if row[11] else 0,
                "Active": row[12],
                "MetaData": {
                    "CreateTime": row[13].isoformat() if hasattr(row[13], 'isoformat') else str(row[13]) if row[13] else None,
                    "LastUpdatedTime": row[14].isoformat() if hasattr(row[14], 'isoformat') else str(row[14]) if row[14] else None
                }
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "QueryResponse": {
                "Customer": customers,
                "maxResults": len(customers),
                "startPosition": int(offset)
            }
        })
        
    except Exception as e:
        import traceback
        print(f"Error in get_customers: {e}")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/v3/company/<company_id>/invoices', methods=['GET'])
def get_invoices(company_id):
    """Get invoices endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get query parameters
        limit = request.args.get('maxResults', 100)
        offset = request.args.get('startPosition', 0)
        
        cursor.execute('''
            SELECT id, doc_number, customer_id, customer_name, due_date, invoice_date,
                   status, subtotal, tax_amount, total_amount, balance, line_items, memo,
                   created_date, last_modified
            FROM qb_invoices
            ORDER BY created_date DESC
            LIMIT %s OFFSET %s
        ''', (int(limit), int(offset)))
        
        rows = cursor.fetchall()
        invoices = []
        
        for row in rows:
            invoices.append({
                "Id": row[0],
                "DocNumber": row[1],
                "CustomerRef": {"value": row[2]} if row[2] else None,
                "CustomerName": row[3],
                "DueDate": row[4].isoformat() if row[4] else None,
                "TxnDate": row[5].isoformat() if row[5] else None,
                "TxnStatus": row[6],
                "SubTotal": float(row[7]) if row[7] else 0,
                "TaxAmount": float(row[8]) if row[8] else 0,
                "TotalAmt": float(row[9]) if row[9] else 0,
                "Balance": float(row[10]) if row[10] else 0,
                "Line": row[11] if row[11] else [],
                "PrivateNote": row[12],
                "MetaData": {
                    "CreateTime": row[13].isoformat() if hasattr(row[13], 'isoformat') else str(row[13]) if row[13] else None,
                    "LastUpdatedTime": row[14].isoformat() if hasattr(row[14], 'isoformat') else str(row[14]) if row[14] else None
                }
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "QueryResponse": {
                "Invoice": invoices,
                "maxResults": len(invoices),
                "startPosition": int(offset)
            }
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/company/<company_id>/invoices', methods=['POST'])
def create_invoice(company_id):
    """Create invoice endpoint"""
    try:
        invoice_data = request.json
        
        # Simulate invoice creation
        new_invoice = {
            "Id": f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "DocNumber": invoice_data.get('DocNumber', f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"),
            "CustomerRef": invoice_data.get('CustomerRef', {}),
            "DueDate": invoice_data.get('DueDate'),
            "TxnDate": invoice_data.get('TxnDate'),
            "TxnStatus": invoice_data.get('TxnStatus', 'DRAFT'),
            "SubTotal": invoice_data.get('SubTotal', 0),
            "TaxAmount": invoice_data.get('TaxAmount', 0),
            "TotalAmt": invoice_data.get('TotalAmt', 0),
            "Balance": invoice_data.get('Balance', 0),
            "Line": invoice_data.get('Line', []),
            "PrivateNote": invoice_data.get('PrivateNote'),
            "MetaData": {
                "CreateTime": datetime.now().isoformat(),
                "LastUpdatedTime": datetime.now().isoformat()
            }
        }
        
        return jsonify({
            "QueryResponse": {
                "Invoice": [new_invoice]
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/v3/company/<company_id>/customers', methods=['POST'])
def create_customer(company_id):
    """Create customer endpoint"""
    try:
        customer_data = request.json
        
        # Simulate customer creation
        new_customer = {
            "Id": f"QB-CUST-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "Name": customer_data.get('Name', 'New Customer'),
            "Email": customer_data.get('Email'),
            "Phone": customer_data.get('Phone'),
            "Website": customer_data.get('Website'),
            "BillAddr": customer_data.get('BillAddr'),
            "ShipAddr": customer_data.get('ShipAddr'),
            "TaxIdentifier": customer_data.get('TaxIdentifier'),
            "CurrencyRef": customer_data.get('CurrencyRef', {"value": "USD"}),
            "PaymentTermsRef": customer_data.get('PaymentTermsRef', {"value": "Net 30"}),
            "CreditLimit": customer_data.get('CreditLimit', 0),
            "Balance": customer_data.get('Balance', 0),
            "Active": customer_data.get('Active', True),
            "MetaData": {
                "CreateTime": datetime.now().isoformat(),
                "LastUpdatedTime": datetime.now().isoformat()
            }
        }
        
        return jsonify({
            "QueryResponse": {
                "Customer": [new_customer]
            }
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
