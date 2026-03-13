# Intelligent Blockchain System for Securing IoT Data

**Author:** Oyelade Paul Oluwafemi  
**Matric No:** 2021/37014  
**Institution:** Osun State University, Osogbo  
**Department:** Computer Science  
**Supervisor:** Dr. E.O Ojo

---

##  Project Overview

This project implements an **intelligent blockchain-based system for securing Internet of Things (IoT) data** using cryptographic hashing and Ethereum smart contracts. The system ensures data integrity, immutability, and tamper detection through blockchain technology and advanced cryptographic techniques.

### Key Innovation
Combines SHA-256 cryptographic hashing with Ethereum blockchain to create a decentralized, immutable registry for IoT sensor data, preventing unauthorized modifications and ensuring complete audit trails.

---

## Features

- ✅ **SHA-256 Cryptographic Hashing** - Ensures data integrity through cryptographic verification
- ✅ **Ethereum Blockchain Integration** - Immutable storage of data hashes on the blockchain
- ✅ **Smart Contract-Based Registry** - Solidity smart contracts for data management
- ✅ **Automated Tamper Detection** - Real-time detection of data modifications
- ✅ **REST API** - Easy integration with external systems and IoT platforms
- ✅ **Comprehensive Testing Suite** - Unit and integration tests for reliability
- ✅ **Performance Evaluation** - Metrics for system efficiency and scalability
- ✅ **Web Interface** - User-friendly dashboard for monitoring and management
- ✅ **Audit Logging** - Complete transaction history and audit trails
- ✅ **Multi-tenant Support** - Isolated data environments for multiple IoT networks

---

## 📁 Project Structure

```
blockchain-iot-security/
├── contracts/                  # Solidity smart contracts
│   └── IoTDataRegistry.sol    # Main smart contract for data registry
├── scripts/                    # Deployment and utility scripts
│   ├── deploy.js              # Smart contract deployment script
│   └── verify.js              # Verification utility
├── src/                        # Python source code
│   ├── config.py              # Configuration management
│   ├── crypto_utils.py        # Cryptographic utilities (SHA-256)
│   ├── blockchain_client.py   # Blockchain interaction layer
│   ├── data_preprocessing.py  # IoT data preparation
│   ├── iot_security_system.py # Main system logic
│   └── api_server.py          # Flask REST API
├── data/                       # Processed IoT datasets
├── results/                    # Evaluation results and reports
├── tests/                      # Test suite
├── logs/                       # System logs
├── hardhat.config.js          # Hardhat configuration
├── package.json               # Node.js dependencies
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 🛠️ Tech Stack

### Blockchain & Smart Contracts
- **Solidity** - Smart contract language
- **Hardhat** - Smart contract development framework
- **Web3.py** - Python Ethereum integration
- **Ganache** - Local blockchain for testing

### Backend
- **Python 3.10+** - Primary programming language
- **Flask** - REST API framework
- **Pandas** - Data processing
- **NumPy** - Numerical computations

### Security & Cryptography
- **Hashlib** - SHA-256 cryptographic hashing
- **Eth-account** - Ethereum account management
- **Web3** - Blockchain interaction

---

## 📦 Installation

### Prerequisites

```bash
# System Requirements
- Python 3.10 or higher
- Node.js v16 or higher
- npm or yarn package manager
- Git
```

### Step 1: Clone Repository

```bash
git clone https://github.com/Pally-pal/blockchain-iot-security.git
cd blockchain-iot-security
```

### Step 2: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Install Node.js Dependencies

```bash
# Install Ganache (local blockchain)
npm install -g ganache-cli

# Install Hardhat (smart contract framework)
npm install --save-dev hardhat

