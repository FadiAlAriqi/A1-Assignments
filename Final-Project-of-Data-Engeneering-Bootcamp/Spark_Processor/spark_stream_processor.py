from pyspark.sql import SparkSession
from pyspark.sql.functions import col, expr, from_json, to_json, current_timestamp, coalesce, lower, when, split, lit, regexp_replace
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType
import os

current_dir = os.path.abspath(os.path.dirname(__file__))
jar_path = os.path.join(current_dir, "clickhouse-jdbc-0.6.5-shaded.jar")

# Initialize Spark Session configured with Kafka and ClickHouse JDBC Drivers
spark = SparkSession.builder \
    .appName("Enriched-Support-Tickets-Pipeline") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1") \
    .config("spark.jars", jar_path) \
    .config("spark.sql.shuffle.partitions", "3") \
    .config("spark.driver.host", "127.0.0.1") \
    .config("spark.driver.bindAddress", "127.0.0.1") \
    .getOrCreate()

# Maintain terminal clarity by suppressing info/debug messages
spark.sparkContext.setLogLevel("WARN")

# --- Structured Schema Definitions ---

ticket_schema = StructType([
    StructField("name", StringType(), True),
    StructField("subject", StringType(), True),
    StructField("description", StringType(), True),
    StructField("raised_by", StringType(), True),
    StructField("status", StringType(), True),
    StructField("priority", StringType(), True),
    StructField("ticket_type", StringType(), True),
    StructField("customer", StringType(), True), 
    StructField("_assign", StringType(), True),
    StructField("creation", StringType(), True)
])

frappe_customer_schema = StructType([
    StructField("name", StringType(), True),          
    StructField("customer_name", StringType(), True), 
    StructField("email_id", StringType(), True),      
    StructField("mobile_no", StringType(), True)      
])

debezium_envelope_schema = StructType([
    StructField("payload", StructType([
        StructField("after", StructType([
            StructField("customer_id", IntegerType(), True),
            StructField("customer_name", StringType(), True), 
            StructField("email", StringType(), True),
            StructField("phone", StringType(), True)
        ]), True)
    ]), True)
])

KAFKA_BROKERS = "127.0.0.1:9092,127.0.0.1:9094,127.0.0.1:9095"

# --- Ingestion Sub-Pipelines ---

df_gen_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", "customer_tickets") \
    .option("startingOffsets", "earliest").load()

df_cdc_customers_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", "cdc.public.customers") \
    .option("startingOffsets", "earliest").load()

df_frappe_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", "frappe_tickets") \
    .option("startingOffsets", "earliest").load()

df_frappe_customers_raw = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BROKERS) \
    .option("subscribe", "frappe_customers") \
    .option("startingOffsets", "earliest").load()

# --- Parsing and Framing Raw Byte Values ---

df_gen_parsed = df_gen_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json("json_str", ticket_schema).alias("data")).select("data.*")

df_frappe_parsed = df_frappe_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json("json_str", ticket_schema).alias("data")).select("data.*")

df_cdc_customers_parsed = df_cdc_customers_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json("json_str", debezium_envelope_schema).alias("envelope")) \
    .select("envelope.payload.after.*").filter(col("customer_id").isNotNull())

df_frappe_customers_parsed = df_frappe_customers_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json("json_str", frappe_customer_schema).alias("data")).select("data.*")

# --- EventTime Watermarking Assignments ---

df_gen_ts = df_gen_parsed.withColumn("ticket_timestamp", col("creation").cast(TimestampType())) \
    .withWatermark("ticket_timestamp", "24 hours").dropDuplicates(["name", "ticket_timestamp"])

df_cdc_cust_ts = df_cdc_customers_parsed.withColumn("customer_id_str", col("customer_id").cast("string")) \
    .withColumn("customer_timestamp", current_timestamp()).withWatermark("customer_timestamp", "24 hours")

df_frappe_ts = df_frappe_parsed \
    .withColumn("creation_cleaned", coalesce(col("creation"), current_timestamp().cast("string"))) \
    .withColumn("ticket_timestamp", col("creation_cleaned").cast(TimestampType())) \
    .withWatermark("ticket_timestamp", "30 days")

df_frappe_cust_ts = df_frappe_customers_raw.selectExpr("CAST(value AS STRING) as json_str") \
    .select(from_json("json_str", frappe_customer_schema).alias("data")).select("data.*") \
    .withColumn("customer_timestamp", current_timestamp()).withWatermark("customer_timestamp", "30 days")

# --- Stateful Isolated Stream-to-Stream Joins ---

df_enriched_app = df_gen_ts.alias("tickets").join(
    df_cdc_cust_ts.alias("customers"),
    expr("tickets.customer = customers.customer_id_str"),
    how="inner"
).select(
    col("tickets.name").alias("ticket_id"), 
    col("tickets.subject"), 
    col("tickets.description"), 
    col("tickets.raised_by"),
    col("tickets.status"), 
    col("tickets.priority"), 
    col("tickets.ticket_type"), 
    col("tickets.ticket_timestamp"),
    col("tickets.ticket_timestamp").alias("ticket_created_at"), 
    col("tickets._assign"),
    col("customers.customer_id_str").alias("customer_id"), 
    col("customers.customer_name"),
    col("customers.email").alias("customer_email"), 
    col("customers.phone").alias("customer_phone")        
)

