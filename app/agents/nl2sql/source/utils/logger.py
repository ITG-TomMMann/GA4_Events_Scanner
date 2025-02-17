import logging

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("nl2sql.log"),
            logging.StreamHandler()
        ]
    )
    # Set higher verbosity for debugging if needed
    # logging.getLogger().setLevel(logging.DEBUG)
