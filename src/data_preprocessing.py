# src/data_preprocessing.py
"""
IoT Data Preprocessing Module
Processes sensor data for blockchain registration
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

class IoTDataPreprocessor:
    """
    Preprocesses IoT sensor data for blockchain security system
    """
    
    def __init__(self):
        # Your actual dataset path
        self.dataset_path = r"C:\Users\HP\Downloads\Paul's Final Year Project Documents\Blockchain_dataset\sensor_data.csv"
        
        # Output paths
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.project_root, 'data')
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.df = None
        self.features_df = None
        self.original_shape = None
        
        print("=" * 70)
        print("IoT DATA PREPROCESSING MODULE")
        print("=" * 70)
        print(f"Dataset Path: {self.dataset_path}")
        print(f"Output Directory: {self.output_dir}")
    
    def load_data(self):
        """Load dataset from CSV"""
        print("\n[Step 1/7] Loading IoT dataset...")
        
        try:
            self.df = pd.read_csv(self.dataset_path)
            self.original_shape = self.df.shape
            
            print(f"  ✓ Dataset loaded successfully")
            print(f"  ✓ Shape: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            print(f"\n  Columns found:")
            for idx, col in enumerate(self.df.columns, 1):
                print(f"    {idx}. {col}")
            
            # Display first few rows
            print(f"\n  First 3 rows preview:")
            print(self.df.head(3).to_string())
            
            return self.df
            
        except FileNotFoundError:
            print(f"  ✗ ERROR: File not found at {self.dataset_path}")
            sys.exit(1)
        except Exception as e:
            print(f"  ✗ ERROR loading data: {str(e)}")
            sys.exit(1)
    
    def analyze_data(self):
        """Analyze dataset structure and content"""
        print("\n[Step 2/7] Analyzing data...")
        
        # Data info
        print(f"\n  Data Types:")
        print(self.df.dtypes.to_string())
        
        # Missing values
        missing = self.df.isnull().sum()
        if missing.sum() > 0:
            print(f"\n  Missing Values:")
            print(missing[missing > 0].to_string())
        else:
            print(f"\n  ✓ No missing values found")
        
        # Numeric statistics
        print(f"\n  Numeric Statistics:")
        print(self.df.describe().to_string())
    
    def handle_missing_values(self):
        """Handle missing data"""
        print("\n[Step 3/7] Handling missing values...")
        
        missing_count = self.df.isnull().sum().sum()
        
        if missing_count > 0:
            print(f"  Found {missing_count} missing values")
            
            # Strategy 1: Forward fill for time-series
            self.df.fillna(method='ffill', inplace=True)
            
            # Strategy 2: Backward fill for remaining
            self.df.fillna(method='bfill', inplace=True)
            
            # Strategy 3: Drop rows if still have missing
            self.df.dropna(inplace=True)
            
            print(f"  ✓ Missing values handled")
            print(f"  ✓ New shape: {self.df.shape}")
        else:
            print(f"  ✓ No missing values to handle")
    
    def normalize_timestamps(self):
        """Ensure consistent timestamp format"""
        print("\n[Step 4/7] Normalizing timestamps...")
        
        # Check if timestamp column exists
        timestamp_cols = [col for col in self.df.columns if 'time' in col.lower() or 'date' in col.lower()]
        
        if timestamp_cols:
            timestamp_col = timestamp_cols[0]
            print(f"  Found timestamp column: '{timestamp_col}'")
            
            try:
                self.df['timestamp'] = pd.to_datetime(self.df[timestamp_col])
                self.df['timestamp_unix'] = self.df['timestamp'].astype(np.int64) // 10**9
                print(f"  ✓ Timestamps normalized")
            except Exception as e:
                print(f"  Warning: Could not parse timestamps: {str(e)}")
                self.create_synthetic_timestamps()
        else:
            print(f"  No timestamp column found, creating synthetic timestamps...")
            self.create_synthetic_timestamps()
    
    def create_synthetic_timestamps(self):
        """Create synthetic timestamps if not present"""
        start_date = datetime(2024, 1, 1)
        self.df['timestamp'] = pd.date_range(
            start=start_date,
            periods=len(self.df),
            freq='1min'
        )
        self.df['timestamp_unix'] = self.df['timestamp'].astype(np.int64) // 10**9
        print(f"  ✓ Synthetic timestamps created")
    
    def add_device_identifiers(self):
        """Add device identifiers if not present"""
        print("\n[Step 5/7] Adding device identifiers...")
        
        # Check if device ID column exists
        device_cols = [col for col in self.df.columns if 'device' in col.lower() or 'id' in col.lower()]
        
        if device_cols and 'device_id' not in self.df.columns:
            # Rename existing column
            self.df['device_id'] = self.df[device_cols[0]]
            print(f"  ✓ Using existing column: '{device_cols[0]}'")
        elif 'device_id' in self.df.columns:
            print(f"  ✓ Device ID column already exists")
        else:
            # Create device IDs
            num_devices = min(10, max(1, len(self.df) // 100))  # 1-10 devices
            device_ids = [f"DEVICE_{i:03d}" for i in range(num_devices)]
            self.df['device_id'] = np.random.choice(device_ids, size=len(self.df))
            print(f"  ✓ Created {num_devices} device IDs")
    
    def extract_features(self):
        """Extract key features for blockchain registration"""
        print("\n[Step 6/7] Extracting features...")
        
        feature_columns = []
        
        # Always include device_id and timestamp
        if 'device_id' in self.df.columns:
            feature_columns.append('device_id')
        if 'timestamp_unix' in self.df.columns:
            feature_columns.append('timestamp_unix')
        
        # Include all numeric columns (sensor readings)
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Remove timestamp_unix if already added
        numeric_cols = [col for col in numeric_cols if col != 'timestamp_unix']
        
        feature_columns.extend(numeric_cols)
        
        # Remove duplicates while preserving order
        feature_columns = list(dict.fromkeys(feature_columns))
        
        self.features_df = self.df[feature_columns].copy()
        
        print(f"  ✓ Features extracted: {len(feature_columns)} columns")
        print(f"  Features: {', '.join(feature_columns)}")
        
        return self.features_df
    
    def save_processed_data(self):
        """Save preprocessed data"""
        print("\n[Step 7/7] Saving processed data...")
        
        # Save full processed dataset
        full_output_path = os.path.join(self.output_dir, 'processed_iot_data.csv')
        self.df.to_csv(full_output_path, index=False)
        print(f"  ✓ Full dataset saved: {full_output_path}")
        
        # Save feature dataset
        features_output_path = os.path.join(self.output_dir, 'iot_features.csv')
        self.features_df.to_csv(features_output_path, index=False)
        print(f"  ✓ Features saved: {features_output_path}")
        
        # Save sample for testing (first 100 records)
        sample_output_path = os.path.join(self.output_dir, 'sample_iot_data.csv')
        self.features_df.head(100).to_csv(sample_output_path, index=False)
        print(f"  ✓ Sample data saved: {sample_output_path}")
        
        # Generate summary statistics
        summary = {
            'original_shape': self.original_shape,
            'processed_shape': self.df.shape,
            'num_features': len(self.features_df.columns),
            'feature_columns': list(self.features_df.columns),
            'num_devices': self.df['device_id'].nunique() if 'device_id' in self.df.columns else 0,
            'time_range': {
                'start': str(self.df['timestamp'].min()) if 'timestamp' in self.df.columns else None,
                'end': str(self.df['timestamp'].max()) if 'timestamp' in self.df.columns else None
            }
        }
        
        # Save summary
        import json
        summary_path = os.path.join(self.output_dir, 'preprocessing_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        print(f"  ✓ Summary saved: {summary_path}")
    
    def preprocess_pipeline(self):
        """Complete preprocessing pipeline"""
        print("\nStarting preprocessing pipeline...\n")
        
        try:
            self.load_data()
            self.analyze_data()
            self.handle_missing_values()
            self.normalize_timestamps()
            self.add_device_identifiers()
            self.extract_features()
            self.save_processed_data()
            
            print("\n" + "=" * 70)
            print("PREPROCESSING COMPLETE!")
            print("=" * 70)
            print(f"\nSummary:")
            print(f"  Original records: {self.original_shape[0]}")
            print(f"  Processed records: {len(self.df)}")
            print(f"  Features extracted: {len(self.features_df.columns)}")
            print(f"  Output directory: {self.output_dir}")
            print("\nFiles created:")
            print(f"  1. processed_iot_data.csv (full dataset)")
            print(f"  2. iot_features.csv (features only)")
            print(f"  3. sample_iot_data.csv (first 100 records)")
            print(f"  4. preprocessing_summary.json (metadata)")
            print("\n✅ Data is ready for blockchain registration!")
            print("=" * 70 + "\n")
            
            return self.df, self.features_df
            
        except Exception as e:
            print(f"\n✗ Preprocessing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

# Main execution
if __name__ == "__main__":
    preprocessor = IoTDataPreprocessor()
    processed_df, features_df = preprocessor.preprocess_pipeline()
