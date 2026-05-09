# IoT Blockchain Security System

## Project Overview

This project implements an intelligent blockchain-based security system for Internet of Things (IoT) data. It provides cryptographic hashing, immutable blockchain storage, and comprehensive audit trails for IoT sensor data.

**Author:** Oyelade Paul Oluwafemi  
**Institution:** Osun State University, Osogbo

---

## Key Features

✅ **Data Integrity** - SHA-256 cryptographic hashing  
✅ **Immutability** - Blockchain-based permanent storage  
✅ **Auditability** - Complete transparent audit trails  
✅ **Decentralization** - No single point of failure  
✅ **REST API** - Easy integration with IoT systems  
✅ **Web Dashboard** - User-friendly interface  

---

## System Architecture

### Components

1. **Smart Contract (IoTDataRegistry.sol)**
   - Solidity contract deployed on Ethereum
   - Manages data registration and verification
   - Handles audit logs

2. **Blockchain Client (blockchain_client.py)**
   - Web3.py integration
   - Contract interaction
   - Data registration and verification

3. **Security System (iot_security_system.py)**
   - Crypto hashing utilities
   - Data preprocessing
   - Blockchain integration

4. **REST API Server (api_server_complete.py)**
   - Flask-based REST API
   - Health checks
   - Data registration and verification endpoints

5. **Frontend (frontend/)**
   - HTML/CSS/JavaScript dashboard
   - Real-time system monitoring
   - Data registration interface

---

## Prerequisites

- **Node.js 14+** - For smart contract development
- **Python 3.9+** - For backend services
- **Ganache CLI** - Local Ethereum blockchain
- **Git** - Version control

---

## Installation

### 1. Clone and Setup

```bash
cd blockchain-iot-security
python -m venv blockchain_env
# On Windows:
blockchain_env\Scripts\activate
# On macOS/Linux:
source blockchain_env/bin/activate
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Node Dependencies

```bash
npm install
```

---

## Running the System

### Step 1: Start Ganache (Local Blockchain)

```bash
ganache-cli --port 8545 --networkId 1337 --accounts 10
```

Keep this terminal open. You should see 10 Ethereum accounts with 100 ETH each.

### Step 2: Deploy Smart Contract

In a new terminal:

```bash
npx hardhat run scripts/deploy.js --network localhost
```

This creates `contract_info.json` with the deployed contract address.

### Step 3: Start API Server

```bash
python src/api_server_complete.py
```

The API will be available at `http://localhost:5000`

### Step 4: Start Frontend Server

In another terminal:

```bash
cd frontend
python serve.py
```

The frontend will be available at `http://localhost:8000`

---

## API Endpoints

### Health Check
```
GET /api/health
```

### Register IoT Data
```
POST /api/register
Content-Type: application/json

{
  "device_id": "DEVICE_001",
  "sensor_data": {
    "temperature": 25.5,
    "humidity": 60.2
  }
}
```

### Verify Data Integrity
```
POST /api/verify
Content-Type: application/json

{
  "sensor_data": {
    "temperature": 25.5,
    "humidity": 60.2
  }
}
```

### Generate Hash
```
POST /api/hash
Content-Type: application/json

{
  "data": {
    "key": "value"
  }
}
```

### Get Total Records
```
GET /api/records
```

### Get Statistics
```
GET /api/stats
```

### Get Audit Report
```
GET /api/audit
```

---

## Configuration

Edit `src/config.py` to customize:

