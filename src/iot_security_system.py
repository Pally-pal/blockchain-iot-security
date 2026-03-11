# src/iot_security_system.py
"""
Main IoT Security System
Integrates data preprocessing, cryptographic hashing, and blockchain storage
"""

import pandas as pd
import json
import time
from datetime import datetime
from typing import List, Dict
from pathlib import Path
import sys

# Add src to path
sys.path.append(str(Path(__file__).parent))

from config import config
from crypto_utils import CryptoHasher
from blockchain_client import BlockchainClient

class IoTSecuritySystem:
    """
    Complete IoT Data Security System integrating
    cryptographic hashing and blockchain storage
    """
    
    def __init__(self):
        """Initialize security system"""
        print("=" * 70)
        print("IOT BLOCKCHAIN SECURITY SYSTEM")
        print("=" * 70)
        print(f"Initializing system...")
        print()
        
        self.hasher = CryptoHasher()
        self.blockchain = BlockchainClient()
        self.hash_registry = []
        
        print("\n✅ System initialized successfully!")
        print("=" * 70)
    
    def process_iot_data(
        self, 
        data_df: pd.DataFrame,
        batch_size: int = None,
        max_records: int = None
    ) -> List[Dict]:
        """
        Process IoT data: hash and register on blockchain
        
        Args:
            data_df: DataFrame containing IoT sensor data
            batch_size: Number of records to process in each batch
            max_records: Maximum number of records to process
            
        Returns:
            List of processing results
        """
        if batch_size is None:
            batch_size = config.BATCH_SIZE
        
        if max_records is None:
            max_records = config.MAX_RECORDS
        
        # Limit records for testing
        data_df = data_df.head(max_records)
        
        print(f"\n{'='*70}")
        print(f"PROCESSING {len(data_df)} IOT RECORDS")
        print("=" * 70)
        
        results = []
        total_records = len(data_df)
        
        for idx, row in data_df.iterrows():
            # Convert row to dictionary
            row_dict = row.to_dict()
            
            # Generate hash
            data_hash = self.hasher.hash_dataframe_row(row_dict)
            
            # Extract device ID
            device_id = row_dict.get('device_id', f'DEVICE_UNKNOWN_{idx}')
            
            # Register on blockchain
            print(f"\n[{idx+1}/{total_records}] Processing {device_id}...")
            print(f"  Hash: {data_hash[:32]}...")
            
            result = self.blockchain.register_data_hash(data_hash, device_id)
            
            # Store result
            record_info = {
                'index': int(idx),
                'device_id': device_id,
                'data_hash': data_hash,
                'blockchain_result': result,
                'timestamp': datetime.now().isoformat(),
                'original_data': {k: str(v) for k, v in row_dict.items()}  # Convert for JSON
            }
            
            results.append(record_info)
            self.hash_registry.append(record_info)
            
            # Batch delay to avoid overwhelming network
            if (idx + 1) % batch_size == 0:
                print(f"\n  ⏸ Batch complete. Processed {idx + 1} records.")
                time.sleep(1)  # Small delay between batches
        
        print("\n" + "=" * 70)
        print(f"PROCESSING COMPLETE")
        print("=" * 70)
        print(f"  Total processed: {len(results)}")
        print(f"  Successful: {sum(1 for r in results if r['blockchain_result'].get('success'))}")
        print(f"  Failed: {sum(1 for r in results if not r['blockchain_result'].get('success'))}")
        print("=" * 70)
        
        return results
    
    def verify_data_integrity(
        self, 
        original_data: Dict
    ) -> Dict:
        """
        Verify integrity of IoT data against blockchain
        
        Args:
            original_data: Original data dictionary
            
        Returns:
            Verification result
        """
        # Compute hash of original data
        computed_hash = self.hasher.hash_dataframe_row(original_data)
        
        # Check blockchain
        blockchain_record = self.blockchain.verify_data_hash(computed_hash)
        
        if blockchain_record['exists']:
            return {
                'integrity_verified': True,
                'message': 'Data integrity confirmed - hash matches blockchain record',
                'computed_hash': computed_hash,
                'blockchain_record': blockchain_record
            }
        else:
            return {
                'integrity_verified': False,
                'message': 'Data not found on blockchain or has been tampered',
                'computed_hash': computed_hash
            }
    
    def simulate_tampering_detection(
        self,
        original_data: Dict,
        tampered_data: Dict
    ) -> Dict:
        """
        Demonstrate tamper detection capability
        
        Args:
            original_data: Original registered data
            tampered_data: Modified data
            
        Returns:
            Detection result
        """
        print("\n" + "=" * 70)
        print("TAMPERING DETECTION SIMULATION")
        print("=" * 70)
        
        # Hash both datasets
        original_hash = self.hasher.hash_dataframe_row(original_data)
        tampered_hash = self.hasher.hash_dataframe_row(tampered_data)
        
        print(f"\nOriginal Data:  {original_data}")
        print(f"Tampered Data: {tampered_data}")
        print(f"\nOriginal Hash:  {original_hash}")
        print(f"Tampered Hash: {tampered_hash}")
        
        # Verify original
        original_verification = self.blockchain.verify_data_hash(original_hash)
        
        # Try to verify tampered
        tampered_verification = self.blockchain.verify_data_hash(tampered_hash)
        
        result = {
            'original_exists': original_verification['exists'],
            'tampered_exists': tampered_verification['exists'],
            'hashes_match': original_hash == tampered_hash,
            'tampering_detected': original_hash != tampered_hash
        }
        
        print("\n" + "-" * 70)
        if result['tampering_detected']:
            print("⚠️  TAMPERING DETECTED!")
            print("The data has been modified and does not match blockchain record.")
            print(f"Original hash exists on blockchain: {result['original_exists']}")
            print(f"Tampered hash exists on blockchain: {result['tampered_exists']}")
        else:
            print("✓ Data integrity verified - no tampering detected")
        print("-" * 70)
        
        return result
    
    def save_results(self, results: List[Dict], filename: str = None):
        """Save processing results to JSON"""
        if filename is None:
            filename = config.RESULTS_DIR / "blockchain_registration_results.json"
        else:
            filename = config.RESULTS_DIR / filename
        
        # Ensure results directory exists
        config.RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n✓ Results saved to: {filename}")
    
    def generate_audit_report(self) -> Dict:
        """Generate system audit report"""
        total_blockchain_records = self.blockchain.get_total_records()
        
        successful = sum(
            1 for r in self.hash_registry 
            if r['blockchain_result'].get('success', False)
        )
        
        failed = len(self.hash_registry) - successful
        
        report = {
            'report_timestamp': datetime.now().isoformat(),
            'total_processed_records': len(self.hash_registry),
            'total_blockchain_records': total_blockchain_records,
            'successful_registrations': successful,
            'failed_registrations': failed,
            'success_rate': f"{(successful/len(self.hash_registry)*100):.2f}%" if self.hash_registry else "0%",
            'system_status': 'OPERATIONAL',
            'blockchain_network': config.GANACHE_URL,
            'contract_address': self.blockchain.contract_address
        }
        
        return report

