import json
import random
import time
import threading
from datetime import datetime, timezone
import psycopg2
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
from faker import Faker

# --- Constants & Configuration ---
KAFKA_BOOTSTRAP_SERVERS = ['127.0.0.1:9092', '127.0.0.1:9094', '127.0.0.1:9095']
KAFKA_TICKET_TOPIC = "customer_tickets"
DB_URI = "postgresql://de_user:de_password@127.0.0.1:5433/customers_db"

CATEGORIES = ["Payment", "Account Access", "Technical Bug", "Delivery", "Refund", "Incident", "Question", "Unspecified"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]
STATUSES = ["Open", "Replied", "Resolved", "Closed"]

SAMPLE_SUBJECTS = ["Payment Gateway Error", "Account Locked Out", "Application Crash during Checkout", "Missing Delivery Order", "Double Charge on Subscription"]
SAMPLE_DESCRIPTIONS = [
    "I am extremely frustrated! My payment went through but my account is still locked.",
    "The application crashes every time I try to check out. Fix this bug!",
    "Thank you for the quick response, but I still haven't received my refund.",
    "Your service is terrible. I've been waiting for my delivery for 5 days.",
    "I need urgent help changing my account email address. It keeps throwing an error."
]

fake = Faker()
app = FastAPI(title="Customer Support Analytics Pipeline - Ingestion API")

def get_actual_db_data():
    """Fetch real customer data and agent names directly from PostgreSQL."""
    customers = []
    agents = []
    try:
        with psycopg2.connect(DB_URI) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT customer_id, customer_name, email FROM customers;")
                c_rows = cur.fetchall()
                customers = [{"customer_id": str(r[0]), "customer_name": r[1], "email": r[2]} for r in c_rows] if c_rows else []
                
                cur.execute("SELECT agent_name FROM agents;")
                a_rows = cur.fetchall()
                agents = [r[0] for r in a_rows] if a_rows else []
    except Exception as e:
        print(f"Warning: Could not fetch from Postgres (Using Faker backup): {e}")
    return customers, agents

def ensure_kafka_topic_exists():
    try:
        admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, client_id='api_admin_client', request_timeout_ms=5000)
        new_topic = NewTopic(name=KAFKA_TICKET_TOPIC, num_partitions=3, replication_factor=3)
        admin_client.create_topics(new_topics=[new_topic], validate_only=False)
    except TopicAlreadyExistsError:
        pass
    except Exception as e:
        print(f"Warning during topic verification/creation: {e}")

ensure_kafka_topic_exists()

try:
    producer = KafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, value_serializer=lambda v: json.dumps(v).encode('utf-8'), acks='all')
except Exception as e:
    print(f"Failed to connect to Kafka HA Cluster: {e}")
    producer = None

# --- Background Continuous Ticket Generator ---
def continuous_ticket_generator():
    print("Background Continuous Ticket Generator has started with DB synchronization...")
    while True:
        if producer:
            try:
                ensure_kafka_topic_exists()
                db_customers, db_agents = get_actual_db_data()
                
                if db_customers:
                    selected_customer = random.choice(db_customers)
                    customer_id = selected_customer["customer_id"]
                    customer_name = selected_customer["customer_name"]
                    customer_email = selected_customer["email"]
                    log_prefix = "[DB Synchronized Stream]"
                else:
                    customer_id = str(fake.random_int(min=100, max=999))
                    customer_name = fake.name()
                    customer_email = fake.email()
                    log_prefix = "[Faker Fallback Stream]"
                
                assigned_agent = random.choice(db_agents) if db_agents else random.choice(['Ali Mansoor', 'Sarah Ahmed', 'Khaled Omar', 'Arwa Al-Sanaani'])
                
                ticket_data = {
                    "name": f"TICK-{fake.unique.random_int(min=10000, max=99999)}",
                    "subject": random.choice(SAMPLE_SUBJECTS),
                    "description": random.choice(SAMPLE_DESCRIPTIONS),
                    "raised_by": customer_email,
                    "status": random.choice(STATUSES),
                    "priority": random.choice(PRIORITIES),
                    "ticket_type": random.choice(CATEGORIES),
                    "customer": customer_id,  
                    "_assign": json.dumps([assigned_agent]),
                    "creation": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
                }
                producer.send(KAFKA_TICKET_TOPIC, value=ticket_data)
                producer.flush()
                print(f"{log_prefix} Sent Ticket {ticket_data['name']} assigned to '{assigned_agent}' with status '{ticket_data['status']}'")
            except Exception as e:
                print(f"Error in background generator: {e}")
        time.sleep(random.uniform(5.0, 20.0))

generator_thread = threading.Thread(target=continuous_ticket_generator, daemon=True)
generator_thread.start()

# --- API Models & Endpoints ---
class TicketModel(BaseModel):
    name: str
    subject: str
    description: str
    raised_by: str
    status: str
    priority: str
    ticket_type: str
    customer: str
    _assign: str
    creation: str

@app.post("/api/tickets/send")
def send_ticket(ticket: TicketModel):
    if not producer: 
        raise HTTPException(status_code=500, detail="Kafka Producer is not available")
    try:
        ensure_kafka_topic_exists()
        ticket_dict = ticket.model_dump()
        producer.send(KAFKA_TICKET_TOPIC, value=ticket_dict)
        producer.flush()
        return {"status": "Success", "message": "Ticket ingested into Kafka successfully", "data": ticket_dict}
    except Exception as e: 
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/tickets/simulate/{count}")
def simulate_tickets(count: int):
    if not producer:
        raise HTTPException(status_code=500, detail="Kafka Producer is not available")
    
    try:
        ensure_kafka_topic_exists()
        db_customers, db_agents = get_actual_db_data()
        generated_tickets = []

        for _ in range(count):
            if db_customers:
                selected_customer = random.choice(db_customers)
                customer_id = selected_customer["customer_id"]
                customer_name = selected_customer["customer_name"]
                customer_email = selected_customer["email"]
            else:
                customer_id = str(fake.random_int(min=100, max=999))
                customer_name = fake.name()
                customer_email = fake.email()

            assigned_agent = random.choice(db_agents) if db_agents else random.choice(['Ali Mansoor', 'Sarah Ahmed', 'Khaled Omar', 'Arwa Al-Sanaani'])

            ticket_data = {
                "name": f"TICK-{fake.unique.random_int(min=10000, max=99999)}",
                "subject": random.choice(SAMPLE_SUBJECTS),
                "description": random.choice(SAMPLE_DESCRIPTIONS),
                "raised_by": customer_email,
                "status": random.choice(STATUSES),
                "priority": random.choice(PRIORITIES),
                "ticket_type": random.choice(CATEGORIES),
                "customer": customer_id,
                "_assign": json.dumps([assigned_agent]),
                "creation": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S.%f")
            }
            producer.send(KAFKA_TICKET_TOPIC, value=ticket_data)
            generated_tickets.append(ticket_data)
        
        producer.flush()
        return {"status": "Simulation Success", "tickets_count": count, "sample_data": generated_tickets[:5]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)