- **GANACHE_URL** - Blockchain endpoint (default: http://127.0.0.1:8545)
- **API_HOST** - API server host (default: 0.0.0.0)
- **API_PORT** - API server port (default: 5000)
- **GAS_LIMIT** - Ethereum gas limit for transactions
- **BATCH_SIZE** - Records to process in each batch

---

## Project Structure

```
blockchain-iot-security/
├── contracts/              # Smart contract source
│   └── IoTDataRegistry.sol
├── scripts/               # Deployment scripts
│   └── deploy.js
├── src/                   # Python backend
│   ├── api_server_complete.py
│   ├── blockchain_client.py
│   ├── config.py
│   ├── crypto_utils.py
│   ├── iot_security_system.py
│   └── data_preprocessing.py
├── frontend/              # Web dashboard
│   ├── index.html
│   ├── app.js
│   ├── styles.css
│   └── serve.py
├── data/                  # Sample data
│   ├── sample_iot_data.csv
│   └── processed_iot_data.csv
├── artifacts/             # Compiled contracts
├── hardhat.config.js      # Hardhat configuration
├── package.json           # Node dependencies
└── requirements.txt       # Python dependencies
```

---

## Usage Examples

### Example 1: Register Sensor Data

```python
import requests
import json

data = {
    "device_id": "SENSOR_001",
    "sensor_data": {
        "temperature": 23.5,
        "humidity": 55.2,
        "pressure": 1013.25
    }
}

response = requests.post(
    'http://localhost:5000/api/register',
    json=data
)

result = response.json()
print(f"Data Hash: {result['data_hash']}")
print(f"Transaction Hash: {result['tx_hash']}")
```

### Example 2: Verify Data Integrity

```python
import requests

data = {
    "sensor_data": {
        "temperature": 23.5,
        "humidity": 55.2,
        "pressure": 1013.25
    }
}

response = requests.post(
    'http://localhost:5000/api/verify',
    json=data
)

result = response.json()
if result['integrity_verified']:
    print("Data integrity confirmed!")
else:
    print("Data has been tampered with!")
```

---

## Troubleshooting

### Issue: "Failed to connect to blockchain"
- Ensure Ganache is running on port 8545
- Check that the URL in config.py matches your Ganache setup

### Issue: "Contract info not found"
- Run the deployment script: `npx hardhat run scripts/deploy.js --network localhost`
- Verify `contract_info.json` is created in the project root

### Issue: "Account balance is 0 ETH"
- This occurs if using a different account than Ganache's default
- Use the default first account from Ganache
- Or transfer ETH from a funded account

### Issue: "API not responding"
- Check that Flask server is running: `python src/api_server_complete.py`
- Verify port 5000 is not in use: `netstat -an | findstr :5000`

### Issue: "Frontend shows 'System Error'"
- Ensure API server is running on port 5000
- Check browser console for specific errors
- Verify API URL in Settings (default: http://localhost:5000)

---

## Testing

### Run Unit Tests

```bash
pytest tests/ -v
```

### Test API Endpoints

```bash
python src/api_test_script.py
```

### Process Sample Data

```bash
python src/iot_security_system.py
```

---

## System Information

**Contract Address:** See `contract_info.json`  
**Network:** Ganache (http://127.0.0.1:8545)  
**Port:** 5000 (API), 8000 (Frontend)  
**Solidity Version:** 0.8.0  
**Python Version:** 3.9+  

---

## Known Limitations

⚠️ **Ganache-only:** Currently configured for local Ganache network only
⚠️ **Single Account:** Uses single Ethereum account for all transactions
⚠️ **No Authentication:** API has no user authentication
⚠️ **Test Data:** Uses sample CSV files, not real-time IoT streams

---

## Future Enhancements

- [ ] Multi-user authentication and authorization
- [ ] Real-time IoT data streaming
- [ ] Multiple blockchain network support
- [ ] Advanced analytics dashboard
- [ ] Machine learning anomaly detection
- [ ] Distributed storage (IPFS)
- [ ] Mobile app interface
- [ ] Performance optimization

---

## References

- [Ethereum Documentation](https://ethereum.org/en/developers/)
- [Solidity Smart Contracts](https://soliditylang.org/)
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Flask REST API](https://flask.palletsprojects.com/)
- [Hardhat Framework](https://hardhat.org/)

---

## License

This project is part of an academic final year project at Osun State University.

---

## Support

For issues or questions, please refer to the documentation or contact the project author.

**Last Updated:** May 7, 2026
