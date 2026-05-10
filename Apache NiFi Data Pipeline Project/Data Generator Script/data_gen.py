import pandas as pd
import numpy as np
import os
import time
from datetime import datetime
import random

OUTPUT_DIR = r"./my_data/input"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def generate_messy_data(num_rows=10):
    data = {
        'transaction_id': [random.randint(1000, 2000) for _ in range(num_rows)],
        'customer_id': [random.randint(1, 100) for _ in range(num_rows)],
        'amount': [round(random.uniform(10.5, 500.0), 2) for _ in range(num_rows)],
        'status': random.choices(['Success', 'Failed', 'Pending', None], k=num_rows),
        'timestamp': [datetime.now().strftime("%Y-%m-%d %H:%M:%S") for _ in range(num_rows)]
    }
    
    df = pd.DataFrame(data)
    
    if random.random() > 0.7:
        df = pd.concat([df, df.iloc[[0]]], ignore_index=True)
        
    return df

def start_simulation(max_files=20):
    print(f"Starting data simulation in: {OUTPUT_DIR}")
    file_count = 0
    
    try:
        while file_count < max_files:
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"transaction_{timestamp_str}.csv"
            file_path = os.path.join(OUTPUT_DIR, file_name)
            
            df = generate_messy_data(random.randint(5, 15))
            df.to_csv(file_path, index=False)
            
            file_count += 1
            print(f"[{file_count}/{max_files}] Created: {file_name}")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

if __name__ == "__main__":
    start_simulation(max_files=20)