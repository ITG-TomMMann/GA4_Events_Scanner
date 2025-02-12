import pytest
from src.rag.retrieval import retrieve_examples
from unittest.mock import patch

@patch('src.rag.retrieval.compute_embedding')
@patch('src.rag.vector_store.VectorStore')
@patch('builtins.open')
def test_retrieve_examples(mock_open, mock_vector_store, mock_compute_emb):
    mock_compute_emb.return_value = [0.1, 0.2, 0.3]
    mock_vector_store_instance = mock_vector_store.return_value
    mock_vector_store_instance.index.search.return_value = ([], [0])
    mock_open.return_value.__enter__.return_value.read.return_value = '[{"nl_query": "Get all users", "sql": "SELECT * FROM users;"}]'
    
    examples = retrieve_examples("Get all users")
    assert len(examples) == 1
    assert examples[0]['sql'] == "SELECT * FROM users;"
