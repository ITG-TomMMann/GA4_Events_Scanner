import argparse
import yaml
import logging
from schema_agent import get_schema
from rag.retrieval import retrieve_examples
from query_agent import generate_sql
from utils.logger import setup_logger
import os 


def parse_arguments():
    parser = argparse.ArgumentParser(description="Text-to-SQL CLI")
    parser.add_argument('--query', type=str, help="Natural language query")
    parser.add_argument('--schema', type=str, help="Optional schema input")
    return parser.parse_args()


def load_config():
def load_config():
    source_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(source_dir, "..", "config", "config.yaml")
    config_path = os.path.normpath(config_path)

    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    setup_logger()
    args = parse_arguments()
    config = load_config()

    while True:
        nl_query = args.query if args.query else input("Enter your query (or 'exit' to quit): ")
        if nl_query.lower() == 'exit':
            break
        schema = get_schema(args.schema)
        examples = retrieve_examples(nl_query)
        sql = generate_sql(nl_query, schema, examples)
        print(f"Generated SQL:\n{sql}")
        args.query = None
        args.query = None

if __name__ == "__main__":
    main()
