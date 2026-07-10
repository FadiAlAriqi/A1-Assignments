import requests
import json
import time
import os
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError

# --- Configuration ---
FRAPPE_URL = "http://localhost"
API_KEY = "0dda264da6d23df"
API_SECRET = "64bb549295b1741"

KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092', '127.0.0.1:9094', '127.0.0.1:9095']
TICKET_TOPIC = "frappe_tickets"
CUSTOMER_TOPIC = "frappe_customers"

TICKET_WATERMARK_FILE = "frappe_tickets_watermark.txt"
CUSTOMER_WATERMARK_FILE = "frappe_customers_watermark.txt"

headers = {
    "Authorization": f"token {API_KEY}:{API_SECRET}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def ensure_kafka_topics_exist():
    """Dynamically verifies and creates required Frappe Kafka topics if missing."""
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            client_id='frappe_batch_admin'
        )
        
        existing_topics = admin_client.list_topics()
        required_topics = [TICKET_TOPIC, CUSTOMER_TOPIC]
        topics_to_create = []

        for topic in required_topics:
            if topic not in existing_topics:
                print(f"Notice: Topic '{topic}' not found. Preparing auto-generation...")
                # Creating topic with 3 partitions and replication factor of 1 for local multi-broker setup
                topics_to_create.append(NewTopic(name=topic, num_partitions=3, replication_factor=1))

        if topics_to_create:
            admin_client.create_topics(new_topics=topics_to_create, validate_only=False)
            print("Success: Missing Frappe Kafka topics generated successfully.")
        else:
            print("Status: All required Frappe Kafka topics verified and present.")
            
        admin_client.close()
    except TopicAlreadyExistsError:
        print("Status: Topics already exist, proceeding safely.")
    except Exception as e:
        print(f"Warning: KafkaAdminClient initialization or checking failed: {str(e)}")

def clean_html(html_text):
    """Strips HTML tags from Frappe rich text editor fields to output pure string data."""
    if not html_text: 
        return ""
    try:
        soup = BeautifulSoup(html_text, "html.parser")
        return soup.get_text()
    except Exception:
        return html_text

def get_watermark(filename):
    """Retrieves the last parsed modified execution state timestamp from local store."""
    if os.path.exists(filename):
        with open(filename, "r") as f:
            val = f.read().strip()
            if val: 
                return val
    return None

def save_watermark(filename, timestamp):
    """Commits the latest successfully synchronised high-watermark timestamp checkpoint."""
    with open(filename, "w") as f:
        f.write(str(timestamp))

def fetch_frappe_data(doctype, fields, watermark_file):
    """Polls the Frappe REST API resource dynamically using state-aware incremental filtering."""
    url = f"{FRAPPE_URL}/api/resource/{doctype}"
    last_watermark = get_watermark(watermark_file)
    
    if last_watermark:
        filters = [["modified", ">", last_watermark]]
        order_by = "modified asc"
    else:
        filters = []
        order_by = "creation asc"
        
    params = {
        "fields": json.dumps(fields),
        "filters": json.dumps(filters) if filters else None,
        "order_by": order_by,
        "limit_page_length": 1000
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        return response.json().get("data", []) if response.status_code == 200 else []
    except Exception as e:
        print(f"Error: Connection or retrieval failed for {doctype}: {str(e)}")
        return []

def main():
    # Enforce auto-generation of required streaming topics before initializing producers
    ensure_kafka_topics_exist()

    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            acks='all'
        )
        print("Success: Kafka Producer initialized successfully for Frappe Batch pipeline.")
    except Exception as e:
        print(f"Error: Failed to instantiate Kafka Producer cluster reference: {str(e)}")
        return

    print("Status: Polling loop activated. Synchronizing Frappe datasets every 1 minute...")
    while True:
        # A) Ingest and dispatch Frappe Ticket updates
        ticket_fields = ["name", "subject", "description", "raised_by", "status", "priority", "ticket_type", "customer", "_assign", "creation", "modified"]
        tickets = fetch_frappe_data("HD Ticket", ticket_fields, TICKET_WATERMARK_FILE)
        if tickets:
            print(f"Status: Ingesting {len(tickets)} new/updated ticket(s) from Frappe.")
            max_mod = get_watermark(TICKET_WATERMARK_FILE) or "2000-01-01 00:00:00.000000"
            for t in tickets:
                t["description"] = clean_html(t.get("description", ""))
                producer.send(TICKET_TOPIC, value=t)
                if t["modified"] > max_mod: 
                    max_mod = t["modified"]
            producer.flush()
            save_watermark(TICKET_WATERMARK_FILE, max_mod)

        # B) Ingest and dispatch Frappe Customer updates
        # NOTE: Fields align perfectly with the unified schema architecture using 'customer_name'
        customer_fields = ["name", "customer_name", "email_id", "mobile_no", "creation", "modified"]
        customers = fetch_frappe_data("HD Customer", customer_fields, CUSTOMER_WATERMARK_FILE)
        if customers:
            print(f"Status: Ingesting {len(customers)} new/updated customer(s) from Frappe.")
            max_mod = get_watermark(CUSTOMER_WATERMARK_FILE) or "2000-01-01 00:00:00.000000"
            for c in customers:
                # Payload mapping matches the downstream PySpark analytical core schema
                mapped_customer = {
                    "name": c["name"],
                    "customer_name": c.get("customer_name", ""), # Unified full name placeholder
                    "email_id": c.get("email_id", ""),
                    "mobile_no": c.get("mobile_no", "")
                }
                producer.send(CUSTOMER_TOPIC, value=mapped_customer)
                if c["modified"] > max_mod: 
                    max_mod = c["modified"]
            producer.flush()
            save_watermark(CUSTOMER_WATERMARK_FILE, max_mod)
            
        time.sleep(60)

if __name__ == "__main__":
    main()