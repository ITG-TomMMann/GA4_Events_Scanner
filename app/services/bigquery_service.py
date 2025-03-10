import pydata_google_auth
from google.cloud import bigquery
import pandas as pd
import logging
import os
import tempfile

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

# Example usage
if __name__ == "__main__":
    bq_service = BigQueryService()
    
    # Example query
    query = """
        SELECT * 
        FROM `jlr-dl-dxa.PRD_GA4.GA4_lookup_market`
        LIMIT 10
    """
    
    try:
        # Execute query
        results = bq_service.execute_query(query)
        
        # Print results
        print(f"Query returned {len(results)} rows.")
        print(results.head())
        
        # Save to CSV
        csv_path = bq_service.save_to_csv(results)
        print(f"Results saved to {csv_path}")
        
    except Exception as e:
        print(f"Error: {e}")