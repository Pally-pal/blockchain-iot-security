# PROJECT SETUP AND INITIALIZATION
# Run this script first to set up your complete project structure

import os
import json
import subprocess
import sys

class ProjectSetup:
    def __init__(self):
        # Your dataset path
        self.dataset_path = r"C:\Users\HP\Downloads\Paul's Final Year Project Documents\Blockchain_dataset\sensor_data.csv"
        
        # Project root (where this script is located)
        self.project_root = os.path.dirname(os.path.abspath(__file__))
        
        print("=" * 70)
        print("INTELLIGENT BLOCKCHAIN SYSTEM FOR SECURING IOT DATA")
        print("PROJECT SETUP AND INITIALIZATION")
        print("=" * 70)
        print(f"\nProject Root: {self.project_root}")
        print(f"Dataset Path: {self.dataset_path}")
    
    def create_directory_structure(self):
        """Create project directory structure"""
        print("\n[1/6] Creating directory structure...")
        
        directories = [
            'contracts',
            'scripts',
            'data',
            'results',
            'src',
            'tests',
            'logs',
            'config'
        ]
        
        for directory in directories:
            dir_path = os.path.join(self.project_root, directory)
            os.makedirs(dir_path, exist_ok=True)
            print(f"  ✓ Created: {directory}/")
        
        print("  ✓ Directory structure created successfully")
    
    def check_dataset(self):
        """Verify dataset exists"""
        print("\n[2/6] Checking dataset...")
        
        if os.path.exists(self.dataset_path):
            file_size = os.path.getsize(self.dataset_path) / (1024 * 1024)  # MB
            print(f"  ✓ Dataset found: {file_size:.2f} MB")
            
            # Quick preview
            import pandas as pd
            df = pd.read_csv(self.dataset_path, nrows=5)
            print(f"  ✓ Columns: {list(df.columns)}")
            print(f"  ✓ Shape preview: {df.shape}")
        else:
            print(f"  ✗ ERROR: Dataset not found at {self.dataset_path}")
            print("  Please verify the path and try again.")
            sys.exit(1)
    
    def create_config_file(self):
        """Create configuration file"""
        print("\n[3/6] Creating configuration file...")
        
        config_content = f'''# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """System Configuration"""
    
    # Project Paths
    PROJECT_ROOT = r"{self.project_root}"
    DATASET_PATH = r"{self.dataset_path}"
    DATA_DIR = os.path.join(PROJECT_ROOT, "data")
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "results")
    LOGS_DIR = os.path.join(PROJECT_ROOT, "logs")
    
    # Blockchain Network Configuration
    GANACHE_URL = "http://127.0.0.1:8545"
    NETWORK_ID = 1337
    
    # Account Configuration (Update after Ganache starts)
    OWNER_ADDRESS = ""  # Will be set from Ganache
    OWNER_PRIVATE_KEY = ""  # Will be set from Ganache
    
    # Smart Contract Configuration
    GAS_LIMIT = 6721975
    GAS_PRICE = 20000000000  # 20 Gwei
    
    # Contract Info File
    CONTRACT_INFO_FILE = os.path.join(PROJECT_ROOT, "contract_info.json")
    
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    
    # Processing Configuration
    BATCH_SIZE = 10
    MAX_RECORDS = 100  # Limit for testing
    
    @classmethod
    def update_blockchain_credentials(cls, address, private_key):
        """Update blockchain credentials from Ganache"""
        cls.OWNER_ADDRESS = address
        cls.OWNER_PRIVATE_KEY = private_key

config = Config()
'''
        
        config_path = os.path.join(self.project_root, 'src', 'config.py')
        with open(config_path, 'w') as f:
            f.write(config_content)
        
        print(f"  ✓ Configuration file created: src/config.py")
    
    def create_requirements_file(self):
        """Create requirements.txt"""
        print("\n[4/6] Creating requirements.txt...")
        
        requirements = '''# Core Python Libraries
pandas==2.0.0
numpy==1.24.0

# Blockchain Libraries
web3==6.0.0
eth-account==0.8.0
py-solc-x==1.1.1

# API Libraries
flask==2.3.0
flask-cors==4.0.0

# Utilities
python-dotenv==1.0.0
requests==2.31.0

# Testing
pytest==7.4.0
pytest-cov==4.1.0

# Performance & Visualization
matplotlib==3.7.1
seaborn==0.12.2

# Development
ipython==8.14.0
jupyter==1.0.0
'''
        
        req_path = os.path.join(self.project_root, 'requirements.txt')
        with open(req_path, 'w') as f:
            f.write(requirements)
        
        print(f"  ✓ requirements.txt created")
    
    def create_env_template(self):
        """Create .env template"""
        print("\n[5/6] Creating .env template...")
        
        env_content = '''# Blockchain Configuration
GANACHE_URL=http://127.0.0.1:8545
NETWORK_ID=1337

# Account Credentials (Update from Ganache)
OWNER_ADDRESS=
OWNER_PRIVATE_KEY=

# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
'''
        
        env_path = os.path.join(self.project_root, '.env.template')
        with open(env_path, 'w') as f:
            f.write(env_content)
        
        print(f"  ✓ .env template created")
    
    def create_readme(self):
        """Create README.md"""
        print("\n[6/6] Creating README.md...")
        
        readme_content = f'''# Intelligent Blockchain System for Securing IoT Data

**Author:** Oyelade Paul Oluwafemi  
**Matric No:** 2021/37014  
**Institution:** Osun State University, Osogbo  
**Department:** Computer Science

## Project Overview

This project implements an intelligent blockchain-based system for securing Internet of Things (IoT) data using cryptographic hashing and smart contracts.

## Features

- ✅ SHA-256 cryptographic hashing for data integrity
- ✅ Ethereum blockchain integration for immutable storage
- ✅ Smart contract-based data registry
- ✅ Automated tamper detection
- ✅ REST API for external integration
- ✅ Comprehensive testing suite
- ✅ Performance evaluation metrics

## Project Structure

```
project/
├── contracts/          # Solidity smart contracts
├── scripts/           # Deployment scripts
├── data/              # Processed datasets
├── results/           # Evaluation results
├── src/               # Source code
│   ├── config.py
│   ├── crypto_utils.py
│   ├── blockchain_client.py
│   ├── data_preprocessing.py
│   ├── iot_security_system.py
│   └── api_server.py
├── tests/             # Test suite
└── requirements.txt
```

## Installation

### Prerequisites
- Python 3.10+
- Node.js v16+
- Ganache CLI

### Setup Steps

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Ganache:**
```bash
npm install -g ganache-cli
```

3. **Install Hardhat (for smart contracts):**
```bash
npm install --save-dev hardhat
```

## Quick Start

### 1. Start Ganache (Terminal 1)
```bash
ganache-cli --port 8545 --networkId 1337
```

### 2. Update Configuration
Copy the first account address and private key from Ganache output to `src/config.py`

### 3. Deploy Smart Contract (Terminal 2)
```bash
npx hardhat compile
npx hardhat run scripts/deploy.js --network localhost
```

### 4. Run Data Preprocessing
```bash
python src/data_preprocessing.py
```

### 5. Run Main System
```bash
python src/iot_security_system.py
```

### 6. Start API Server
```bash
python src/api_server.py
```

## Dataset

**Location:** `{self.dataset_path}`

## API Endpoints

- `GET /api/health` - System health check
- `POST /api/register` - Register IoT data
- `POST /api/verify` - Verify data integrity
- `GET /api/audit` - Get audit report
- `GET /api/records` - Get total records

## Testing

```bash
python -m pytest tests/ -v
```

## Performance Evaluation

```bash
python performance_evaluation.py
```

## License

This project is submitted as part of academic requirements for B.Sc Computer Science.

## Contact

**Email:** oyeladepaul@example.com  
**Supervisor:** Dr. E.O Ojo
'''
        
        readme_path = os.path.join(self.project_root, 'README.md')
        with open(readme_path, 'w') as f:
            f.write(readme_content)
        
        print(f"  ✓ README.md created")
    
    def display_next_steps(self):
        """Display next steps"""
        print("\n" + "=" * 70)
        print("SETUP COMPLETE!")
        print("=" * 70)
        print("\n📋 NEXT STEPS:\n")
        print("1. Install Python dependencies:")
        print("   pip install -r requirements.txt\n")
        
        print("2. Install Node.js dependencies:")
        print("   npm install -g ganache-cli")
        print("   npm install --save-dev hardhat\n")
        
        print("3. Start Ganache in a new terminal:")
        print("   ganache-cli --port 8545 --networkId 1337\n")
        
        print("4. Copy the FIRST account details from Ganache and update:")
        print("   - src/config.py (OWNER_ADDRESS and OWNER_PRIVATE_KEY)\n")
        
        print("5. Deploy smart contract:")
        print("   npx hardhat compile")
        print("   npx hardhat run scripts/deploy.js --network localhost\n")
        
        print("6. Run data preprocessing:")
        print("   python src/data_preprocessing.py\n")
        
        print("7. Run the complete system:")
        print("   python src/iot_security_system.py\n")
        
        print("=" * 70)
        print("\n✅ Project structure is ready!")
        print(f"📁 Project location: {self.project_root}\n")
    
    def run_setup(self):
        """Run complete setup"""
        try:
            self.create_directory_structure()
            self.check_dataset()
            self.create_config_file()
            self.create_requirements_file()
            self.create_env_template()
            self.create_readme()
            self.display_next_steps()
            
            return True
        except Exception as e:
            print(f"\n✗ Setup failed: {str(e)}")
            return False

if __name__ == "__main__":
    setup = ProjectSetup()
    setup.run_setup()
