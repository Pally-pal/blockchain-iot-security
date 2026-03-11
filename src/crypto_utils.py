# src/crypto_utils.py
"""
Cryptographic hashing utilities for IoT data
Uses SHA-256 for data integrity verification
"""

import hashlib
import json
from typing import Dict, Any, Union

class CryptoHasher:
    """
    Cryptographic hashing utility for IoT data integrity
    """
    
    @staticmethod
    def generate_sha256_hash(data: Union[Dict, str, bytes]) -> str:
        """
        Generate SHA-256 hash of data
        
        Args:
            data: Data to hash (can be dict, string, or bytes)
            
        Returns:
            Hexadecimal hash string (64 characters)
        
        Example:
            >>> hasher = CryptoHasher()
            >>> data = {'device_id': 'DEVICE_001', 'temp': 25.5}
            >>> hash_value = hasher.generate_sha256_hash(data)
            >>> len(hash_value)
            64
        """
        if isinstance(data, dict):
            # Convert dict to sorted JSON string for consistency
            data_string = json.dumps(data, sort_keys=True)
        elif isinstance(data, str):
            data_string = data
        elif isinstance(data, bytes):
            return hashlib.sha256(data).hexdigest()
        else:
            # Convert any other type to string
            data_string = str(data)
        
        # Encode and hash
        data_bytes = data_string.encode('utf-8')
        hash_object = hashlib.sha256(data_bytes)
        
        return hash_object.hexdigest()
    
    @staticmethod
    def hash_dataframe_row(row_dict: Dict) -> str:
        """
        Hash a single row from DataFrame
        
        Args:
            row_dict: Dictionary representation of DataFrame row
            
        Returns:
            SHA-256 hash string
        
        Example:
            >>> row = {'device_id': 'DEVICE_001', 'timestamp': 1234567890, 'temp': 25.5}
            >>> hash_value = CryptoHasher.hash_dataframe_row(row)
        """
        # Remove any non-essential fields
        essential_fields = {
            k: v for k, v in row_dict.items() 
            if not k.startswith('_') and k not in ['index', 'Unnamed: 0']
        }
        
        # Convert numpy/pandas types to native Python types
        cleaned_fields = {}
        for key, value in essential_fields.items():
            # Handle NaN, None, and numpy types
            if value is None or (hasattr(value, '__iter__') and len(str(value)) == 0):
                cleaned_fields[key] = None
            elif hasattr(value, 'item'):  # numpy types
                cleaned_fields[key] = value.item()
            else:
                cleaned_fields[key] = value
        
        return CryptoHasher.generate_sha256_hash(cleaned_fields)
    
    @staticmethod
    def verify_hash(original_data: Any, provided_hash: str) -> bool:
        """
        Verify if provided hash matches data
        
        Args:
            original_data: Original data
            provided_hash: Hash to verify against
            
        Returns:
            True if hashes match, False otherwise
        
        Example:
            >>> data = {'value': 42}
            >>> hash1 = CryptoHasher.generate_sha256_hash(data)
            >>> CryptoHasher.verify_hash(data, hash1)
            True
        """
        computed_hash = CryptoHasher.generate_sha256_hash(original_data)
        return computed_hash.lower() == provided_hash.lower()
    
    @staticmethod
    def hash_multiple(data_list: list) -> Dict[int, str]:
        """
        Hash multiple data items
        
        Args:
            data_list: List of data items to hash
            
        Returns:
            Dictionary mapping index to hash
        """
        return {
            idx: CryptoHasher.generate_sha256_hash(data)
            for idx, data in enumerate(data_list)
        }

# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("CRYPTOGRAPHIC HASHING TEST")
    print("=" * 70)
    
    hasher = CryptoHasher()
    
    # Test 1: Hash dictionary data
    sensor_data = {
        'device_id': 'DEVICE_001',
        'timestamp': 1640000000,
        'temperature': 25.5,
        'humidity': 60.2
    }
    
    print("\n[Test 1] Hash Dictionary:")
    print(f"Data: {sensor_data}")
    data_hash = hasher.generate_sha256_hash(sensor_data)
    print(f"Hash: {data_hash}")
    print(f"Hash Length: {len(data_hash)} characters")
    
    # Test 2: Verify hash
    print("\n[Test 2] Verify Hash:")
    is_valid = hasher.verify_hash(sensor_data, data_hash)
    print(f"Hash Valid: {is_valid}")
    
    # Test 3: Detect tampering
    print("\n[Test 3] Detect Tampering:")
    tampered_data = sensor_data.copy()
    tampered_data['temperature'] = 30.0  # Changed value
    tampered_hash = hasher.generate_sha256_hash(tampered_data)
    print(f"Original Hash:  {data_hash}")
    print(f"Tampered Hash: {tampered_hash}")
    print(f"Hashes Match: {data_hash == tampered_hash}")
    print(f"Tampering Detected: {data_hash != tampered_hash}")
    
    # Test 4: Hash consistency
    print("\n[Test 4] Hash Consistency:")
    hash1 = hasher.generate_sha256_hash(sensor_data)
    hash2 = hasher.generate_sha256_hash(sensor_data)
    print(f"Hash 1: {hash1}")
    print(f"Hash 2: {hash2}")
    print(f"Consistent: {hash1 == hash2}")
    
    print("\n" + "=" * 70)
    print("✅ All cryptographic tests completed!")
    print("=" * 70)
