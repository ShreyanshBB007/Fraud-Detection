from kafka import KafkaProducer
import json
import random
import time
from datetime import datetime

def gen_txn():
    return {
        "user_id": random.randint(1, 100),
        "amount": round(random.uniform(10, 5000), 2),
        "location": random.choice(["IN", "US", "UK", "CA", "AU"]),
        "timestamp": datetime.utcnow().isoformat()
    }

def start_producer():
    print("🚀 Starting Producer... Connecting to Kafka...")
    
    producer = KafkaProducer(
        bootstrap_servers="localhost:9092",
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )

    print("✔ Connected to Kafka")

    while True:
        txn = gen_txn()
        producer.send("transactions", txn)
        print("➡ Sent:", txn)
        time.sleep(1)

if __name__ == "__main__":
    start_producer()
