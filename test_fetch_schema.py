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

# Define the fully-qualified table ID
table_id = "jlr-dl-dxa.PRD_GA4.GA4_lookup_market"

try:
    # Retrieve the table metadata
    table = client.get_table(table_id)

    # Print the schema details
    print("Schema for table", table_id)
    for field in table.schema:
        print(f"Name: {field.name}, Type: {field.field_type}, Mode: {field.mode}")
except Exception as e:
    print(f"Error retrieving schema: {e}")
