import pytest
from src.query_agent import generate_sql
from unittest.mock import patch

@patch('src.query_agent.openai.ChatCompletion.create')
def test_generate_sql(mock_openai):
    mock_openai.return_value = {
        'choices': [{'message': {'content': 'SELECT * FROM users;'}}]
    }
    sql = generate_sql("Get all users", {"users": {"columns": ["id", "name"]}}, [])
    assert sql == 'SELECT * FROM users;'
