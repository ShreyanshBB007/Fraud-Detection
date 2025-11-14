import json

def simple_rule(tx):
    return tx.get("amount", 0) > 150

def process(tx_json):
    tx = json.loads(tx_json)
    tx["_flagged"] = simple_rule(tx)
    return tx

if __name__ == "__main__":
    from services.producer.producer import gen_txn
    sample = gen_txn()
    print("Produced:", sample)
    print("Processed:", process(json.dumps(sample)))
