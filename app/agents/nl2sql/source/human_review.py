import logging
import json

def capture_feedback(sql_query: str, corrections: str) -> None:
    feedback = {
        "sql_query": sql_query,
        "corrections": corrections
    }
    os.makedirs('feedback', exist_ok=True)
    with open('feedback/log.json', 'a') as f:
        json.dump(feedback, f)
        f.write('\n')
    logging.info("Captured feedback for SQL query.")
