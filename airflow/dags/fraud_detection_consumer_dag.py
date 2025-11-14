from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
import json
from kafka import KafkaConsumer
from pymongo import MongoClient
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
    'fraud_detection_consumer',
    default_args=default_args,
    description='Fraud Detection Consumer and Processing DAG',
    schedule_interval=timedelta(minutes=5),  # Run every 5 minutes
    catchup=False,
    tags=['fraud-detection', 'consumer', 'kafka', 'mongodb'],
)

def fraud_detection_rules(transaction):
    """Apply fraud detection rules to transaction"""
    fraud_score = 0
    fraud_reasons = []
    
    # Rule 1: High amount transactions
    if transaction['amount'] > 2000:
        fraud_score += 30
        fraud_reasons.append("High transaction amount")
    
    # Rule 2: Late night transactions
    if transaction['hour_of_day'] < 6 or transaction['hour_of_day'] > 23:
        fraud_score += 20
        fraud_reasons.append("Unusual time of transaction")
    
    # Rule 3: Weekend high-value transactions
    if transaction['is_weekend'] and transaction['amount'] > 1000:
        fraud_score += 25
        fraud_reasons.append("High value weekend transaction")
    
    # Rule 4: Suspicious location flag
    if transaction.get('suspicious_location', False):
        fraud_score += 40
        fraud_reasons.append("Transaction from suspicious location")
    
    # Rule 5: Multiple high-value transactions (simulated)
    if transaction['amount'] > 1500 and transaction['card_type'] == 'amex':
        fraud_score += 15
        fraud_reasons.append("High-value AMEX transaction pattern")
    
    is_fraud = fraud_score >= 50
    
    return {
        'is_fraud': is_fraud,
        'fraud_score': fraud_score,
        'fraud_reasons': fraud_reasons
    }

def process_transactions(**context):
    """Consume transactions from Kafka and process for fraud detection"""
    try:
        # Connect to MongoDB
        mongo_client = MongoClient('mongodb://mongodb:27017/')
        db = mongo_client['fraud_detection']
        transactions_collection = db['transactions']
        fraud_alerts_collection = db['fraud_alerts']
        
        # Create Kafka consumer
        consumer = KafkaConsumer(
            'transactions',
            bootstrap_servers=['kafka:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            consumer_timeout_ms=30000,  # Timeout after 30 seconds if no messages
            auto_offset_reset='latest'  # Only process new messages
        )
        
        transactions_processed = 0
        fraud_detected = 0
        
        for message in consumer:
            transaction = message.value
            
            # Apply fraud detection
            fraud_result = fraud_detection_rules(transaction)
            
            # Enrich transaction with fraud detection results
            transaction['fraud_analysis'] = fraud_result
            transaction['processed_at'] = datetime.now().isoformat()
            
            # Store transaction in MongoDB
            transactions_collection.insert_one(transaction)
            transactions_processed += 1
            
            # If fraud detected, create alert
            if fraud_result['is_fraud']:
                fraud_alert = {
                    'transaction_id': transaction['transaction_id'],
                    'user_id': transaction['user_id'],
                    'amount': transaction['amount'],
                    'fraud_score': fraud_result['fraud_score'],
                    'fraud_reasons': fraud_result['fraud_reasons'],
                    'alert_time': datetime.now().isoformat(),
                    'status': 'pending_review'
                }
                fraud_alerts_collection.insert_one(fraud_alert)
                fraud_detected += 1
                print(f"FRAUD ALERT: Transaction {transaction['transaction_id']} - Score: {fraud_result['fraud_score']}")
            
            print(f"Processed transaction: {transaction['transaction_id']} - Fraud: {fraud_result['is_fraud']}")
        
        consumer.close()
        mongo_client.close()
        
        result = f"Processed {transactions_processed} transactions, detected {fraud_detected} potential fraud cases"
        print(result)
        return result
        
    except Exception as e:
        print(f"Error processing transactions: {str(e)}")
        raise

def check_mongodb_connection():
    """Check if MongoDB is available"""
    try:
        mongo_client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=5000)
        mongo_client.admin.command('ismaster')
        mongo_client.close()
        print("MongoDB connection successful")
        return "MongoDB is available"
    except Exception as e:
        print(f"MongoDB connection failed: {str(e)}")
        raise

def get_fraud_statistics():
    """Get fraud detection statistics from MongoDB"""
    try:
        mongo_client = MongoClient('mongodb://mongodb:27017/')
        db = mongo_client['fraud_detection']
        
        # Get transaction counts
        total_transactions = db['transactions'].count_documents({})
        fraud_transactions = db['fraud_alerts'].count_documents({})
        
        # Get recent fraud alerts
        recent_alerts = list(db['fraud_alerts'].find().sort('alert_time', -1).limit(5))
        
        mongo_client.close()
        
        stats = {
            'total_transactions': total_transactions,
            'fraud_transactions': fraud_transactions,
            'fraud_rate': round((fraud_transactions / total_transactions * 100) if total_transactions > 0 else 0, 2),
            'recent_alerts_count': len(recent_alerts)
        }
        
        print(f"Fraud Detection Statistics: {stats}")
        return stats
        
    except Exception as e:
        print(f"Error getting statistics: {str(e)}")
        raise

# Define tasks
check_mongodb_task = PythonOperator(
    task_id='check_mongodb_connection',
    python_callable=check_mongodb_connection,
    dag=dag,
)

process_transactions_task = PythonOperator(
    task_id='process_transactions',
    python_callable=process_transactions,
    dag=dag,
)

get_statistics_task = PythonOperator(
    task_id='get_fraud_statistics',
    python_callable=get_fraud_statistics,
    dag=dag,
)

# Set task dependencies
check_mongodb_task >> process_transactions_task >> get_statistics_task