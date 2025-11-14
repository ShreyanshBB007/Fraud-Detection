from kafka import KafkaConsumer
import json
import time
from collections import defaultdict, deque
from pymongo import MongoClient

# ==================================================
# MongoDB Setup
# ==================================================
client = MongoClient("mongodb://localhost:27017/")
db = client["fraud_system"]

transactions_col = db["transactions"]
alerts_col = db["fraud_alerts"]

# ==================================================
# State for Windowed Rules
# ==================================================
user_transactions = defaultdict(lambda: deque(maxlen=10))  # last timestamps
user_last_location = {}  # track user location


# ==================================================
# BASIC RULES
# ==================================================
def basic_rules(txn):
    rules = []
    user_id = txn["user_id"]
    amount = txn["amount"]
    location = txn["location"]
    timestamp = time.time()

    # ---- Rule 1: HIGH AMOUNT ----
    if amount > 3000:
        rules.append("HIGH_AMOUNT")

    # ---- Rule 2: UNUSUAL LOCATION ----
    if location not in ["IN", "US"]:
        rules.append("UNUSUAL_LOCATION")

    # ---- Rule 3: BURST TRANSACTIONS ----
    user_transactions[user_id].append(timestamp)
    recent_txns = user_transactions[user_id]

    if len(recent_txns) >= 3 and (recent_txns[-1] - recent_txns[-3]) < 10:
        rules.append("BURST_TRANSACTIONS")

    # ---- Rule 4: LOCATION JUMP ----
    if user_id in user_last_location:
        if user_last_location[user_id] != location:
            rules.append("LOCATION_JUMP")

    user_last_location[user_id] = location

    return rules


# ==================================================
# ADVANCED RULES
# ==================================================
def advanced_rules(txn):
    rules = []

    # You can add ML, anomaly detection, statistical checks here.
    # Currently adding 2 sample advanced rules.

    amount = txn["amount"]

    # ---- Advanced Rule 1: Suspiciously round figures (e.g., 9999, 5000, etc.) ----
    if amount % 1000 == 0:
        rules.append("ROUND_FIGURE_SUSPICIOUS")

    # ---- Advanced Rule 2: Extremely low-value repeated payments ----
    if 0 < amount < 5:
        rules.append("MICRO_PAYMENT_PATTERN")

    return rules


# ==================================================
# KAFKA CONSUMER
# ==================================================
def start_consumer():
    print("🚀 Fraud Processor started with BASIC + ADVANCED rules...\n")

    consumer = KafkaConsumer(
        "transactions",
        bootstrap_servers="localhost:9092",
        auto_offset_reset="latest",
        enable_auto_commit=True,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    )

    for msg in consumer:

        try:
            txn = msg.value
            print(f"\n⬅ Received Transaction: {txn}")

            # Store raw transaction
            transactions_col.insert_one(txn)

            # Apply rules
            basic_alerts = basic_rules(txn)
            adv_alerts = advanced_rules(txn)

            alerts = basic_alerts + adv_alerts

            if alerts:
                print(f"🚨 FRAUD DETECTED! → {alerts}")

                alerts_col.insert_one({
                    "transaction": txn,
                    "alerts": alerts,
                    "timestamp": time.time()
                })
            else:
                print("✓ Transaction OK")

        except Exception as e:
            print(f"❌ Error processing message: {str(e)}")
            continue

        time.sleep(0.1)   # prevents busy-loop CPU spike


if __name__ == "__main__":
    start_consumer()
