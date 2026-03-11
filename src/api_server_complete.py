# src/api_server.py
"""
REST API Server for IoT Blockchain Security System
Provides endpoints for data registration, verification, and system status
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.append(str(Path(__file__).parent))

from config import config
from iot_security_system import IoTSecuritySystem
from crypto_utils import CryptoHasher

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize security system (global instance)
print("Initializing IoT Security System...")
security_system = IoTSecuritySystem()
hasher = CryptoHasher()

print(" API Server Ready!")

# ============================================================================
# API ENDPOINTS
# ============================================================================

@app.route('/', methods=['GET'])
def home():
    """API home endpoint with documentation"""
    return jsonify({
        'service': 'IoT Blockchain Security System API',
        'version': '1.0.0',
        'author': 'Oyelade Paul Oluwafemi',
        'endpoints': {
            '/api/health': 'GET - System health check',
            '/api/register': 'POST - Register IoT data on blockchain',
            '/api/verify': 'POST - Verify data integrity',
            '/api/audit': 'GET - Get system audit report',
            '/api/records': 'GET - Get total blockchain records',
            '/api/stats': 'GET - Get system statistics',
            '/api/hash': 'POST - Generate hash for data'
        },
        'documentation': '/api/docs'
    })

@app.route('/api/docs', methods=['GET'])
def documentation():
    """API documentation"""
    docs = {
        'title': 'IoT Blockchain Security System API',
        'description': 'REST API for securing IoT data using blockchain technology',
        'endpoints': [
            {
                'path': '/api/health',
                'method': 'GET',
                'description': 'Check system health and blockchain connectivity',
                'response': {
                    'status': 'healthy',
                    'blockchain_connected': True,
                    'total_records': 20,
                    'contract_address': '0x...',
                    'account_balance': '999.5 ETH'
                }
            },
            {
                'path': '/api/register',
                'method': 'POST',
                'description': 'Register IoT sensor data on blockchain',
                'request_body': {
                    'device_id': 'DEVICE_001',
                    'sensor_data': {
                        'temperature': 25.5,
                        'humidity': 60.2,
                        'timestamp': 1234567890
                    }
                },
                'response': {
                    'success': True,
                    'data_hash': '0abc123...',
                    'tx_hash': '0x456def...',
                    'block_number': 123,
                    'message': 'Data registered successfully'
                }
            },
            {
                'path': '/api/verify',
                'method': 'POST',
                'description': 'Verify data integrity against blockchain',
                'request_body': {
                    'sensor_data': {
                        'temperature': 25.5,
                        'humidity': 60.2
                    }
                },
                'response': {
                    'integrity_verified': True,
                    'message': 'Data integrity confirmed',
                    'blockchain_record': {}
                }
            },
            {
                'path': '/api/hash',
                'method': 'POST',
                'description': 'Generate SHA-256 hash for data',
                'request_body': {
                    'data': {'key': 'value'}
                },
                'response': {
                    'hash': '0abc123...',
                    'algorithm': 'SHA-256'
                }
            }
        ]
    }
    return jsonify(docs)

@app.route('/api/health', methods=['GET'])
def health_check():
    """System health check endpoint"""
    try:
        # Get blockchain status
        total_records = security_system.blockchain.get_total_records()
        is_connected = security_system.blockchain.w3.is_connected()
        
        # Get account balance
        balance = security_system.blockchain.w3.eth.get_balance(
            security_system.blockchain.account
        )
        balance_eth = security_system.blockchain.w3.from_wei(balance, 'ether')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'blockchain_connected': is_connected,
            'total_records': total_records,
            'contract_address': security_system.blockchain.contract_address,
            'account_address': security_system.blockchain.account,
            'account_balance': f'{balance_eth} ETH',
            'network': config.GANACHE_URL
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@app.route('/api/register', methods=['POST'])
def register_data():
    """
    Register IoT data on blockchain
    
    Expected JSON:
    {
        "device_id": "DEVICE_001",
        "sensor_data": {
            "temperature": 25.5,
            "humidity": 60.2
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        device_id = data.get('device_id')
        sensor_data = data.get('sensor_data')
        
        if not device_id or not sensor_data:
            return jsonify({
                'success': False,
                'error': 'Missing device_id or sensor_data'
            }), 400
        
        # Generate hash
        data_hash = hasher.generate_sha256_hash(sensor_data)
        
        # Register on blockchain
        result = security_system.blockchain.register_data_hash(
            data_hash,
            device_id
        )
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'message': 'Data registered successfully on blockchain',
                'data_hash': data_hash,
                'tx_hash': result.get('tx_hash'),
                'block_number': result.get('block_number'),
                'gas_used': result.get('gas_used'),
                'device_id': device_id,
                'timestamp': datetime.now().isoformat()
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Registration failed'),
                'data_hash': data_hash
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/verify', methods=['POST'])
def verify_data():
    """
    Verify data integrity against blockchain
    
    Expected JSON:
    {
        "sensor_data": {
            "temperature": 25.5,
            "humidity": 60.2
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        sensor_data = data.get('sensor_data')
        
        if not sensor_data:
            return jsonify({
                'success': False,
                'error': 'Missing sensor_data'
            }), 400
        
        # Verify integrity
        result = security_system.verify_data_integrity(sensor_data)
        
        return jsonify({
            'success': True,
            'integrity_verified': result['integrity_verified'],
            'message': result['message'],
            'computed_hash': result['computed_hash'],
            'blockchain_record': result.get('blockchain_record', {}),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/hash', methods=['POST'])
def generate_hash():
    """
    Generate SHA-256 hash for data
    
    Expected JSON:
    {
        "data": {
            "key": "value"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'data' not in data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Generate hash
        data_hash = hasher.generate_sha256_hash(data['data'])
        
        return jsonify({
            'success': True,
            'hash': data_hash,
            'algorithm': 'SHA-256',
            'hash_length': len(data_hash),
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/audit', methods=['GET'])
def get_audit_report():
    """Get system audit report"""
    try:
        report = security_system.generate_audit_report()
        return jsonify({
            'success': True,
            'audit_report': report
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/records', methods=['GET'])
def get_total_records():
    """Get total blockchain records"""
    try:
        total = security_system.blockchain.get_total_records()
        return jsonify({
            'success': True,
            'total_records': total,
            'contract_address': security_system.blockchain.contract_address
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/stats', methods=['GET'])
def get_statistics():
    """Get system statistics"""
    try:
        total_records = security_system.blockchain.get_total_records()
        processed_records = len(security_system.hash_registry)
        
        balance = security_system.blockchain.w3.eth.get_balance(
            security_system.blockchain.account
        )
        balance_eth = security_system.blockchain.w3.from_wei(balance, 'ether')
        
        return jsonify({
            'success': True,
            'statistics': {
                'total_blockchain_records': total_records,
                'total_processed_records': processed_records,
                'account_balance': f'{balance_eth} ETH',
                'contract_address': security_system.blockchain.contract_address,
                'network_url': config.GANACHE_URL,
                'system_uptime': 'Active'
            },
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'Please check the API documentation at /api/docs'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': str(error)
    }), 500

# Main entry point
if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("IOT BLOCKCHAIN SECURITY API SERVER")
    print("=" * 70)
    print(f"Server starting on {config.API_HOST}:{config.API_PORT}")
    print(f"Blockchain: {config.GANACHE_URL}")
    print(f"Contract: {security_system.blockchain.contract_address}")
    print("\nAPI Endpoints:")
    print("  - http://localhost:5000/")
    print("  - http://localhost:5000/api/docs")
    print("  - http://localhost:5000/api/health")
    print("  - http://localhost:5000/api/register (POST)")
    print("  - http://localhost:5000/api/verify (POST)")
    print("=" * 70 + "\n")
    
    app.run(
        host=config.API_HOST,
        port=config.API_PORT,
        debug=True
    )
