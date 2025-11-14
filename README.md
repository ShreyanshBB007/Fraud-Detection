# Fraud Detection Capstone Project

A real-time fraud detection system built with Apache Kafka, MongoDB, Apache Airflow, and Python. This project demonstrates a complete end-to-end pipeline for detecting fraudulent transactions in real-time using streaming data processing and rule-based detection algorithms.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────┐    ┌────────────────┐    ┌─────────────┐
│   Transaction   │───▶│    Kafka    │───▶│ Fraud Detection│───▶│  MongoDB    │
│   Producer      │    │  (Stream)   │    │   Consumer     │    │ (Storage)   │
└─────────────────┘    └─────────────┘    └────────────────┘    └─────────────┘
         ▲                                           │                    │
         │                                           ▼                    ▼
┌─────────────────┐                         ┌────────────────┐    ┌─────────────┐
│    Airflow      │◀────────────────────────│ Fraud Alerts   │    │ Transaction │
│ (Orchestration) │                         │   & Reports    │    │   History   │
└─────────────────┘                         └────────────────┘    └─────────────┘
```

## 🎯 Project Purpose

This fraud detection system is designed to:

- **Process transactions in real-time** using Apache Kafka streaming
- **Apply rule-based fraud detection** to identify suspicious activities
- **Store transaction data and alerts** in MongoDB for analysis
- **Orchestrate the entire pipeline** using Apache Airflow DAGs
- **Provide monitoring and reporting** capabilities for system health

## 🚀 Key Features

### Real-Time Processing
- Kafka-based streaming architecture for low-latency processing
- Continuous transaction monitoring and analysis
- Immediate fraud alert generation

### Fraud Detection Rules
- **High Amount Transactions**: Flags transactions over $2,000 (+30 fraud score)
- **Unusual Timing**: Detects late-night transactions (11 PM - 6 AM) (+20 fraud score)
- **Weekend Patterns**: High-value weekend transactions (+25 fraud score)
- **Location Anomalies**: Suspicious location indicators (+40 fraud score)
- **Payment Method Patterns**: AMEX high-value transaction patterns (+15 fraud score)

### Automated Orchestration
- **Producer DAG**: Generates realistic transaction data every 10 minutes
- **Consumer DAG**: Processes transactions and detects fraud every 5 minutes
- **Monitoring DAG**: System health checks and reporting every 15 minutes

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Streaming** | Apache Kafka | Real-time data streaming and message queuing |
| **Database** | MongoDB | Transaction storage and fraud alert persistence |
| **Orchestration** | Apache Airflow | Workflow management and task scheduling |
| **Processing** | Python | Data processing and fraud detection logic |
| **Containerization** | Docker & Docker Compose | Service deployment and management |
| **Messaging** | Confluent Kafka | Enhanced Kafka client for reliable messaging |

## 📁 Project Structure

```
fraud-detection-project/
├── airflow/                     # Airflow configuration and DAGs
│   ├── dags/                    # Airflow DAG definitions
│   │   ├── fraud_detection_producer_dag.py
│   │   ├── fraud_detection_consumer_dag.py
│   │   └── fraud_detection_monitoring_dag.py
│   ├── logs/                    # Airflow execution logs
│   ├── plugins/                 # Custom Airflow plugins
│   ├── airflow-db/              # Airflow SQLite database
│   ├── docker-compose.yaml     # Airflow services configuration
│   └── requirements.txt        # Python dependencies
├── docker/                      # Docker configurations
│   ├── kafka/                   # Kafka setup
│   │   └── docker-compose.yml
│   └── mongo/                   # MongoDB setup
│       └── docker-compose.yml
├── services/                    # Application services
│   ├── api/                     # API service (future enhancement)
│   ├── processor/               # Data processing service
│   └── producer/                # Data generation service
├── docs/                        # Documentation
├── notebooks/                   # Jupyter notebooks for analysis
├── tests/                       # Unit and integration tests
├── venv/                        # Python virtual environment
├── requirements.txt             # Python project dependencies
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## 🏃‍♂️ Quick Start

