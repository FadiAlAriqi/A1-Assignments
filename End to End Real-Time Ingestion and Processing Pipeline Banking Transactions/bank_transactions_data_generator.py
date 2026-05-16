import csv
import time
import random
import os
from datetime import datetime

OUTPUT_DIR = r"./my_data/input"

os.makedirs(OUTPUT_DIR, exist_ok=True)

customers = ["CUST001", "CUST002", "CUST003", "CUST004", None]
statuses = ["SUCCESS", "FAILED", "PENDING", "UNKNOWN"]

def random_timestamp():
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M",
        "%Y/%m/%d",
        "%m-%d-%Y %H:%M:%S"
    ]
    fmt = random.choice(formats)
    return datetime.now().strftime(fmt)

def generate_record():
    return [
        random.randint(1000, 9999),                        # transaction_id
        random.choice(customers),                          # customer_id
        random.choice([100, 200, 500, -50, "invalid"]),    # amount
        random_timestamp(),                                # timestamp
        random.choice(statuses)                            # status
    ]

def generate_corrupted_row():
    corrupted_examples = [
        ["###", "???", "NaN"],
        ["", "", ""],
        ["BROKEN_DATA"],
        ["1234", None, "oops", "bad_timestamp"]
    ]
    return random.choice(corrupted_examples)

def create_csv_file():
    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"transaction_{timestamp_str}.csv"
    filepath = os.path.join(OUTPUT_DIR, file_name)

    records = []

    for _ in range(random.randint(5, 15)):
        records.append(generate_record())

    if random.random() < 0.3:
        records.append(records[0])

    if random.random() < 0.3:
        records.append(generate_corrupted_row())

    with open(filepath, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(["transaction_id", "customer_id", "amount", "timestamp", "status"])

        for r in records:
            writer.writerow(r)

    print(f"- Generated file: {filepath}")

while True:
    create_csv_file()
    time.sleep(random.randint(2, 4))