"""
Data handler abstraction layer for local and cloud storage.
Supports local CSV files and future cloud storage (AWS S3, GCP, Azure).
"""

import os
import pandas as pd
from typing import Optional
import io

class DataHandler:
    """Abstract base class for data handling"""
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV file and return as DataFrame"""
        raise NotImplementedError
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Save DataFrame as CSV file"""
        raise NotImplementedError


class LocalDataHandler(DataHandler):
    """Handle data from local filesystem"""
    
    def __init__(self, data_dir: str = '/app/data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        print(f"LocalDataHandler initialized with data_dir: {self.data_dir}")
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV from local filesystem"""
        filepath = os.path.join(self.data_dir, filename)
        
        # Also check in root directory for backward compatibility
        if not os.path.exists(filepath) and os.path.exists(filename):
            filepath = filename
        
        try:
            print(f"Loading CSV from local: {filepath}")
            df = pd.read_csv(filepath)
            print(f"Successfully loaded {filename}: {len(df)} rows")
            return df
        except FileNotFoundError:
            print(f"ERROR: File not found: {filepath}")
            return pd.DataFrame()
        except Exception as e:
            print(f"ERROR loading {filename}: {str(e)}")
            return pd.DataFrame()
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Save DataFrame to local filesystem"""
        filepath = os.path.join(self.data_dir, filename)
        try:
            df.to_csv(filepath, index=False)
            print(f"Successfully saved {filename}")
            return True
        except Exception as e:
            print(f"ERROR saving {filename}: {str(e)}")
            return False


class S3DataHandler(DataHandler):
    """Handle data from AWS S3 (for future use)"""
    
    def __init__(self):
        try:
            import boto3
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
                region_name=os.getenv('AWS_REGION', 'us-east-1')
            )
            self.bucket = os.getenv('AWS_S3_BUCKET')
            print(f"S3DataHandler initialized with bucket: {self.bucket}")
        except ImportError:
            raise ImportError("boto3 is required for S3 support. Install with: pip install boto3")
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV from S3"""
        try:
            print(f"Loading CSV from S3: s3://{self.bucket}/{filename}")
            obj = self.s3_client.get_object(Bucket=self.bucket, Key=filename)
            df = pd.read_csv(io.BytesIO(obj['Body'].read()))
            print(f"Successfully loaded {filename} from S3: {len(df)} rows")
            return df
        except Exception as e:
            print(f"ERROR loading {filename} from S3: {str(e)}")
            return pd.DataFrame()
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Save DataFrame to S3"""
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            self.s3_client.put_object(
                Bucket=self.bucket,
                Key=filename,
                Body=csv_buffer.getvalue()
            )
            print(f"Successfully saved {filename} to S3")
            return True
        except Exception as e:
            print(f"ERROR saving {filename} to S3: {str(e)}")
            return False


class GCPDataHandler(DataHandler):
    """Handle data from Google Cloud Storage (for future use)"""
    
    def __init__(self):
        try:
            from google.cloud import storage
            self.client = storage.Client(project=os.getenv('GCP_PROJECT_ID'))
            self.bucket = self.client.bucket(os.getenv('GCP_BUCKET_NAME'))
            print(f"GCPDataHandler initialized with bucket: {os.getenv('GCP_BUCKET_NAME')}")
        except ImportError:
            raise ImportError("google-cloud-storage is required for GCP support. Install with: pip install google-cloud-storage")
    
    def load_csv(self, filename: str) -> pd.DataFrame:
        """Load CSV from GCS"""
        try:
            print(f"Loading CSV from GCS: gs://{self.bucket.name}/{filename}")
            blob = self.bucket.blob(filename)
            df = pd.read_csv(io.BytesIO(blob.download_as_bytes()))
            print(f"Successfully loaded {filename} from GCS: {len(df)} rows")
            return df
        except Exception as e:
            print(f"ERROR loading {filename} from GCS: {str(e)}")
            return pd.DataFrame()
    
    def save_csv(self, df: pd.DataFrame, filename: str) -> bool:
        """Save DataFrame to GCS"""
        try:
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            blob = self.bucket.blob(filename)
            blob.upload_from_string(csv_buffer.getvalue(), content_type='text/csv')
            print(f"Successfully saved {filename} to GCS")
            return True
        except Exception as e:
            print(f"ERROR saving {filename} to GCS: {str(e)}")
            return False


def get_data_handler() -> DataHandler:
    """Factory function to get appropriate data handler based on configuration"""
    data_source = os.getenv('DATA_SOURCE', 'local').lower()
    
    print(f"Initializing data handler with source: {data_source}")
    
    if data_source == 'local':
        return LocalDataHandler(data_dir=os.getenv('DATA_DIR', '/app/data'))
    elif data_source == 'aws' or data_source == 's3':
        return S3DataHandler()
    elif data_source == 'gcp':
        return GCPDataHandler()
    else:
        print(f"Unknown data source: {data_source}, defaulting to local")
        return LocalDataHandler()