df_enriched_frappe = df_frappe_ts.alias("tickets").join(
    df_frappe_cust_ts.alias("customers"),
    expr("""
        tickets.customer = customers.name AND 
        tickets.ticket_timestamp >= customers.customer_timestamp - INTERVAL 30 DAYS AND 
        tickets.ticket_timestamp <= customers.customer_timestamp + INTERVAL 30 DAYS
    """),
    how="left" 
).select(
    col("tickets.name").alias("ticket_id"), 
    col("tickets.subject"), 
    col("tickets.description"), 
    col("tickets.raised_by"),
    col("tickets.status"), 
    col("tickets.priority"), 
    col("tickets.ticket_type"), 
    col("tickets.ticket_timestamp"),
    col("tickets.ticket_timestamp").alias("ticket_created_at"), 
    col("tickets._assign"),
    col("tickets.customer").alias("customer_id"), 
    col("customers.customer_name"),                        
    col("customers.email_id").alias("customer_email"), 
    col("customers.mobile_no").alias("customer_phone")        
)

# --- Merging Enriched Output Channels via Streaming Union ---
df_final_pipeline = df_enriched_app.union(df_enriched_frappe)

# --- Data Cleaning: Parsing & Cleaning the '_assign' Array Field ---
df_clean_agent = df_final_pipeline.withColumn(
    "assigned_agent",
    when(
        col("_assign").isNotNull() & (col("_assign") != "") & (col("_assign") != "[]"), 
        regexp_replace(regexp_replace(col("_assign"), r"""[\[\]"']""", ""), r"^\s+|\s+$", "")
    ).otherwise(lit("Unassigned"))
)

# --- Advanced Analytical Features Implementation ---
df_analyzed_pipeline = df_clean_agent \
    .withColumn("cleaned_description", lower(coalesce(col("description"), col("subject"), lit("")))) \
    .withColumn("ml_features", split(col("cleaned_description"), " ")) \
    .withColumn(
        "ml_prediction_score", 
        when(
            col("cleaned_description").contains("error") | 
            col("cleaned_description").contains("fail") | 
            col("cleaned_description").contains("bad") | 
            col("cleaned_description").contains("slow") | 
            col("cleaned_description").contains("broken") | 
            col("cleaned_description").contains("bug"), 
            0.15
        ).when(
            col("cleaned_description").contains("thank") | 
            col("cleaned_description").contains("success") | 
            col("cleaned_description").contains("good") | 
            col("cleaned_description").contains("solved") | 
            col("cleaned_description").contains("awesome"), 
            0.85
        ).otherwise(0.50)
    ) \
    .withColumn(
        "sentiment", 
        when(col("ml_prediction_score") < 0.40, "Negative")
        .when(col("ml_prediction_score") > 0.60, "Positive")
        .otherwise("Neutral")
    ) \
    .withColumn(
        "standardized_ticket_type", 
        coalesce(lower(col("ticket_type")), lit("unclassified"))
    )

# --- SLA Metrics Generation ---
df_metrics_pipeline = df_analyzed_pipeline \
    .withColumn("current_age_minutes", (current_timestamp().cast("long") - col("ticket_timestamp").cast("long")) / 60) \
    .select(
        col("ticket_id"), 
        col("subject"), 
        col("description"), 
        col("raised_by"), 
        col("status"), 
        col("priority"), 
        col("standardized_ticket_type").alias("ticket_type"), 
        col("assigned_agent"), 
        col("ml_features"), 
        col("ml_prediction_score"), 
        col("sentiment"),              
        col("ticket_created_at"), 
        col("current_age_minutes"),      
        col("customer_id"), 
        col("customer_name"), 
        col("customer_email"), 
        col("customer_phone")
    )

# --- Micro-Batch ClickHouse Micro-Engine Writer (ForeachBatch Strategy) ---
def write_to_clickhouse(batch_df, batch_id):
    # Convert array to clean string representation for JDBC standard protocol transmission
    db_ready_df = batch_df.withColumn("ml_features", to_json(col("ml_features")))
    clickhouse_url = "jdbc:clickhouse://127.0.0.1:8123/default"
    
    db_ready_df.write \
        .format("jdbc") \
        .option("url", clickhouse_url) \
        .option("dbtable", "enriched_tickets_stream") \
        .option("user", "default") \
        .option("password", "") \
        .option("driver", "com.clickhouse.jdbc.ClickHouseDriver") \
        .mode("append") \
        .save()

# --- Console Sink Streaming Execution via Micro-Batching Control ---
query = df_metrics_pipeline.writeStream \
    .foreachBatch(write_to_clickhouse) \
    .option("checkpointLocation", "./clickhouse_checkpoint") \
    .start()

print("Status: Advanced Micro-Batch Streaming Pipeline to ClickHouse established successfully...")
query.awaitTermination()