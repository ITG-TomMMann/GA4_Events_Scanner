import pytest
from source.rag.retrieval import retrieve_examples
from unittest.mock import patch

@patch('source.rag.retrieval.OpenAIEmbeddings')
@patch('source.rag.retrieval.FAISS')
def test_retrieve_examples(mock_faiss, mock_embeddings):
    mock_embeddings_instance = mock_embeddings.return_value
    mock_embeddings_instance.embed_query.return_value = [0.1, 0.2, 0.3]
    
    mock_vector_store = mock_faiss.load_local.return_value
    mock_vector_store.similarity_search_by_vector.return_value = [
        type('Doc', (object,), {'page_content': 'SELECT * FROM users;'})
    ]
    
    examples = retrieve_examples("Get all users")
    assert len(examples) == 1
    assert examples[0] == "SELECT * FROM users;"
