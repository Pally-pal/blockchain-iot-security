# INTELLIGENT BLOCKCHAIN SYSTEM FOR SECURING IOT DATA

**Project Documentation**

---

## PROJECT INFORMATION

**Title:** Development of an Intelligent Blockchain System for Securing IoT Data

**Author:** Oyelade Paul Oluwafemi  
**Matric Number:** 2021/37014  
**Department:** Computer Science  
**Institution:** Osun State University, Osogbo  
**Supervisor:** Dr. E.O Ojo  
**Date:** January, 2026

---

## TABLE OF CONTENTS

1. [Executive Summary](#executive-summary)
2. [System Overview](#system-overview)
3. [Installation Guide](#installation-guide)
4. [System Architecture](#system-architecture)
5. [Component Documentation](#component-documentation)
6. [API Documentation](#api-documentation)
7. [Usage Guide](#usage-guide)
8. [Testing Procedures](#testing-procedures)
9. [Results and Evaluation](#results-and-evaluation)
10. [Troubleshooting](#troubleshooting)
11. [Future Enhancements](#future-enhancements)
12. [References](#references)

---

## 1. EXECUTIVE SUMMARY

### 1.1 Project Objective

This project implements an intelligent blockchain-based security system for Internet of Things (IoT) data. The system addresses critical security challenges in IoT environments by providing:

- **Data Integrity:** Cryptographic hashing ensures data cannot be modified without detection
- **Immutability:** Blockchain storage prevents unauthorized alterations
- **Auditability:** Complete transparent audit trails of all data transactions
- **Decentralization:** No single point of failure or control

### 1.2 Key Features

✅ SHA-256 cryptographic hashing for data integrity  
✅ Ethereum blockchain integration for immutable storage  
✅ Smart contract-based data registry  
✅ Automated tamper detection  
✅ REST API for external integration  
✅ Comprehensive audit reporting  
✅ Real-time data verification  

### 1.3 Technology Stack

**Blockchain:**
- Ethereum (Ganache local network)
- Solidity 0.8.0 (Smart Contracts)
- Web3.py (Python-Ethereum integration)

**Backend:**
- Python 3.10+
- Flask (REST API)
- Pandas (Data processing)

**Frontend/Testing:**
- Requests (API testing)
- JSON (Data interchange)

---

## 2. SYSTEM OVERVIEW

### 2.1 Problem Statement

IoT systems face critical security challenges:
- **Data tampering:** Unauthorized modification of sensor data
- **Centralized vulnerabilities:** Single points of failure
- **Lack of auditability:** Difficulty tracking data modifications
- **Trust issues:** No verifiable proof of data integrity

### 2.2 Solution Approach

The system employs a hybrid architecture combining:

1. **Cryptographic Hashing (SHA-256):** Generates unique fingerprints for IoT data
2. **Blockchain Storage:** Stores hashes immutably on Ethereum
3. **Smart Contracts:** Automates data registration and verification
4. **REST API:** Enables seamless integration with IoT devices

### 2.3 System Components

```
┌─────────────────────────────────────────────────────┐
│              IoT Devices / Sensors                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│         Data Preprocessing Module                   │
│  (Cleaning, Normalization, Feature Extraction)      │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│       Cryptographic Hashing Module (SHA-256)        │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│         Blockchain Client (Web3.py)                 │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│      Smart Contract (IoTDataRegistry.sol)           │
│              ↓                                       │
│      Ethereum Blockchain (Ganache)                  │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│         REST API Server (Flask)                     │
└─────────────────┬───────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────┐
│      External Applications / Users                  │
└─────────────────────────────────────────────────────┘
```

---

## 3. INSTALLATION GUIDE

### 3.1 Prerequisites

**Software Requirements:**
- Python 3.10 or higher
- Node.js v16 or higher
- npm (Node Package Manager)
- Git (optional, for version control)

**Hardware Requirements:**
- Minimum 8GB RAM
- 50GB free disk space
- Multi-core processor (Intel i5 or equivalent)

### 3.2 Step-by-Step Installation

#### Step 1: Create Project Directory

```bash
mkdir blockchain-iot-security
cd blockchain-iot-security
```

#### Step 2: Set Up Python Virtual Environment

```bash
# Create virtual environment
python -m venv blockchain_env

# Activate virtual environment
# Windows:
blockchain_env\Scripts\activate
# Linux/Mac:
source blockchain_env/bin/activate
```

#### Step 3: Install Python Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install pandas==2.0.0
pip install web3==6.0.0
pip install eth-account==0.8.0
pip install flask==2.3.0
pip install flask-cors==4.0.0
pip install requests==2.31.0
```

#### Step 4: Install Node.js Dependencies

```bash
# Install Ganache (blockchain)
npm install -g ganache-cli

# Install Hardhat (smart contract framework)
npm init -y
npm install --save-dev hardhat@^2.22.0
npm install --save-dev @nomiclabs/hardhat-waffle ethereum-waffle chai @nomiclabs/hardhat-ethers ethers
```

#### Step 5: Create Project Structure

```bash
mkdir contracts scripts data results src tests logs
```

### 3.3 Configuration

#### Create config.py

Place your dataset path and Ganache credentials in `src/config.py`.

#### Deploy Smart Contract

```bash
# Start Ganache (keep running)
ganache-cli --port 8545 --networkId 1337 --accounts 10

# In new terminal, compile and deploy
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

---

## 4. SYSTEM ARCHITECTURE

### 4.1 Data Flow Architecture

1. **IoT Data Collection:** Sensor data collected from devices
2. **Preprocessing:** Data cleaned and normalized
3. **Hash Generation:** SHA-256 hash computed for each record
4. **Blockchain Registration:** Hash stored on Ethereum blockchain
5. **Verification:** Data integrity verified against blockchain

### 4.2 Security Architecture

**Three-Layer Security:**

1. **Cryptographic Layer:** SHA-256 hashing
2. **Blockchain Layer:** Immutable distributed ledger
3. **Smart Contract Layer:** Automated enforcement of rules

### 4.3 Smart Contract Structure

```solidity
contract IoTDataRegistry {
    struct DataRecord {
        bytes32 dataHash;
        address deviceAddress;
        uint256 timestamp;
        string deviceId;
        bool exists;
    }
    
    mapping(bytes32 => DataRecord) public dataRecords;
    
    function registerData(bytes32 _dataHash, string memory _deviceId) 
    function verifyData(bytes32 _dataHash)
    function getDataRecord(bytes32 _dataHash)
    function getTotalRecords()
}
```

---

## 5. COMPONENT DOCUMENTATION

### 5.1 Data Preprocessing Module

**File:** `src/data_preprocessing.py`

**Purpose:** Prepares IoT sensor data for blockchain registration

**Key Functions:**
- `load_data()` - Loads CSV dataset
- `handle_missing_values()` - Cleans missing data
- `normalize_timestamps()` - Ensures consistent time format
- `add_device_identifiers()` - Adds device IDs
- `extract_features()` - Extracts relevant features

**Usage:**
```bash
python src/data_preprocessing.py
```

**Output:**
- `data/processed_iot_data.csv`
- `data/iot_features.csv`
- `data/sample_iot_data.csv`

### 5.2 Cryptographic Hashing Module

**File:** `src/crypto_utils.py`

**Purpose:** Generates SHA-256 hashes for data integrity

**Key Functions:**
- `generate_sha256_hash(data)` - Creates hash
- `hash_dataframe_row(row_dict)` - Hashes DataFrame row
- `verify_hash(data, hash)` - Verifies hash matches data

**Example:**
```python
from crypto_utils import CryptoHasher

hasher = CryptoHasher()
data = {'device': 'DEVICE_001', 'temp': 25.5}
hash_value = hasher.generate_sha256_hash(data)
# Output: 64-character hexadecimal string
```

### 5.3 Blockchain Client Module

**File:** `src/blockchain_client.py`

**Purpose:** Interfaces with Ethereum blockchain

**Key Functions:**
- `register_data_hash(hash, device_id)` - Stores hash on blockchain
- `verify_data_hash(hash)` - Checks if hash exists
- `get_total_records()` - Returns total blockchain records

**Example:**
```python
from blockchain_client import BlockchainClient

client = BlockchainClient()
result = client.register_data_hash(hash_value, 'DEVICE_001')
print(result['tx_hash'])  # Transaction hash
```

### 5.4 Main Security System

**File:** `src/iot_security_system.py`

**Purpose:** Orchestrates complete security workflow

**Key Functions:**
- `process_iot_data(df)` - Processes and registers data
- `verify_data_integrity(data)` - Verifies against blockchain
- `simulate_tampering_detection()` - Demonstrates tamper detection
- `generate_audit_report()` - Creates audit report

**Usage:**
```bash
python src/iot_security_system.py
```

### 5.5 REST API Server

**File:** `src/api_server.py`

**Purpose:** Provides HTTP API for external integration

**Endpoints:** (See API Documentation section)

**Usage:**
```bash
python src/api_server.py
```

---

## 6. API DOCUMENTATION

### 6.1 Base URL

```
http://localhost:5000
```

### 6.2 Endpoints

#### GET /
**Description:** API home with endpoint list

**Response:**
```json
{
  "service": "IoT Blockchain Security System API",
  "version": "1.0.0",
  "endpoints": {...}
}
```

#### GET /api/health
**Description:** System health check

**Response:**
```json
{
  "status": "healthy",
  "blockchain_connected": true,
  "total_records": 20,
  "account_balance": "999.5 ETH"
}
```

#### POST /api/register
**Description:** Register IoT data on blockchain

**Request Body:**
```json
{
  "device_id": "DEVICE_001",
  "sensor_data": {
    "temperature": 25.5,
    "humidity": 60.2
  }
}
```

**Response:**
```json
{
  "success": true,
  "data_hash": "0abc123...",
  "tx_hash": "0x456def...",
  "block_number": 123
}
```

#### POST /api/verify
**Description:** Verify data integrity

**Request Body:**
```json
{
  "sensor_data": {
    "temperature": 25.5,
    "humidity": 60.2
  }
}
```

**Response:**
```json
{
  "integrity_verified": true,
  "message": "Data integrity confirmed",
  "computed_hash": "0abc123..."
}
```

#### POST /api/hash
**Description:** Generate SHA-256 hash

**Request Body:**
```json
{
  "data": {"key": "value"}
}
```

**Response:**
```json
{
  "success": true,
  "hash": "0abc123...",
  "algorithm": "SHA-256"
}
```

#### GET /api/audit
**Description:** Get system audit report

**Response:**
```json
{
  "audit_report": {
    "total_processed_records": 20,
    "successful_registrations": 20,
    "success_rate": "100.00%"
  }
}
```

#### GET /api/records
**Description:** Get total blockchain records

**Response:**
```json
{
  "total_records": 20,
  "contract_address": "0x..."
}
```

---

## 7. USAGE GUIDE

### 7.1 Running the Complete System

#### Step 1: Start Ganache
```bash
ganache-cli --port 8545 --networkId 1337 --accounts 10
```

#### Step 2: Process IoT Data
```bash
python src/data_preprocessing.py
```

#### Step 3: Run Security System
```bash
python src/iot_security_system.py
```

#### Step 4: Start API Server (Optional)
```bash
python src/api_server.py
```

### 7.2 Using the API

#### Example: Register Data via API

```python
import requests

url = "http://localhost:5000/api/register"
data = {
    "device_id": "SENSOR_001",
    "sensor_data": {
        "temperature": 25.5,
        "humidity": 60.2,
        "pressure": 1013.25
    }
}

response = requests.post(url, json=data)
print(response.json())
```

#### Example: Verify Data

```python
import requests

url = "http://localhost:5000/api/verify"
data = {
    "sensor_data": {
        "temperature": 25.5,
        "humidity": 60.2,
        "pressure": 1013.25
    }
}

response = requests.post(url, json=data)
result = response.json()

if result['integrity_verified']:
    print("✓ Data integrity confirmed!")
else:
    print("✗ Data has been tampered!")
```

---

## 8. TESTING PROCEDURES

### 8.1 Unit Testing

Test individual components:

```bash
# Test hashing module
python src/crypto_utils.py

# Test blockchain client
python src/blockchain_client.py
```

### 8.2 Integration Testing

Test complete workflow:

```bash
python src/iot_security_system.py
```

### 8.3 API Testing

Test all API endpoints:

```bash
# Start API server first
python src/api_server.py

# In new terminal, run tests
python test_api.py
```

### 8.4 Tampering Detection Test

```bash
python test_tampering.py
```

---

## 9. RESULTS AND EVALUATION

### 9.1 Performance Metrics

**System successfully achieved:**
- ✅ 100% success rate for data registration
- ✅ 20/20 records registered on blockchain
- ✅ Zero transaction failures
- ✅ Consistent hash generation
- ✅ Accurate tamper detection

### 9.2 Security Evaluation

**Integrity Protection:**
- All data hashes stored immutably
- Tampering immediately detected
- Complete audit trail maintained

**Decentralization:**
- No single point of failure
- Distributed across blockchain nodes
- Transparent verification

---

## 10. TROUBLESHOOTING

### 10.1 Common Issues

**Problem:** Cannot connect to blockchain  
**Solution:** Ensure Ganache is running on port 8545

**Problem:** Out of gas error  
**Solution:** Increase GAS_LIMIT in config.py

**Problem:** Account balance is 0  
**Solution:** Use different Ganache account or restart Ganache

### 10.2 Debugging

Enable verbose logging in code:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

## 11. FUTURE ENHANCEMENTS

### Potential Improvements:

1. **Machine Learning Integration:** Anomaly detection for sensor data
2. **Multi-Chain Support:** Deploy on multiple blockchain networks
3. **Web Dashboard:** Visual interface for monitoring
4. **Mobile App:** Native iOS/Android applications
5. **Advanced Analytics:** Real-time data analytics
6. **Scalability:** Support for millions of IoT devices

---

## 12. REFERENCES

- Nakamoto, S. (2008). Bitcoin: A Peer-to-Peer Electronic Cash System
- Ethereum Project. (2023). Ethereum Documentation
- Web3.py Documentation
- Flask Framework Documentation
- Solidity Documentation

---

## APPENDIX A: PROJECT File Structure

```
blockchain-iot-security/
│
├── contracts/
│   └── IoTDataRegistry.sol
│
├── scripts/
│   └── deploy.js
│
├── data/
│   ├── processed_iot_data.csv
│   ├── iot_features.csv
│   └── sample_iot_data.csv
│
├── results/
│   └── blockchain_registration_results.json
│
├── src/
│   ├── config.py
│   ├── crypto_utils.py
│   ├── blockchain_client.py
│   ├── data_preprocessing.py
│   ├── iot_security_system.py
│   └── api_server.py
│
├── tests/
│   ├── test_tampering.py
│   └── test_api.py
│
├── contract_info.json
├── hardhat.config.js
├── package.json
└── README.md
```

---

**End of Documentation**

*For questions or support, contact: Oyelade Paul Oluwafemi*  
*Institution: Osun State University, Osogbo*  
*Department: Computer Science*
