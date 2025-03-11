import logging
import os
import tempfile
import sys
import subprocess
import importlib.util

# Check and install required packages

# Now import required packages
import pydata_google_auth
from google.cloud import bigquery
import pandas as pd

class BigQueryService:
    """Service to interact with Google BigQuery for data analysis."""
    
    def __init__(self, project_id="jlr-dl-dxa"):
        """
        Initialize BigQuery service.
        
        Args:
            project_id (str): The Google Cloud project ID.
        """
        self.project_id = project_id
        self.client = None
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize the client
        self._init_client()
    
    def _init_client(self):
        """Initialize the BigQuery client with appropriate credentials."""
        try:
            # Define the scopes required for BigQuery
            scopes = [
                'https://www.googleapis.com/auth/cloud-platform',
                'https://www.googleapis.com/auth/bigquery',
            ]
            
            # Get application default credentials or user credentials
            credentials = None
            
            # Try application default credentials first
            try:
                from google.auth import default
                credentials, _ = default(scopes=scopes)
                self.logger.info("Using application default credentials")
            except Exception as e:
                self.logger.info(f"Application default credentials not found: {e}")
                
            # Fall back to user credentials
            if credentials is None:
                credentials = pydata_google_auth.get_user_credentials(scopes)
                self.logger.info("Using user credentials")
            
            # Initialize the client
            self.client = bigquery.Client(credentials=credentials, project=self.project_id)
            self.logger.info(f"BigQuery client initialized for project: {self.project_id}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize BigQuery client: {e}")
            raise
    
    def estimate_query_cost(self, query):
        """
        Estimate the cost of running a BigQuery SQL query without executing it.
        
        Args:
            query (str): The SQL query to estimate.
            
        Returns:
            dict: Cost estimation information including bytes processed and approximate cost.
        """
        if not self.client:
            raise ValueError("BigQuery client not initialized")
        
        try:
            self.logger.info(f"Estimating cost for query: {query}")
            
            # Configure job for dry run (cost estimation)
            job_config = bigquery.QueryJobConfig(dry_run=True)
            
            # Start the query job without executing it
            query_job = self.client.query(query, job_config=job_config)
            
            # Get bytes that would be processed
            bytes_processed = query_job.total_bytes_processed
            
            # Calculate approximate cost (as of March 2025)
            # BigQuery pricing: $5 per TB (1 TB = 1,099,511,627,776 bytes)
            tb_processed = bytes_processed / 1099511627776
            estimated_cost_usd = tb_processed * 5.0
            
            result = {
                "bytes_processed": bytes_processed,
                "terabytes_processed": tb_processed,
                "estimated_cost_usd": estimated_cost_usd,
                "estimated_cost_formatted": f"${estimated_cost_usd:.6f}"
            }
            
            self.logger.info(f"Cost estimation: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error estimating query cost: {e}")
            raise
            
    def execute_query(self, query, max_results=None):
        """
        Execute a BigQuery SQL query.
        
        Args:
            query (str): The SQL query to execute.
            max_results (int, optional): Maximum number of results to return.
            
        Returns:
            DataFrame: Results as a pandas DataFrame.
        """
        if not self.client:
            raise ValueError("BigQuery client not initialized")
        
        try:
            self.logger.info(f"Executing query: {query}")
            
            # Configure query job
            job_config = bigquery.QueryJobConfig()
            if max_results:
                job_config.maximum_results = max_results
            
            # Execute the query
            query_job = self.client.query(query, job_config=job_config)
            
            # Wait for the query to complete
            results = query_job.result()
            
            # Convert to DataFrame
            df = results.to_dataframe()
            
            self.logger.info(f"Query executed successfully. Returned {len(df)} rows.")
            return df
            
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            raise
    
    def save_to_csv(self, df, filename=None):
        """
        Save DataFrame to CSV file.
        
        Args:
            df (DataFrame): Pandas DataFrame to save.
            filename (str, optional): Output filename. If None, creates a temporary file.
            
        Returns:
            str: Path to the saved CSV file.
        """
        try:
            if filename is None:
                # Create a temporary file
                fd, path = tempfile.mkstemp(suffix='.csv')
                os.close(fd)
                filename = path
            
            # Save DataFrame to CSV
            df.to_csv(filename, index=False)
            self.logger.info(f"DataFrame saved to {filename}")
            
            return filename
            
        except Exception as e:
            self.logger.error(f"Error saving DataFrame to CSV: {e}")
            raise
    
    def get_table_schema(self, table_id):
        """
        Get schema for a specific table.
        
        Args:
            table_id (str): Table ID in format 'dataset.table_name'.
            
        Returns:
            dict: Table schema information.
        """
        try:
            table_ref = self.client.get_table(f"{self.project_id}.{table_id}")
            
            schema = {
                "fields": [
                    {
                        "name": field.name,
                        "type": field.field_type,
                        "description": field.description
                    }
                    for field in table_ref.schema
                ],
                "num_rows": table_ref.num_rows,
                "created": table_ref.created.isoformat()
            }
            
            return schema
            
        except Exception as e:
            self.logger.error(f"Error getting schema for table {table_id}: {e}")
            raise
            
    def list_datasets(self):
        """
        List all datasets in the project.
        
        Returns:
            list: List of dataset IDs.
        """
        try:
            datasets = list(self.client.list_datasets())
            return [dataset.dataset_id for dataset in datasets]
        except Exception as e:
            self.logger.error(f"Error listing datasets: {e}")
            raise
            
    def list_tables(self, dataset_id):
        """
        List all tables in a dataset.
        
        Args:
            dataset_id (str): Dataset ID.
            
        Returns:
            list: List of table IDs.
        """
        try:
            tables = list(self.client.list_tables(dataset_id))
            return [table.table_id for table in tables]
        except Exception as e:
            self.logger.error(f"Error listing tables in dataset {dataset_id}: {e}")
            raise

# Create a default BigQuery service instance
bq_service = BigQueryService()