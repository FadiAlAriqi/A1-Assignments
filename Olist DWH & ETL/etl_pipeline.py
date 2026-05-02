import pandas as pd
import sqlite3
from sqlalchemy import create_engine, text
from datetime import datetime
import os
from typing import List, Optional
from pydantic import BaseModel, Field

SQLITE_DB_PATH = './olist.sqlite'
POSTGRES_CONN_STR = 'postgresql://postgres:$her10ck@localhost:5432/olist_dwh'

class DateDim(BaseModel):
    date_key: int
    full_date: datetime
    day: int
    month: int
    year: int
    quarter: int
    weekday: str

class OlistETL:
    def __init__(self, source_db: str, target_conn: str):
        self.source_db = source_db
        self.target_engine = create_engine(target_conn)
        self.source_conn = sqlite3.connect(source_db)

    def extract_table(self, table_name: str) -> pd.DataFrame:
        """Extracts data from the source SQLite database."""
        print(f"Extracting {table_name}...")
        return pd.read_sql_query(f"SELECT * FROM {table_name}", self.source_conn)

    def load_table(self, df: pd.DataFrame, table_name: str):
        """Loads data into the target database."""
        print(f"Loading {table_name}...")
        df.to_sql(table_name, self.target_engine, if_exists='replace', index=False)

    def create_dim_date(self, start_date: str, end_date: str):
        """Generates and loads the date dimension."""
        print("Generating dim_date...")
        date_range = pd.date_range(start=start_date, end=end_date)
        df_date = pd.DataFrame({'full_date': date_range})
        df_date['date_key'] = df_date['full_date'].dt.strftime('%Y%m%d').astype(int)
        df_date['day'] = df_date['full_date'].dt.day
        df_date['month'] = df_date['full_date'].dt.month
        df_date['year'] = df_date['full_date'].dt.year
        df_date['quarter'] = df_date['full_date'].dt.quarter
        df_date['weekday'] = df_date['full_date'].dt.day_name()
        
        self.load_table(df_date, 'dim_date')

    def transform_dimensions(self):
        """Transforms and loads dimension tables."""
        df_cust = self.extract_table('customers')
        df_cust = df_cust.rename(columns={
            'customer_id': 'customer_id_nk',
            'customer_zip_code_prefix': 'zip_code_prefix',
            'customer_city': 'city',
            'customer_state': 'state'
        })
        df_cust['customer_key'] = range(1, len(df_cust) + 1)
        self.load_table(df_cust[['customer_key', 'customer_id_nk', 'customer_unique_id', 'city', 'state', 'zip_code_prefix']], 'dim_customer')

        df_seller = self.extract_table('sellers')
        df_seller = df_seller.rename(columns={
            'seller_id': 'seller_id_nk',
            'seller_zip_code_prefix': 'zip_code_prefix',
            'seller_city': 'city',
            'seller_state': 'state'
        })
        df_seller['seller_key'] = range(1, len(df_seller) + 1)
        self.load_table(df_seller[['seller_key', 'seller_id_nk', 'city', 'state', 'zip_code_prefix']], 'dim_seller')

        df_prod = self.extract_table('products')
        df_trans = self.extract_table('product_category_name_translation')
        df_prod = df_prod.merge(df_trans, on='product_category_name', how='left')
        df_prod = df_prod.rename(columns={
            'product_id': 'product_id_nk',
            'product_category_name': 'category_name',
            'product_weight_g': 'weight',
            'product_length_cm': 'length',
            'product_height_cm': 'product_height',
            'product_width_cm': 'product_width',
            'product_photos_qty': 'photos_qty'
        })
        df_prod['product_key'] = range(1, len(df_prod) + 1)
        self.load_table(df_prod[['product_key', 'product_id_nk', 'category_name', 'product_category_name_english', 'weight', 'length', 'product_height', 'product_width', 'photos_qty']], 'dim_product')

        df_pay_type = self.extract_table('order_payments')[['payment_type']].drop_duplicates()
        df_pay_type['payment_type_key'] = range(1, len(df_pay_type) + 1)
        self.load_table(df_pay_type, 'dim_payment_type')

        df_lq = self.extract_table('leads_qualified')
        df_ls = df_lq[['landing_page_id', 'origin']].drop_duplicates()
        df_ls['lead_source_key'] = range(1, len(df_ls) + 1)
        self.load_table(df_ls, 'dim_lead_source')

        df_lc = self.extract_table('leads_closed')
        df_bs = df_lc[['business_segment', 'lead_type']].drop_duplicates()
        df_bs['business_segment_key'] = range(1, len(df_bs) + 1)
        self.load_table(df_bs, 'dim_business_segment')

    def transform_facts(self):
        """Transforms and loads fact tables."""
        dim_cust = pd.read_sql("SELECT customer_key, customer_id_nk FROM dim_customer", self.target_engine)
        dim_seller = pd.read_sql("SELECT seller_key, seller_id_nk FROM dim_seller", self.target_engine)
        dim_prod = pd.read_sql("SELECT product_key, product_id_nk FROM dim_product", self.target_engine)
        dim_pay_type = pd.read_sql("SELECT payment_type_key, payment_type FROM dim_payment_type", self.target_engine)
        dim_ls = pd.read_sql("SELECT lead_source_key, landing_page_id, origin FROM dim_lead_source", self.target_engine)
        dim_bs = pd.read_sql("SELECT business_segment_key, business_segment, lead_type FROM dim_business_segment", self.target_engine)

        def to_date_key(date_series):
            return pd.to_datetime(date_series).dt.strftime('%Y%m%d').fillna(0).astype(int)

        df_items = self.extract_table('order_items')
        df_orders = self.extract_table('orders')
        df_sales = df_items.merge(df_orders, on='order_id', how='inner')
        df_sales = df_sales.merge(dim_cust, left_on='customer_id', right_on='customer_id_nk', how='left')
        df_sales = df_sales.merge(dim_seller, left_on='seller_id', right_on='seller_id_nk', how='left')
        df_sales = df_sales.merge(dim_prod, left_on='product_id', right_on='product_id_nk', how='left')
        
        df_sales['order_date_key'] = to_date_key(df_sales['order_purchase_timestamp'])
        df_sales['shipping_limit_date_key'] = to_date_key(df_sales['shipping_limit_date'])
        df_sales['quantity'] = 1
        df_sales['unit_price'] = df_sales['price']
        df_sales['total_price'] = df_sales['price'] + df_sales['freight_value']
        df_sales['sales_key'] = range(1, len(df_sales) + 1)
        
        self.load_table(df_sales[['sales_key', 'order_id', 'order_item_id', 'product_key', 'customer_key', 'seller_key', 'order_date_key', 'shipping_limit_date_key', 'quantity', 'unit_price', 'freight_value', 'total_price']], 'fact_sales')

        df_pay = self.extract_table('order_payments')
        df_pay = df_pay.merge(df_orders, on='order_id', how='inner')
        df_pay = df_pay.merge(dim_cust, left_on='customer_id', right_on='customer_id_nk', how='left')
        df_pay = df_pay.merge(dim_pay_type, on='payment_type', how='left')
        
        df_pay['payment_date_key'] = to_date_key(df_pay['order_purchase_timestamp'])
        df_pay['payment_key'] = range(1, len(df_pay) + 1)
        
        self.load_table(df_pay[['payment_key', 'order_id', 'customer_key', 'payment_date_key', 'payment_type_key', 'payment_value', 'payment_installments']], 'fact_payments')

        df_del = df_orders.copy()
        df_seller_map = df_items[['order_id', 'seller_id']].drop_duplicates(subset='order_id')
        df_del = df_del.merge(df_seller_map, on='order_id', how='left')
        df_del = df_del.merge(dim_cust, left_on='customer_id', right_on='customer_id_nk', how='left')
        df_del = df_del.merge(dim_seller, left_on='seller_id', right_on='seller_id_nk', how='left')
        
        df_del['order_date_key'] = to_date_key(df_del['order_purchase_timestamp'])
        df_del['approved_date_key'] = to_date_key(df_del['order_approved_at'])
        df_del['delivered_date_key'] = to_date_key(df_del['order_delivered_customer_date'])
        df_del['estimated_date_key'] = to_date_key(df_del['order_estimated_delivery_date'])
        
        t_approved = pd.to_datetime(df_del['order_approved_at'])
        t_delivered = pd.to_datetime(df_del['order_delivered_customer_date'])
        t_estimated = pd.to_datetime(df_del['order_estimated_delivery_date'])
        
        df_del['delivery_time_days'] = (t_delivered - t_approved).dt.days
        df_del['delivery_delay_days'] = (t_delivered - t_estimated).dt.days.clip(lower=0)
        df_del['is_delayed'] = (df_del['delivery_delay_days'] > 0).astype(int)
        df_del['delivery_key'] = range(1, len(df_del) + 1)
        
        self.load_table(df_del[['delivery_key', 'order_id', 'customer_key', 'seller_key', 'order_date_key', 'approved_date_key', 'delivered_date_key', 'estimated_date_key', 'delivery_time_days', 'delivery_delay_days', 'is_delayed']], 'fact_delivery')

        df_rev = self.extract_table('order_reviews')
        df_rev = df_rev.merge(df_orders, on='order_id', how='inner')
        df_rev = df_rev.merge(dim_cust, left_on='customer_id', right_on='customer_id_nk', how='left')
        
        df_rev['review_date_key'] = to_date_key(df_rev['review_creation_date'])
        df_rev['has_comment'] = df_rev['review_comment_message'].notnull().astype(int)
        df_rev['review_key'] = range(1, len(df_rev) + 1)
        
        self.load_table(df_rev[['review_key', 'order_id', 'customer_key', 'review_date_key', 'review_score', 'has_comment']], 'fact_reviews')

        df_lq = self.extract_table('leads_qualified')
        df_lc = self.extract_table('leads_closed')
        df_leads = df_lq.merge(df_lc, on='mql_id', how='left')
        
        df_leads = df_leads.merge(dim_seller, left_on='seller_id', right_on='seller_id_nk', how='left')
        df_leads = df_leads.merge(dim_ls, on=['landing_page_id', 'origin'], how='left')
        df_leads = df_leads.merge(dim_bs, on=['business_segment', 'lead_type'], how='left')
        
        df_leads['first_contact_date_key'] = to_date_key(df_leads['first_contact_date'])
        df_leads['won_date_key'] = to_date_key(df_leads['won_date'])
        df_leads['is_won'] = df_leads['won_date'].notnull().astype(int)
        df_leads['lead_key'] = range(1, len(df_leads) + 1)
        
        self.load_table(df_leads[['lead_key', 'mql_id', 'seller_key', 'lead_source_key', 'business_segment_key', 'first_contact_date_key', 'won_date_key', 'is_won', 'has_company', 'has_gtin', 'average_stock', 'declared_product_catalog_size', 'declared_monthly_revenue']], 'fact_leads')

    def reset_schema(self):
        with self.target_engine.connect() as conn:
            conn.execute(text("""
                DROP TABLE IF EXISTS fact_leads CASCADE;
                DROP TABLE IF EXISTS fact_reviews CASCADE;
                DROP TABLE IF EXISTS fact_delivery CASCADE;
                DROP TABLE IF EXISTS fact_payments CASCADE;
                DROP TABLE IF EXISTS fact_sales CASCADE;

                DROP TABLE IF EXISTS dim_business_segment CASCADE;
                DROP TABLE IF EXISTS dim_lead_source CASCADE;
                DROP TABLE IF EXISTS dim_payment_type CASCADE;
                DROP TABLE IF EXISTS dim_product CASCADE;
                DROP TABLE IF EXISTS dim_seller CASCADE;
                DROP TABLE IF EXISTS dim_customer CASCADE;
                DROP TABLE IF EXISTS dim_date CASCADE;
            """))
            conn.commit()

    def run(self):
        """Executes the full ETL pipeline."""
        print("Starting ETL Pipeline...")
        self.reset_schema()
        self.create_dim_date('2016-01-01', '2019-12-31')
        self.transform_dimensions()
        self.transform_facts()
        print("ETL Pipeline completed successfully.")

if __name__ == "__main__":
    etl = OlistETL(SQLITE_DB_PATH, POSTGRES_CONN_STR)
    etl.run()
