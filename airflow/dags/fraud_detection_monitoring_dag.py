from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
import json
from pymongo import MongoClient
from kafka import KafkaConsumer, KafkaProducer
import docker

# Default arguments for the DAG
default_args = {
    'owner': 'fraud-detection-team',
    'depends_on_past': False,
    'start_date': datetime(2025, 11, 14),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}

# Create the DAG
dag = DAG(
    'fraud_detection_monitoring',
    default_args=default_args,
    description='System Health Monitoring DAG',
    schedule_interval=timedelta(minutes=15),  # Run every 15 minutes
    catchup=False,
    tags=['fraud-detection', 'monitoring', 'health-check'],
)

def check_system_health(**context):
    """Comprehensive system health check"""
    health_report = {
        'timestamp': datetime.now().isoformat(),
        'services': {},
        'overall_status': 'healthy'
    }
    
    try:
        # Check MongoDB
        try:
            mongo_client = MongoClient('mongodb://mongodb:27017/', serverSelectionTimeoutMS=5000)
            mongo_client.admin.command('ismaster')
            db = mongo_client['fraud_detection']
            transaction_count = db['transactions'].count_documents({})
            alert_count = db['fraud_alerts'].count_documents({})
            mongo_client.close()
            
            health_report['services']['mongodb'] = {
                'status': 'healthy',
                'transaction_count': transaction_count,
                'alert_count': alert_count
            }
        except Exception as e:
            health_report['services']['mongodb'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_report['overall_status'] = 'degraded'
        
        # Check Kafka
        try:
            producer = KafkaProducer(
                bootstrap_servers=['kafka:9092'],
                request_timeout_ms=5000
            )
            producer.close()
            
            health_report['services']['kafka'] = {
                'status': 'healthy',
                'bootstrap_servers': ['kafka:9092']
            }
        except Exception as e:
            health_report['services']['kafka'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            health_report['overall_status'] = 'degraded'
        
        print(f"System Health Report: {json.dumps(health_report, indent=2)}")
        return health_report
        
    except Exception as e:
        print(f"Error checking system health: {str(e)}")
        health_report['overall_status'] = 'critical'
        health_report['error'] = str(e)
        return health_report

def generate_daily_fraud_report(**context):
    """Generate daily fraud detection report"""
    try:
        mongo_client = MongoClient('mongodb://mongodb:27017/')
        db = mongo_client['fraud_detection']
        
        # Calculate date range for today
        today = datetime.now().date()
        start_of_day = datetime.combine(today, datetime.min.time()).isoformat()
        end_of_day = datetime.combine(today, datetime.max.time()).isoformat()
        
        # Get today's transactions
        today_transactions = db['transactions'].count_documents({
            'processed_at': {'$gte': start_of_day, '$lte': end_of_day}
        })
        
        # Get today's fraud alerts
        today_fraud = db['fraud_alerts'].count_documents({
            'alert_time': {'$gte': start_of_day, '$lte': end_of_day}
        })
        
        # Get fraud breakdown by reasons
        fraud_pipeline = [
            {'$match': {'alert_time': {'$gte': start_of_day, '$lte': end_of_day}}},
            {'$unwind': '$fraud_reasons'},
            {'$group': {'_id': '$fraud_reasons', 'count': {'$sum': 1}}},
            {'$sort': {'count': -1}}
        ]
        fraud_reasons = list(db['fraud_alerts'].aggregate(fraud_pipeline))
        
        # Get average fraud score
        avg_score_pipeline = [
            {'$match': {'alert_time': {'$gte': start_of_day, '$lte': end_of_day}}},
            {'$group': {'_id': None, 'avg_score': {'$avg': '$fraud_score'}}}
        ]
        avg_score_result = list(db['fraud_alerts'].aggregate(avg_score_pipeline))
        avg_fraud_score = avg_score_result[0]['avg_score'] if avg_score_result else 0
        
        mongo_client.close()
        
        report = {
            'date': today.isoformat(),
            'total_transactions': today_transactions,
            'fraud_alerts': today_fraud,
            'fraud_rate': round((today_fraud / today_transactions * 100) if today_transactions > 0 else 0, 2),
            'avg_fraud_score': round(avg_fraud_score, 2),
            'fraud_reasons_breakdown': fraud_reasons
        }
        
        print(f"Daily Fraud Report: {json.dumps(report, indent=2)}")
        return report
        
    except Exception as e:
        print(f"Error generating daily report: {str(e)}")
        raise

def cleanup_old_data(**context):
    """Clean up old transaction and alert data (older than 30 days)"""
    try:
        mongo_client = MongoClient('mongodb://mongodb:27017/')
        db = mongo_client['fraud_detection']
        
        # Calculate cutoff date (30 days ago)
        cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
        
        # Remove old transactions
        old_transactions = db['transactions'].delete_many({
            'processed_at': {'$lt': cutoff_date}
        })
        
        # Remove old fraud alerts
        old_alerts = db['fraud_alerts'].delete_many({
            'alert_time': {'$lt': cutoff_date}
        })
        
        mongo_client.close()
        
        result = {
            'transactions_removed': old_transactions.deleted_count,
            'alerts_removed': old_alerts.deleted_count,
            'cutoff_date': cutoff_date
        }
        
        print(f"Cleanup completed: {result}")
        return result
        
    except Exception as e:
        print(f"Error during cleanup: {str(e)}")
        raise

# Define tasks
system_health_task = PythonOperator(
    task_id='check_system_health',
    python_callable=check_system_health,
    dag=dag,
)

daily_report_task = PythonOperator(
    task_id='generate_daily_fraud_report',
    python_callable=generate_daily_fraud_report,
    dag=dag,
)

cleanup_task = PythonOperator(
    task_id='cleanup_old_data',
    python_callable=cleanup_old_data,
    dag=dag,
)

# Set task dependencies
system_health_task >> [daily_report_task, cleanup_task]