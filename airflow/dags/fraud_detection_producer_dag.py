from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
import random
from confluent_kafka import Producer
import time

# Default arguments for the DAG
default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 14),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Create the DAG
dag = DAG(
    'fraud_detection_producer',
    default_args=default_args,
    description='Fraud Detection Data Producer DAG',
    schedule_interval=timedelta(minutes=10),  # Run every 10 minutes
    catchup=False,
    tags=['fraud-detection', 'producer', 'kafka'],
)

def generate_transaction_data():
    """Generate sample transaction data"""
    transaction = {
        'transaction_id': f"txn_{int(time.time())}_{random.randint(1000, 9999)}",
        'user_id': f"user_{random.randint(1, 1000)}",
        'amount': round(random.uniform(10.0, 5000.0), 2),
        'merchant': random.choice(['Amazon', 'Walmart', 'Target', 'Best Buy', 'Starbucks', 'McDonalds']),
        'location': random.choice(['NY', 'CA', 'TX', 'FL', 'IL']),
        'timestamp': datetime.now().isoformat(),
        'card_type': random.choice(['visa', 'mastercard', 'amex']),
        'is_weekend': datetime.now().weekday() >= 5,
        'hour_of_day': datetime.now().hour,
    }
    
    # Add some fraud indicators randomly
    if random.random() < 0.1:  # 10% chance of suspicious activity
        transaction['amount'] = round(random.uniform(2000.0, 10000.0), 2)  # High amount
        transaction['suspicious_location'] = True
    
    return transaction

def send_to_kafka(**context):
    """Send transaction data to Kafka"""
    try:
        # Create Kafka producer
        producer = Producer({
            'bootstrap.servers': 'kafka:9092'
        })
        
        # Generate and send 5 transactions
        transactions_sent = 0
        for i in range(5):
            transaction = generate_transaction_data()
            producer.produce('transactions', key=transaction['transaction_id'], value=json.dumps(transaction))
            transactions_sent += 1
            print(f"Sent transaction {i+1}: {transaction['transaction_id']}")
            time.sleep(1)  # Small delay between transactions
        
        producer.flush()
        
        print(f"Successfully sent {transactions_sent} transactions to Kafka")
        return f"Sent {transactions_sent} transactions"
        
    except Exception as e:
        print(f"Error sending to Kafka: {str(e)}")
        raise

def check_kafka_connection():
    """Check if Kafka is available"""
    try:
        from confluent_kafka import Producer
        producer = Producer({
            'bootstrap.servers': 'kafka:9092',
            'socket.timeout.ms': 5000
        })
        # Try to get metadata to test connection
        metadata = producer.list_topics(timeout=5)
        print("Kafka connection successful")
        return "Kafka is available"
    except Exception as e:
        print(f"Kafka connection failed: {str(e)}")
        raise

# Define tasks
check_kafka_task = PythonOperator(
    task_id='check_kafka_connection',
    python_callable=check_kafka_connection,
    dag=dag,
)

produce_transactions_task = PythonOperator(
    task_id='produce_transactions',
    python_callable=send_to_kafka,
    dag=dag,
)

# Set task dependencies
check_kafka_task >> produce_transactions_task