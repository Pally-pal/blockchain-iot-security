# src/config.py
"""
Configuration file for IoT Blockchain Security System
"""

import os
from pathlib import Path

class Config:
    """System Configuration"""
    
    # Project Paths
    PROJECT_ROOT = Path(__file__).parent.parent.absolute()
    
    # Dataset Path (Your actual dataset location)
    DATASET_PATH = r"C:\Users\HP\Downloads\Paul's Final Year Project Documents\Blockchain_dataset\sensor_data.csv"
    
    # Directory Paths
    DATA_DIR = PROJECT_ROOT / "data"
    RESULTS_DIR = PROJECT_ROOT / "results"
    LOGS_DIR = PROJECT_ROOT / "logs"
    CONTRACTS_DIR = PROJECT_ROOT / "contracts"
    
    # Processed Data Files
    PROCESSED_DATA_FILE = DATA_DIR / "processed_iot_data.csv"
    FEATURES_FILE = DATA_DIR / "iot_features.csv"
    SAMPLE_DATA_FILE = DATA_DIR / "sample_iot_data.csv"
    
    # Blockchain Network Configuration
    GANACHE_URL = "http://127.0.0.1:8545"
    NETWORK_ID = 1337
    
    # Account Configuration (FROM YOUR GANACHE OUTPUT)
    OWNER_ADDRESS = "0xB45e8457a2057493954963868CDA334Bf26B5014"
    OWNER_PRIVATE_KEY = "0x1d63bcf56bacc9b26db10d9881afd44bb3f785fee2f56c876f0c0f7b8f22ed4e"
    
    # Smart Contract Configuration
    GAS_LIMIT = 3000000
    GAS_PRICE = 20000000000  # 20 Gwei
    
    # Contract Info File
    CONTRACT_INFO_FILE = PROJECT_ROOT / "contract_info.json"
    
    # API Configuration
    API_HOST = "0.0.0.0"
    API_PORT = 5000
    
    # Processing Configuration
    BATCH_SIZE = 10  # Number of records to process in each batch
    MAX_RECORDS = 100  # Maximum records for testing
    
    # Logging Configuration
    LOG_LEVEL = "INFO"
    LOG_FILE = LOGS_DIR / "system.log"
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.DATA_DIR, cls.RESULTS_DIR, cls.LOGS_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate_paths(cls):
        """Validate that critical paths exist"""
        if not Path(cls.DATASET_PATH).exists():
            raise FileNotFoundError(f"Dataset not found at: {cls.DATASET_PATH}")
        
        if not cls.CONTRACT_INFO_FILE.exists():
            raise FileNotFoundError(
                f"Contract info not found. Please deploy the smart contract first.\n"
                f"Expected file: {cls.CONTRACT_INFO_FILE}"
            )
        
        return True

# Create configuration instance
config = Config()

# Ensure directories exist
config.ensure_directories()

# Print configuration on import (for debugging)
if __name__ == "__main__":
    print("=" * 70)
    print("CONFIGURATION SETTINGS")
    print("=" * 70)
    print(f"Project Root: {config.PROJECT_ROOT}")
    print(f"Dataset Path: {config.DATASET_PATH}")
    print(f"Ganache URL: {config.GANACHE_URL}")
    print(f"Owner Address: {config.OWNER_ADDRESS}")
    print(f"Contract Info: {config.CONTRACT_INFO_FILE}")
    print("=" * 70)