### Prerequisites
- Docker and Docker Compose installed
- Python 3.10+ with pip
- Git

### 1. Clone and Setup
```bash
git clone https://github.com/ShreyanshBB007/Fraud-Detection.git
cd fraud-detection-project

# Setup Python virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 2. Start Infrastructure Services
```bash
# Start Kafka
docker compose -f docker/kafka/docker-compose.yml up -d

# Start MongoDB
docker compose -f docker/mongo/docker-compose.yml up -d

# Verify services are running
docker ps
```

### 3. Start Airflow
```bash
cd airflow

# Initialize Airflow
docker compose up airflow-init

# Start Airflow services
docker compose up -d

# Access Airflow UI: http://localhost:8080
# Login: admin / admin
```

### 4. Enable and Monitor DAGs
1. Open Airflow UI: http://localhost:8080
2. Login with credentials: `admin` / `admin`
3. Enable the three DAGs by toggling them on:
   - `fraud_detection_producer`
   - `fraud_detection_consumer`
   - `fraud_detection_monitoring`
4. Trigger manual runs to test the pipeline

## 🔄 System Workflow

### 1. Data Generation (Producer DAG)
```python
# Every 10 minutes:
# 1. Generate realistic transaction data
# 2. Add fraud indicators randomly (10% chance)
# 3. Send transactions to Kafka 'transactions' topic
```

**Sample Transaction:**
```json
{
  "transaction_id": "txn_1699962000_1234",
  "user_id": "user_567",
  "amount": 1250.75,
  "merchant": "Amazon",
  "location": "NY",
  "timestamp": "2025-11-14T13:40:00",
  "card_type": "visa",
  "is_weekend": false,
  "hour_of_day": 13
}
```

### 2. Fraud Detection (Consumer DAG)
```python
# Every 5 minutes:
# 1. Consume transactions from Kafka
# 2. Apply fraud detection rules
# 3. Calculate fraud score (0-100)
# 4. Store transaction in MongoDB
# 5. Create fraud alert if score ≥ 50
```

**Fraud Detection Logic:**
- Threshold: Fraud Score ≥ 50
- Multiple rules can trigger simultaneously
- Detailed reasoning provided in alerts

### 3. System Monitoring (Monitoring DAG)
```python
# Every 15 minutes:
# 1. Check Kafka and MongoDB connectivity
# 2. Generate daily fraud statistics
# 3. Clean up old data (30+ days)
# 4. System health reporting
```

## 📊 Data Storage Schema

### MongoDB Collections

#### `transactions` Collection
```json
{
  "_id": "ObjectId",
  "transaction_id": "txn_1699962000_1234",
  "user_id": "user_567",
  "amount": 1250.75,
  "merchant": "Amazon",
  "location": "NY",
  "timestamp": "2025-11-14T13:40:00",
  "card_type": "visa",
  "is_weekend": false,
  "hour_of_day": 13,
  "fraud_analysis": {
    "is_fraud": false,
    "fraud_score": 25,
    "fraud_reasons": ["High-value weekend transaction"]
  },
  "processed_at": "2025-11-14T13:41:00"
}
```

#### `fraud_alerts` Collection
```json
{
  "_id": "ObjectId",
  "transaction_id": "txn_1699962000_5678",
  "user_id": "user_789",
  "amount": 3500.00,
  "fraud_score": 75,
  "fraud_reasons": [
    "High transaction amount",
    "Unusual time of transaction",
    "Transaction from suspicious location"
  ],
  "alert_time": "2025-11-14T02:30:00",
  "status": "pending_review"
}
```

## 🔍 Fraud Detection Rules

| Rule | Trigger Condition | Score | Description |
|------|------------------|-------|-------------|
| **High Amount** | Amount > $2,000 | +30 | Flags unusually large transactions |
| **Late Night** | 11 PM - 6 AM | +20 | Detects off-hours activity |
| **Weekend High-Value** | Weekend + Amount > $1,000 | +25 | Weekend spending patterns |
| **Suspicious Location** | Location flag present | +40 | Geographic anomalies |
| **AMEX Pattern** | AMEX + Amount > $1,500 | +15 | Payment method patterns |

**Fraud Threshold:** Total Score ≥ 50 = Fraud Alert

## 📈 Monitoring and Observability

### Airflow Dashboard
- **DAG Status**: Monitor task execution and failures
- **Task Logs**: Detailed execution logs for debugging
- **Scheduling**: View upcoming and past runs
- **Performance**: Task duration and success rates

### System Health Checks
- **Kafka Connectivity**: Producer/consumer health
- **MongoDB Status**: Database connectivity and performance
- **Data Pipeline**: End-to-end processing verification

### Reporting Features
- **Daily Fraud Statistics**: Transaction counts and fraud rates
- **Fraud Reason Analysis**: Breakdown by detection rules
- **System Performance**: Processing times and throughput

## 🚦 Service Endpoints

| Service | Endpoint | Credentials | Purpose |
|---------|----------|-------------|---------|
| **Airflow UI** | http://localhost:8080 | admin / admin | DAG management and monitoring |
| **MongoDB** | localhost:27017 | None | Direct database access |
| **Kafka** | localhost:9092 | None | Message broker |

## 🧪 Testing the System

### Manual Testing
```bash
# 1. Check services are running
docker ps

