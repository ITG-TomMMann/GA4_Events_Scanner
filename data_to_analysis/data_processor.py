from langsmith_tracing import trace_api_call
import pandas as pd
import os

def process_data(csv_path, processed_hypothesis_path, output_dir):
    # Read the CSV data
    data = pd.read_csv(csv_path)
    
    # Implement transformation based on processed hypothesis
    # Example transformations:
    data['enquiry_rate'] = data['enquiries'] / data['total_visitors']
    data['config_completion_rate'] = data['config_completions'] / data['total_visitors']
    
    # Aggregate data as needed
    aggregated_data = data.groupby('config_type').agg({
        'enquiry_rate': 'mean',
        'config_completion_rate': 'mean'
    }).reset_index()
    
    # Save processed data
    processed_data_path = os.path.join(output_dir, 'processed_data.csv')
    aggregated_data.to_csv(processed_data_path, index=False)
    
    trace_api_call('process_data', {'csv_path': csv_path, 'processed_hypothesis_path': processed_hypothesis_path, 'output_dir': output_dir}, processed_data_path)
    
    return processed_data_path
