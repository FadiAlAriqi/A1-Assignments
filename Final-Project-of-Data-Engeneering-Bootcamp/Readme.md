# Real-Time Data Engineering Pipeline

A comprehensive data engineering project aimed at building an advanced real-time data processing pipeline. This system integrates **Change Data Capture (CDC)**, stream processing, and big data analytics. It synchronizes customer data from PostgreSQL, generates and processes support tickets via Spark Streaming, and then stores them in ClickHouse for immediate analysis and visualization through Grafana.

---

## 🛠️ Tools and Technologies (Stack)

The tools were carefully selected to ensure high performance and scalability, with specific versions identified to guarantee environment stability:

| Tool | Version | Description |
| --- | --- | --- |
| **PostgreSQL** | `16-alpine` | The primary database for storing customer and agent data. |
| **ClickHouse** | `24.3-alpine` | An analytical engine (OLAP) for storing and processing large volumes of data at high speed. |
| **Apache Kafka** | `3.7.0` | A message broker for transmitting data between systems. |
| **Kafka UI** | `latest` | A graphical interface for managing and monitoring Kafka topics. |
| **Debezium Connect** | `2.5` | A CDC tool for monitoring changes in PostgreSQL and streaming them to Kafka. |
| **Apache Spark** | `3.5.1` | A data processing engine (Spark Streaming) for real-time transformation and analysis. |
| **Grafana** | `10.4.1` | A data visualization platform for building interactive dashboards. |
| **Python** | `3.14.3` | The programming language used for writing Spark processors and data generators. |

---

## 🏗️ System Architecture

1. **Data Source:** Customer data is ingested into **PostgreSQL**.

1. **Change Data Capture (CDC):** **Debezium** monitors changes in PostgreSQL and sends them to **Kafka**.

1. **Ticket Generation:** A **Python** application generates real-time support tickets.

1. **Processing:** **Spark Streaming** pulls data from Kafka, enriches it, and pushes it to **ClickHouse**.

1. **Storage and Analysis:** Data is organized in ClickHouse using **Materialized Views** to optimize queries.

1. **Visualization:** Results and analytics are displayed via **Grafana**.

---

## 🚀 Setup Instructions

### 1. Environment Setup with Docker

Ensure you have a `docker-compose.yml` file in the root directory, then use the following commands:

- **To start all services in the background:**

   ```bash
   docker-compose up -d
   ```

- **To check the status of containers:**

   ```bash
   docker-compose ps
   ```

- **To stop all services:**

   ```bash
   docker-compose down
   ```

### 2. Python Environment & Requirements

This project is developed using **Python 3.14.3**. It is highly recommended to use a virtual environment (`venv`) to manage dependencies.

- **Create and Activate Virtual Environment:**

   ```bash
   # Create a virtual environment
   python -m venv venv
   
   # Activate on Windows
   .\venv\Scripts\activate
   
   # Activate on Linux/macOS
   source venv/bin/activate
   ```

- **Install All Dependencies in One Command:**

   Ensure you have a `requirements.txt` file with the following content:

   ```
   fastapi==0.138.1
   uvicorn==0.49.0
   kafka-python==3.0.7
   faker==40.23.0
   pydantic==2.13.4
   ```

   Then run:

   ```bash
   pip install -r requirements.txt
   ```

### 3. ClickHouse Setup (Analytical Engine)

Execute the following queries in ClickHouse to create the necessary tables:

