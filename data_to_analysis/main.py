import argparse
import os
from hypothesis_processor import process_hypothesis
from data_processor import process_data
from email_generator import generate_email

def parse_arguments():
    parser = argparse.ArgumentParser(description='Generate analytical email based on CSV data and hypothesis.')
    parser.add_argument('csv_path', type=str, help='Path to the CSV data file.')
    parser.add_argument('hypothesis_path', type=str, help='Path to the hypothesis Markdown file.')
    return parser.parse_args()

def create_output_directories(csv_path):
    base_name = os.path.splitext(os.path.basename(csv_path))[0]
    output_dir = os.path.join('data_to_analysis', 'output_data', base_name)
    aggregated_dir = os.path.join('data_to_analysis', 'aggregated_data', base_name)
    processed_hypothesis_dir = os.path.join('data_to_analysis', 'processed_hypothesis', base_name)
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(aggregated_dir, exist_ok=True)
    os.makedirs(processed_hypothesis_dir, exist_ok=True)
    
    return output_dir, aggregated_dir, processed_hypothesis_dir

def main():
    args = parse_arguments()
    output_dir, aggregated_dir, processed_hypothesis_dir = create_output_directories(args.csv_path)
    
    processed_hypothesis = process_hypothesis(args.hypothesis_path, processed_hypothesis_dir)
    processed_data = process_data(args.csv_path, processed_hypothesis, aggregated_dir)
    generate_email(processed_data, processed_hypothesis, output_dir)

if __name__ == '__main__':
    main()
