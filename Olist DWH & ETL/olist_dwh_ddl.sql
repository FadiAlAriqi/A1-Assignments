-- --- Dimension Tables ---

CREATE TABLE dim_date (
    date_key INT PRIMARY KEY,
    full_date DATE NOT NULL,
    day INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    quarter INT NOT NULL,
    weekday VARCHAR(20) NOT NULL
);

CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY,
    customer_id_nk VARCHAR(50) NOT NULL,
    customer_unique_id VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    state CHAR(2),
    zip_code_prefix INT
);

CREATE TABLE dim_seller (
    seller_key INT PRIMARY KEY,
    seller_id_nk VARCHAR(50) NOT NULL,
    city VARCHAR(100),
    state CHAR(2),
    zip_code_prefix INT
);

CREATE TABLE dim_product (
    product_key INT PRIMARY KEY,
    product_id_nk VARCHAR(50) NOT NULL,
    category_name VARCHAR(100),
    category_name_english VARCHAR(100),
    weight NUMERIC,
    length NUMERIC,
    product_height NUMERIC,
    product_width NUMERIC,
    photos_qty INT
);

CREATE TABLE dim_payment_type (
    payment_type_key INT PRIMARY KEY,
    payment_type VARCHAR(50) NOT NULL
);

CREATE TABLE dim_lead_source (
    lead_source_key INT PRIMARY KEY,
    landing_page_id VARCHAR(50),
    origin VARCHAR(50)
);

CREATE TABLE dim_business_segment (
    business_segment_key INT PRIMARY KEY,
    business_segment VARCHAR(100),
    lead_type VARCHAR(50)
);

-- --- Fact Tables ---

CREATE TABLE fact_sales (
    sales_key INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL, 
    order_item_id INT NOT NULL,    
    product_key INT REFERENCES dim_product(product_key),
    customer_key INT REFERENCES dim_customer(customer_key),
    seller_key INT REFERENCES dim_seller(seller_key),
    order_date_key INT REFERENCES dim_date(date_key),
    shipping_limit_date_key INT REFERENCES dim_date(date_key),
    quantity INT DEFAULT 1,
    unit_price NUMERIC(10, 2),
    freight_value NUMERIC(10, 2),
    total_price NUMERIC(10, 2)
);

CREATE TABLE fact_payments (
    payment_key INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL, 
    customer_key INT REFERENCES dim_customer(customer_key),
    payment_date_key INT REFERENCES dim_date(date_key),
    payment_type_key INT REFERENCES dim_payment_type(payment_type_key),
    payment_value NUMERIC(10, 2),
    payment_installments INT
);

CREATE TABLE fact_delivery (
    delivery_key INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL, 
    customer_key INT REFERENCES dim_customer(customer_key),
    seller_key INT REFERENCES dim_seller(seller_key),
    order_date_key INT REFERENCES dim_date(date_key),
    approved_date_key INT REFERENCES dim_date(date_key),
    delivered_date_key INT REFERENCES dim_date(date_key),
    estimated_date_key INT REFERENCES dim_date(date_key),
    delivery_time_days INT,
    delivery_delay_days INT,
    is_delayed INT
);

CREATE TABLE fact_reviews (
    review_key INT PRIMARY KEY,
    order_id VARCHAR(50) NOT NULL, 
    customer_key INT REFERENCES dim_customer(customer_key),
    review_date_key INT REFERENCES dim_date(date_key),
    review_score INT,
    has_comment INT
);

CREATE TABLE fact_leads (
    lead_key INT PRIMARY KEY,
    mql_id VARCHAR(50) NOT NULL, 
    seller_key INT REFERENCES dim_seller(seller_key),
    lead_source_key INT REFERENCES dim_lead_source(lead_source_key),
    business_segment_key INT REFERENCES dim_business_segment(business_segment_key),
    first_contact_date_key INT REFERENCES dim_date(date_key),
    won_date_key INT REFERENCES dim_date(date_key),
    is_won INT,
    has_company INT,
    has_gtin INT,
    average_stock VARCHAR(50),
    declared_product_catalog_size NUMERIC,
    declared_monthly_revenue NUMERIC
);

-- --- Indexes for Performance ---

-- Fact Sales Indexes
CREATE INDEX idx_fact_sales_order_date ON fact_sales(order_date_key);
CREATE INDEX idx_fact_sales_product ON fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer ON fact_sales(customer_key);
CREATE INDEX idx_fact_sales_seller ON fact_sales(seller_key);

-- Fact Payments Indexes
CREATE INDEX idx_fact_payments_date ON fact_payments(payment_date_key);
CREATE INDEX idx_fact_payments_customer ON fact_payments(customer_key);

-- Fact Delivery Indexes
CREATE INDEX idx_fact_delivery_order_date ON fact_delivery(order_date_key);
CREATE INDEX idx_fact_delivery_customer ON fact_delivery(customer_key);

-- Fact Leads Indexes
CREATE INDEX idx_fact_leads_contact_date ON fact_leads(first_contact_date_key);
CREATE INDEX idx_fact_leads_seller ON fact_leads(seller_key);

-- Dimension Indexes (NKs)
CREATE INDEX idx_dim_customer_id ON dim_customer(customer_id_nk);
CREATE INDEX idx_dim_seller_id ON dim_seller(seller_id_nk);
CREATE INDEX idx_dim_product_id ON dim_product(product_id_nk);
