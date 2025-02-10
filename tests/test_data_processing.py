import unittest
from data_processor import process_data
import pandas as pd
import os

class TestDataProcessing(unittest.TestCase):
    def setUp(self):
        # Setup mock CSV and hypothesis
        self.csv_path = 'tests/mock_data.csv'
        self.hypothesis_path = 'tests/mock_hypothesis.md'
        self.output_dir = 'tests/output'
        os.makedirs(self.output_dir, exist_ok=True)
    
    def test_process_data(self):
        processed_data = process_data(self.csv_path, self.hypothesis_path, self.output_dir)
        self.assertTrue(os.path.exists(processed_data))
        df = pd.read_csv(processed_data)
        self.assertIn('enquiry_rate', df.columns)
        self.assertIn('config_completion_rate', df.columns)

if __name__ == '__main__':
    unittest.main()