# Initialize Hardhat (optional)
npx hardhat
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env with your configuration
nano .env
```

Required environment variables:
```env
GANACHE_URL=http://127.0.0.1:8545
NETWORK_ID=1337
OWNER_ADDRESS=<Your Ganache account address>
OWNER_PRIVATE_KEY=<Your Ganache private key>
API_HOST=0.0.0.0
API_PORT=5000
```

---

## 🚀 Quick Start

### Terminal 1: Start Local Blockchain

```bash
# Start Ganache on port 8545
ganache-cli --port 8545 --networkId 1337 --mnemonic "test test test test test test test test test test test junk"
```

**Note:** Copy the first account address and private key for configuration.

### Terminal 2: Deploy Smart Contract

```bash
# Compile smart contracts
npx hardhat compile

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Save the contract address (you'll need it)
```

### Terminal 3: Run Setup

```bash
# Update dataset path in setup_project.py if needed
python setup_project.py

# This will:
# - Create directory structure
# - Validate dataset
# - Generate configuration
# - Create requirements.txt
```

### Terminal 4: Data Preprocessing

```bash
# Preprocess IoT data
python src/data_preprocessing.py

# Processes raw sensor data and prepares for blockchain registration
```

### Terminal 5: Main System

```bash
# Run the main security system
python src/iot_security_system.py

# Processes data, computes hashes, and registers on blockchain
```

### Terminal 6: Start API Server

```bash
# Launch REST API
python src/api_server.py

# API runs on http://localhost:5000
```

---

## 📡 API Endpoints

### Health & Status
```
GET /api/health
Response: {"status": "healthy", "timestamp": "2026-03-13T10:30:00Z"}
```

### Data Registration
```
POST /api/register
Content-Type: application/json

{
  "sensor_id": "sensor_001",
  "timestamp": "2026-03-13T10:30:00Z",
  "temperature": 25.5,
  "humidity": 60.0,
  "data_hash": "abc123..."
}

Response: {"tx_hash": "0x...", "block_number": 123, "status": "confirmed"}
```

### Data Verification
```
POST /api/verify
Content-Type: application/json

{
  "data_hash": "abc123...",
  "sensor_id": "sensor_001"
}

Response: {"verified": true, "blockchain_hash": "abc123...", "timestamp": "..."}
```

### Audit Report
```
GET /api/audit?sensor_id=sensor_001&start_date=2026-03-01&end_date=2026-03-13
Response: [
  {
    "tx_hash": "0x...",
    "sensor_id": "sensor_001",
    "data_hash": "abc123...",
    "timestamp": "...",
    "block_number": 123
  }
]
```

### Get Statistics
```
GET /api/records
Response: {
  "total_records": 1000,
  "verified_records": 999,
  "failed_records": 1,
  "average_processing_time": 2.5
}
```

---

## 🧪 Testing

### Run All Tests

```bash
# Run pytest with verbose output
python -m pytest tests/ -v

# Run with coverage report
python -m pytest tests/ --cov=src --cov-report=html
```

### Run Specific Test Suite

```bash
# Test cryptographic functions
python -m pytest tests/test_crypto_utils.py -v

# Test blockchain operations
python -m pytest tests/test_blockchain_client.py -v

# Test API endpoints
python -m pytest tests/test_api_server.py -v
```

### Test Coverage

```bash
# Generate coverage report
python -m pytest tests/ --cov=src --cov-report=term-missing
```

---

## 📊 Dataset

### Data Format

The system uses IoT sensor data with the following structure:

```csv
timestamp,sensor_id,temperature,humidity,pressure,location
2026-03-13T10:00:00Z,sensor_001,25.5,60.0,1013.25,Room_A
2026-03-13T10:01:00Z,sensor_002,24.8,58.5,1013.20,Room_B
...
```

### Dataset Location

Update the path in `setup_project.py`:
```python
self.dataset_path = "path/to/your/sensor_data.csv"
```

### Supported Data Types
- **Temperature** (float) - Celsius
- **Humidity** (float) - Percentage (0-100)
- **Pressure** (float) - hPa
- **Timestamp** (ISO 8601) - UTC format
- **Location** (string) - Physical location identifier

---

## 🔐 Security Features

### Cryptographic Security
- **SHA-256 Hashing** - Industry-standard cryptographic hash function
- **Data Integrity** - Detect any unauthorized modifications
- **Immutable Records** - Blockchain ensures data cannot be altered retroactively

### Smart Contract Security
- **Access Control** - Only authorized parties can register data
- **Reentrancy Protection** - Guards against reentrancy attacks
- **Rate Limiting** - Prevents spam and abuse

### Network Security
- **TLS/SSL** - Optional HTTPS for API endpoints
- **API Authentication** - Bearer token authentication (configurable)
- **Firewall Rules** - Network isolation for sensitive components

---

## 📈 Performance Metrics

Expected performance on Intel i7 processor:

| Metric | Value |
|--------|-------|
| Data Hashing Speed | ~10,000 records/sec |
| Blockchain Registration | ~5-15 seconds/transaction |
| API Response Time | <500ms |
| Memory Usage | ~200MB (base) |
| Storage (1000 records) | ~50KB |

---

## 🐛 Troubleshooting

### Issue: Ganache Connection Failed

```
Error: Could not connect to http://127.0.0.1:8545

Solution:
1. Verify Ganache is running: ganache-cli --port 8545
2. Check network settings
3. Ensure no firewall blocks localhost:8545
```

### Issue: Smart Contract Deployment Failed

```
Error: Insufficient gas or account balance

Solution:
1. Verify you have the correct private key
2. Check account has sufficient balance in Ganache
3. Increase GAS_LIMIT in config.py
```

### Issue: Dataset Not Found

```
Error: Dataset not found at specified path

Solution:
1. Verify dataset path in setup_project.py
2. Ensure file permissions allow reading
3. Check file format is valid CSV
```

### Issue: API Port Already in Use

```
Error: Port 5000 already in use

Solution:
1. Change API_PORT in src/config.py
2. Or kill existing process: lsof -ti:5000 | xargs kill -9
```

---

## 📚 Documentation

- **Full Documentation**: See `PROJECT_DOCUMENTATION.md`
- **Execution Guide**: See `Step-by-Step Execution Guide.pdf`
- **Project Overview**: See `README.md - Project Overview.pdf`

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Commit changes: `git commit -m 'Add new feature'`
4. Push to branch: `git push origin feature/new-feature`
5. Submit a Pull Request

---

## 📝 License

This project is submitted as part of academic requirements for B.Sc Computer Science at Osun State University, Osogbo.

**Academic License** - For educational and research purposes only.

---

## 📧 Contact & Support

**Author:** Oyelade Paul Oluwafemi  
**Email:** oyeladepaul@example.com  
**Institution:** Osun State University, Osogbo  
**Supervisor:** Dr. E.O Ojo

### Getting Help

- 📖 Read the [Full Documentation](PROJECT_DOCUMENTATION.md)
- 📋 Check [Execution Guide](Step-by-Step%20Execution%20Guide.pdf)
- 🐛 Report issues on GitHub Issues
- 💬 Discussion available in GitHub Discussions

---

## 🎯 Future Enhancements

- [ ] Multi-chain support (Polygon, Binance Smart Chain)
- [ ] Mobile app for IoT monitoring
- [ ] Machine learning for anomaly detection
- [ ] Enhanced visualization dashboard
- [ ] Scalability improvements for large-scale deployments
- [ ] Integration with popular IoT platforms

---

**Last Updated:** March 13, 2026  
**Version:** 1.0.0
