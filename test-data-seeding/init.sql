-- Database initialization for test data seeding

-- QuickBooks tables
CREATE TABLE IF NOT EXISTS qb_customers (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    website VARCHAR(255),
    billing_address JSONB,
    shipping_address JSONB,
    tax_id VARCHAR(50),
    currency VARCHAR(10) DEFAULT 'USD',
    payment_terms VARCHAR(50),
    credit_limit DECIMAL(15,2),
    balance DECIMAL(15,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS qb_invoices (
    id VARCHAR(50) PRIMARY KEY,
    doc_number VARCHAR(50) UNIQUE NOT NULL,
    customer_id VARCHAR(50) REFERENCES qb_customers(id),
    customer_name VARCHAR(255),
    due_date TIMESTAMP,
    invoice_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'DRAFT',
    subtotal DECIMAL(15,2) DEFAULT 0,
    tax_amount DECIMAL(15,2) DEFAULT 0,
    total_amount DECIMAL(15,2) DEFAULT 0,
    balance DECIMAL(15,2) DEFAULT 0,
    line_items JSONB,
    memo TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Salesforce tables
CREATE TABLE IF NOT EXISTS sf_accounts (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(100),
    industry VARCHAR(100),
    annual_revenue DECIMAL(15,2),
    number_of_employees INTEGER,
    phone VARCHAR(50),
    website VARCHAR(255),
    billing_address JSONB,
    shipping_address JSONB,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id VARCHAR(50),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS sf_contacts (
    id VARCHAR(50) PRIMARY KEY,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(50),
    mobile_phone VARCHAR(50),
    title VARCHAR(100),
    department VARCHAR(100),
    account_id VARCHAR(50) REFERENCES sf_accounts(id),
    account_name VARCHAR(255),
    mailing_address JSONB,
    description TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id VARCHAR(50),
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS sf_opportunities (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    account_id VARCHAR(50) REFERENCES sf_accounts(id),
    account_name VARCHAR(255),
    amount DECIMAL(15,2),
    stage_name VARCHAR(100),
    probability INTEGER,
    close_date TIMESTAMP,
    lead_source VARCHAR(100),
    type VARCHAR(100),
    forecast_category VARCHAR(100),
    description TEXT,
    next_step TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    owner_id VARCHAR(50),
    is_won BOOLEAN DEFAULT false,
    is_closed BOOLEAN DEFAULT false
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_qb_invoices_customer_id ON qb_invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_qb_invoices_status ON qb_invoices(status);
CREATE INDEX IF NOT EXISTS idx_sf_contacts_account_id ON sf_contacts(account_id);
CREATE INDEX IF NOT EXISTS idx_sf_opportunities_account_id ON sf_opportunities(account_id);
CREATE INDEX IF NOT EXISTS idx_sf_opportunities_stage ON sf_opportunities(stage_name);

-- Insert some sample data for testing
INSERT INTO qb_customers (id, name, email, phone, currency, payment_terms, credit_limit, is_active) 
VALUES 
    ('QB-CUST-000001', 'Acme Corporation', 'contact@acme.com', '+1-555-0101', 'USD', 'Net 30', 50000.00, true),
    ('QB-CUST-000002', 'TechStart Inc', 'info@techstart.com', '+1-555-0102', 'USD', 'Net 15', 25000.00, true)
ON CONFLICT (id) DO NOTHING;

INSERT INTO sf_accounts (id, name, type, industry, annual_revenue, number_of_employees, phone, is_active)
VALUES 
    ('ACC-000001', 'Global Solutions Ltd', 'Customer - Direct', 'Technology', 5000000.00, 500, '+1-555-0201', true),
    ('ACC-000002', 'Innovation Partners', 'Customer - Channel', 'Healthcare', 2500000.00, 200, '+1-555-0202', true)
ON CONFLICT (id) DO NOTHING;