# Main execution
if __name__ == "__main__":
    try:
        # Initialize system
        system = IoTSecuritySystem()
        
        # Load processed IoT data
        print(f"\nLoading data from: {config.SAMPLE_DATA_FILE}")
        
        if not config.SAMPLE_DATA_FILE.exists():
            print(f"✗ Sample data not found. Please run data_preprocessing.py first!")
            sys.exit(1)
        
        iot_data = pd.read_csv(config.SAMPLE_DATA_FILE)
        print(f"✓ Loaded {len(iot_data)} records")
        
        # Process data (limit to 20 for testing)
        results = system.process_iot_data(
            iot_data.head(20), 
            batch_size=5
        )
        
        # Save results
        system.save_results(results)
        
        # Generate audit report
        audit_report = system.generate_audit_report()
        print("\n" + "=" * 70)
        print("AUDIT REPORT")
        print("=" * 70)
        print(json.dumps(audit_report, indent=2))
        print("=" * 70)
        
        # Demonstrate tampering detection
        if len(results) > 0:
            print("\n" + "=" * 70)
            print("DEMONSTRATING TAMPER DETECTION")
            print("=" * 70)
            
            # Get first record's original data
            first_record = results[0]
            original_data = {
                k: v for k, v in first_record['original_data'].items()
            }
            
            # Create tampered version
            tampered_data = original_data.copy()
            
            # Simulate tampering - modify a value
            for key in tampered_data.keys():
                if isinstance(tampered_data[key], (int, float)) or key == 'temperature':
                    try:
                        tampered_data[key] = str(float(tampered_data[key]) + 10)
                        break
                    except:
                        continue
            
            # Detect tampering
            system.simulate_tampering_detection(original_data, tampered_data)
        
        print("\n" + "=" * 70)
        print("✅ SYSTEM EXECUTION COMPLETE!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ System error: {str(e)}")
        import traceback
        traceback.print_exc()
