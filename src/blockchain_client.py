# src/blockchain_client.py
"""
Blockchain client for interacting with Ethereum smart contracts
Handles Web3 connection, transaction submission, and data verification
"""

import os 
from web3 import Web3
from eth_account import Account
import json
from typing import Dict, Optional
from pathlib import Path
import sys

# Add src to path for imports
sys.path.append(str(Path(__file__).parent))

from config import config
from crypto_utils import CryptoHasher

class BlockchainClient:
    """
    Client for interacting with Ethereum blockchain and IoT smart contract
    """
    
 def __init__(self, contract_address: Optional[str] = None, contract_abi: Optional[list] = None):
        """
        Initialize blockchain client
        
        Args:
            contract_address: Deployed smart contract address
            contract_abi: Contract ABI (Application Binary Interface)
        """
        print("=" * 70)
        print("BLOCKCHAIN CLIENT INITIALIZATION")
        print("=" * 70)
        
        # Connect to blockchain
        blockchain_url = os.getenv("ALCHEMY_URL", "http://127.0.0.1:8545")
        self.w3 = Web3(Web3.HTTPProvider(blockchain_url))
        
        # Verify connection
        if not self.w3.is_connected():
            raise ConnectionError(
                f"Failed to connect to blockchain at {blockchain_url}\n"
                "Check your ALCHEMY_URL environment variable!"
            )
        
        print(f"Connected to blockchain: {blockchain_url}")
        
        # Set default account
        self.account = config.OWNER_ADDRESS
        self.private_key = config.OWNER_PRIVATE_KEY
        
        # Check account balance
        balance = self.w3.eth.get_balance(self.account)
        balance_eth = self.w3.from_wei(balance, 'ether')
        print(f"✓ Account: {self.account}")
        print(f"✓ Balance: {balance_eth} ETH")
        
        # Load smart contract
        if contract_address and contract_abi:
            self._load_contract(contract_address, contract_abi)
        else:
            self._load_contract_from_file()
        
        print("=" * 70)
     
    
    def _load_contract_from_file(self):
        """Load contract info from contract_info.json"""
        try:
            with open(config.CONTRACT_INFO_FILE, 'r') as f:
                contract_info = json.load(f)
            
            self.contract_address = Web3.to_checksum_address(contract_info['address'])
            self.contract_abi = contract_info['abi']
            
            self._load_contract(self.contract_address, self.contract_abi)
            
        except FileNotFoundError:
            raise FileNotFoundError(
                f"Contract info file not found: {config.CONTRACT_INFO_FILE}\n"
                "Please deploy the smart contract first!"
            )
        except Exception as e:
            raise Exception(f"Error loading contract info: {str(e)}")
    
    def _load_contract(self, address: str, abi: list):
        """Load contract instance"""
        self.contract_address = Web3.to_checksum_address(address)
        self.contract_abi = abi
        
        self.contract = self.w3.eth.contract(
            address=self.contract_address,
            abi=self.contract_abi
        )
        
        print(f"✓ Smart contract loaded: {self.contract_address}")
    
    def register_data_hash(
        self, 
        data_hash: str, 
        device_id: str
    ) -> Dict:
        """
        Register IoT data hash on blockchain
        
        Args:
            data_hash: SHA-256 hash of data (hex string)
            device_id: Device identifier
            
        Returns:
            Transaction receipt dictionary
        """
        try:
            # Convert hash to bytes32
            if data_hash.startswith('0x'):
                hash_bytes = Web3.to_bytes(hexstr=data_hash)
            else:
                hash_bytes = Web3.to_bytes(hexstr='0x' + data_hash)
            
            # Check if hash already exists on blockchain (IMPORTANT - avoids duplicates)
            try:
                existing_record = self.contract.functions.getDataRecord(hash_bytes).call()
                if existing_record[4]:  # exists field is True
                    print(f"  ⊘ Data already registered (duplicate)")
                    return {
                        'success': False,
                        'duplicate': True,
                        'error': 'Data already registered on blockchain',
                        'data_hash': data_hash,
                        'device_id': device_id
                    }
            except Exception as check_err:
                print(f"  ⚠ Warning: Could not check for duplicates: {str(check_err)}")
            
            # Get nonce
            nonce = self.w3.eth.get_transaction_count(self.account)
            
            # Build transaction
            transaction = self.contract.functions.registerData(
                hash_bytes,
                device_id
            ).build_transaction({
                'from': self.account,
                'nonce': nonce,
                'gas': config.GAS_LIMIT,
                'gasPrice': config.GAS_PRICE
            })
            
            # Sign transaction
            signed_txn = self.w3.eth.account.sign_transaction(
                transaction, 
                private_key=self.private_key
            )
            
            # Send transaction (support both old and new eth-account versions)
            try:
                raw_transaction = signed_txn.rawTransaction
            except AttributeError:
                raw_transaction = signed_txn.raw_transaction
            
            tx_hash = self.w3.eth.send_raw_transaction(raw_transaction)
            
            # Wait for receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            success = tx_receipt['status'] == 1
            
            if success:
                print(f"  ✓ Data registered | TX: {tx_hash.hex()[:16]}...")
            else:
                print(f"  ✗ Registration failed | TX: {tx_hash.hex()[:16]}...")
            
            return {
                'success': success,
                'duplicate': False,
                'tx_hash': tx_hash.hex(),
                'block_number': tx_receipt['blockNumber'],
                'gas_used': tx_receipt['gasUsed'],
                'data_hash': data_hash,
                'device_id': device_id
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Provide user-friendly error messages
            if 'insufficient funds' in error_msg.lower():
                user_msg = "Account has insufficient balance. Please ensure your account has enough ETH to pay for transaction fees."
            elif 'nonce too low' in error_msg.lower():
                user_msg = "Transaction nonce error. Please try again."
            elif 'already registered' in error_msg.lower():
                user_msg = "This data has already been registered on the blockchain."
                return {
                    'success': False,
                    'duplicate': True,
                    'error': user_msg,
                    'data_hash': data_hash,
                    'device_id': device_id
                }
            elif 'out of gas' in error_msg.lower():
                user_msg = "Transaction ran out of gas. Please try with a higher gas limit."
            elif 'connection' in error_msg.lower() or 'connect' in error_msg.lower():
                user_msg = "Failed to connect to blockchain. Please ensure Ganache is running on http://127.0.0.1:8545"
            else:
                user_msg = f"Registration error: {error_msg[:100]}"
            
            print(f"  ✗ Registration failed: {user_msg}")
            return {
                'success': False,
                'duplicate': False,
                'error': user_msg,
                'data_hash': data_hash,
                'device_id': device_id
            }
    
    def verify_data_hash(self, data_hash: str) -> Dict:
        """
        Verify if data hash exists on blockchain
        
        Args:
            data_hash: Hash to verify
            
        Returns:
            Verification result with record details
        """
        try:
            # Convert hash to bytes32
            if data_hash.startswith('0x'):
                hash_bytes = Web3.to_bytes(hexstr=data_hash)
            else:
                hash_bytes = Web3.to_bytes(hexstr='0x' + data_hash)
            
            # Call smart contract view function
            record = self.contract.functions.getDataRecord(hash_bytes).call()
            
            # record = (dataHash, deviceAddress, timestamp, deviceId, exists)
            if record[4]:  # exists field
                return {
                    'exists': True,
                    'data_hash': data_hash,
                    'device_address': record[1],
                    'timestamp': record[2],
                    'device_id': record[3],
                    'blockchain_hash': record[0].hex()
                }
            else:
                return {
                    'exists': False,
                    'data_hash': data_hash
                }
                
        except Exception as e:
            print(f"  ✗ Verification error: {str(e)}")
            return {
                'exists': False,
                'error': str(e),
                'data_hash': data_hash
            }
    
    def get_total_records(self) -> int:
        """Get total number of registered records"""
        try:
            # Call the getTotalRecords function from the smart contract
            total = self.contract.functions.getTotalRecords().call()
            if isinstance(total, int):
                return total
            else:
                # If not an integer, try to convert
                return int(total)
        except AttributeError as e:
            print(f"✗ Contract method error (getTotalRecords not found): {str(e)}")
            return 0
        except Exception as e:
            print(f"✗ Error calling getTotalRecords(): {str(e)}")
            # Try alternative: access registeredHashes length directly
            try:
                hashes_array = self.contract.functions.registeredHashes(0).call()
                return len(hashes_array) if hashes_array else 0
            except:
                return 0
    
    def get_contract_owner(self) -> str:
        """Get contract owner address"""
        try:
            return self.contract.functions.owner().call()
        except Exception as e:
            print(f"Error getting owner: {str(e)}")
            return ""
    
    def find_device_records(self, device_id: str) -> Dict:
        """
        Find all blockchain records for a specific device ID
        
        Args:
            device_id: Device identifier to search for
            
        Returns:
            Dictionary with found records
        """
        try:
            total_records = self.get_total_records()
            found_records = []
            
            if total_records == 0:
                return {
                    'found': False,
                    'device_id': device_id,
                    'records': [],
                    'message': 'No records found on blockchain'
                }
            
            # Iterate through all registered hashes
            for i in range(total_records):
                try:
                    # Get hash at index i
                    data_hash = self.contract.functions.registeredHashes(i).call()
                    
                    # Get record details
                    record = self.contract.functions.getDataRecord(data_hash).call()
                    
                    # record = (dataHash, deviceAddress, timestamp, deviceId, exists)
                    if record[4] and record[3] == device_id:  # exists and device_id matches
                        found_records.append({
                            'data_hash': data_hash.hex(),
                            'device_id': record[3],
                            'device_address': record[1],
                            'timestamp': record[2],
                            'exists': record[4]
                        })
                except Exception as e:
                    continue
            
            if found_records:
                return {
                    'found': True,
                    'device_id': device_id,
                    'records': found_records,
                    'count': len(found_records),
                    'message': f'Found {len(found_records)} record(s) for device {device_id}'
                }
            else:
                return {
                    'found': False,
                    'device_id': device_id,
                    'records': [],
                    'message': f'No records found for device {device_id}'
                }
                
        except Exception as e:
            print(f"Error finding device records: {str(e)}")
            return {
                'found': False,
                'device_id': device_id,
                'records': [],
                'error': str(e),
                'message': 'Error searching blockchain for device records'
            }

# Example usage and testing
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("BLOCKCHAIN CLIENT TEST")
    print("=" * 70)
    
    try:
        # Initialize client
        client = BlockchainClient()
        
        # Test: Get contract owner
        print("\n[Test 1] Get Contract Owner:")
        owner = client.get_contract_owner()
        print(f"Owner: {owner}")
        
        # Test: Get total records
        print("\n[Test 2] Get Total Records:")
        total = client.get_total_records()
        print(f"Total Records: {total}")
        
        # Test: Register a test hash
        print("\n[Test 3] Register Test Data:")
        test_data = {'device': 'TEST_DEVICE', 'value': 42}
        hasher = CryptoHasher()
        test_hash = hasher.generate_sha256_hash(test_data)
        print(f"Test Hash: {test_hash}")
        
        result = client.register_data_hash(test_hash, 'TEST_DEVICE')
        print(f"Registration Success: {result.get('success', False)}")
        
        # Test: Verify the hash
        print("\n[Test 4] Verify Data:")
        verification = client.verify_data_hash(test_hash)
        print(f"Data Exists: {verification.get('exists', False)}")
        
        if verification.get('exists'):
            print(f"Device ID: {verification.get('device_id')}")
            print(f"Timestamp: {verification.get('timestamp')}")
        
        print("\n" + "=" * 70)
        print("✅ Blockchain client tests completed!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