# 2. Trigger producer DAG
docker exec airflow-webserver airflow dags trigger fraud_detection_producer

# 3. Monitor in Airflow UI
# Navigate to: http://localhost:8080

# 4. Check MongoDB data
docker exec -it mongodb mongosh
use fraud_detection
db.transactions.find().limit(5)
db.fraud_alerts.find()
```

### Verification Steps
1. **Producer**: Check if transactions appear in Kafka
2. **Consumer**: Verify processing logs in Airflow
3. **Storage**: Confirm data in MongoDB collections
4. **Alerts**: Review fraud alerts and scoring

## 🔧 Configuration

### Environment Variables
- `AIRFLOW__CORE__FERNET_KEY`: Airflow encryption key
- `AIRFLOW__WEBSERVER__SECRET_KEY`: Web UI security
- Default MongoDB: `mongodb://mongodb:27017/`
- Default Kafka: `kafka:9092`

### Scaling Options
- **Kafka Partitions**: Increase for higher throughput
- **MongoDB Sharding**: Scale database for large datasets
- **Airflow Workers**: Add workers for parallel processing
- **Docker Resources**: Adjust CPU/memory limits

## 📝 Development and Customization

### Adding New Fraud Rules
1. Edit `fraud_detection_rules()` in consumer DAG
2. Add new scoring logic and thresholds
3. Update fraud reason descriptions
4. Test with sample transactions

### Custom Data Sources
1. Modify producer DAG to connect to real data sources
2. Update transaction schema as needed
3. Adjust Kafka topic configuration
4. Update MongoDB collections

### Machine Learning Integration
- Replace rule-based detection with ML models
- Integrate with scikit-learn, TensorFlow, or PyTorch
- Add model training and retraining DAGs
- Implement feature engineering pipelines

## 📚 Additional Resources

### Documentation
- [Apache Kafka Documentation](https://kafka.apache.org/documentation/)
- [MongoDB Manual](https://docs.mongodb.com/manual/)
- [Apache Airflow Documentation](https://airflow.apache.org/docs/)
- [Confluent Kafka Python](https://docs.confluent.io/kafka-clients/python/current/overview.html)

### Troubleshooting
- Check Docker container logs: `docker logs <container_name>`
- Airflow task logs available in UI
- MongoDB connection issues: Verify network connectivity
- Kafka producer/consumer errors: Check topic creation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a pull request

## 📄 License

This project is created for educational purposes as part of a capstone project.

## 👥 Team

- **Developer**: ShreyanshBB007
- **Project Type**: Fraud Detection Capstone
- **Technology Stack**: Kafka + MongoDB + Airflow + Python

---

**🚀 Ready to detect fraud in real-time? Follow the Quick Start guide above!**
