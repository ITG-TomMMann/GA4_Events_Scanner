import pydata_google_auth
from google.cloud import bigquery

# Define the scopes required for BigQuery
SCOPES = [
    'https://www.googleapis.com/auth/cloud-platform',
    'https://www.googleapis.com/auth/bigquery',
]

# Authenticate and obtain user credentials
credentials = pydata_google_auth.get_user_credentials(SCOPES)

# Initialize the BigQuery client with the obtained credentials
client = bigquery.Client(credentials=credentials, project="jlr-dl-dxa")

# Define the SQL query
query = """
    SELECT * 
    FROM `jlr-dl-dxa.PRD_GA4.GA4_lookup_market`
"""

# Execute the query
query_job = client.query(query)

# Fetch and print the results
try:
    results = query_job.result()  # Wait for the query to complete
    for row in results:
        print(dict(row))  # Convert each row to a dictionary and print
except Exception as e:
    print(f"Error executing query: {e}")