```sql
-- 1. Raw Data Ingestion Buffer Table
CREATE TABLE enriched_tickets_stream
(
    ticket_id String,
    subject String,
    description String,
    raised_by String,
    status String,
    priority String,
    ticket_type String,
    assigned_agent String,
    ml_features String,
    ml_prediction_score Float32,
    sentiment String,
    ticket_created_at DateTime64(3),
    current_age_minutes Float64,
    customer_id String,
    customer_name String,
    customer_email String,
    customer_phone String,
    processed_at DateTime DEFAULT now()
)
ENGINE = ReplacingMergeTree(processed_at)
PARTITION BY toYYYYMM(ticket_created_at)
PRIMARY KEY ticket_id
ORDER BY (ticket_id, ticket_created_at);

-- 2. Optimized Analytical Engine Table
CREATE TABLE enriched_tickets_analytics
(
    ticket_id String,
    subject String,
    description String,
    raised_by String,
    status String,
    priority String,
    ticket_type String,
    assigned_agent String,
    ml_features Array(String),
    ml_prediction_score Float32,
    sentiment String,
    ticket_created_at DateTime64(3),
    current_age_minutes Float64,
    customer_id String,
    customer_name String,
    customer_email String,
    customer_phone String,
    processed_at DateTime
)
ENGINE = ReplacingMergeTree(processed_at)
PARTITION BY toYYYYMM(ticket_created_at)
PRIMARY KEY ticket_id
ORDER BY (ticket_id, ticket_created_at);

-- 3. Materialized View for on-the-fly JSON Parsing and Flattening
CREATE MATERIALIZED VIEW mv_enriched_tickets_to_analytics
TO enriched_tickets_analytics AS
SELECT
    ticket_id, subject, description, raised_by, status, priority, ticket_type, assigned_agent,
    JSONExtract(ml_features, 'Array(String)') AS ml_features,
    ml_prediction_score, sentiment, ticket_created_at, current_age_minutes,
    customer_id, customer_name, customer_email, customer_phone, processed_at
FROM enriched_tickets_stream;
```

### 4. PostgreSQL and Debezium Setup

Enable CDC feature to allow Debezium to read updates:

```sql
-- Enable full replica identity (critical for UPDATE/DELETE operations)
ALTER TABLE customers REPLICA IDENTITY FULL;

CREATE TABLE customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE agents (
    agent_id SERIAL PRIMARY KEY,
    agent_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO customers (customer_name, email, phone) VALUES
    ('Fadi Al-Ariqi', 'f.ariqi.x@gmail.com', '784358000'),
    ('Ahmed Mojali', 'ahmed@gmail.com', '779769654'),
    ('Zakaria Gaghman', 'zakaria@gmail.com', '735689942'),
    ('Emad Al-Qadasi', 'sofian@gmail.com', '774545587');

INSERT INTO agents (agent_name, email) VALUES
    ('Ali Mansoor', 'ali.mansoor@support.com'),
    ('Sarah Ahmed', 'sarah.ahmed@support.com'),
    ('Khaled Omar', 'khaled.omar@support.com'),
    ('Arwa Al-Sanaani', 'arwa.sanaani@support.com');
```

Then, register the Debezium Connector via an API call (example using CMD):

```bash
curl -X POST -H "Content-Type: application/json" --data "{\"name\": \"postgres-cdc-connector\", \"config\": {\"connector.class\": \"io.debezium.connector.postgresql.PostgresConnector\", \"tasks.max\": \"1\", \"plugin.name\": \"pgoutput\", \"database.hostname\": \"postgres\", \"database.port\": \"5432\", \"database.user\": \"de_user\", \"database.password\": \"de_password\", \"database.dbname\": \"customers_db\", \"database.server.name\": \"postgres\", \"topic.prefix\": \"cdc\", \"table.include.list\": \"public.customers\"}}" http://localhost:8083/connectors
```

### 5. Running Data Processing Pipelines

The pipelines are run in a specific order:

1. **Ticket Generator:** To start data ingestion.

1. **Historical Batch Sync Pipeline:** (Optional ) For synchronizing historical data.

1. **Spark Stream Processor:** For stream processing.

```bash
# 1. Run Real-Time Ingestion Pipe
cd ..\"Tickets Generator"\
python .\app.py

# 2. Run Historical Batch Sync Pipeline (Ensure Frappe is Up with Valid API Token)
python .\frappe_batch_ingest.py

# 3. Run Spark Streaming Processor
cd .\Spark_Processor\
Remove-Item -Recurse -Force .\clickhouse_checkpoint
python .\spark_stream_processor.py
```

---

## 📊 System Monitoring and Validation

You can verify data ingestion and integrity by executing the following queries in ClickHouse:

```sql
-- Count total processed tickets
SELECT count(*) FROM enriched_tickets_stream;
SELECT count(*) FROM enriched_tickets_analytics;

-- View the latest analyzed tickets
SELECT * FROM enriched_tickets_analytics ORDER BY processed_at DESC LIMIT 30;
```

---

> **Note:** This project is designed for educational and practical purposes in data engineering. Please ensure that environment configuration files (.env) are properly set up and linked before operation.