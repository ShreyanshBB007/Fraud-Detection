import json, time, random, uuid

def gen_txn():
    return {
        "txn_id": str(uuid.uuid4()),
        "user_id": f"user_{random.randint(1,100)}",
        "product_id": f"product_{random.randint(1,200)}",
        "amount": round(random.random()*200, 2),
        "timestamp": int(time.time()*1000)
    }

def main(loop=10, delay=0.1):
    for _ in range(loop):
        print(json.dumps(gen_txn()))
        time.sleep(delay)

if __name__ == "__main__":
    main()
