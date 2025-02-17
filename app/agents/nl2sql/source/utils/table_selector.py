from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import json
import os
import logging

class TableSelector:
    def __init__(self, schema_sql_path: str, vector_store_path: str = "rag/table_store.faiss"):
        self.schema_sql_path = schema_sql_path
        self.vector_store_path = vector_store_path
        self.embeddings = OpenAIEmbeddings(openai_api_key=os.getenv("OPENAI_API_KEY"))
        self.vector_store = self.initialize_vector_store()

    def initialize_vector_store(self):
        try:
            if os.path.exists(self.vector_store_path):
                vector_store = FAISS.load_local(self.vector_store_path, self.embeddings)
                logging.info("FAISS table index loaded.")
            else:
                schema = self.parse_schema()
                documents = [{"page_content": table} for table in schema.keys()]
                vector_store = FAISS.from_documents(documents, self.embeddings)
                vector_store.save_local(self.vector_store_path)
                logging.info("FAISS table index created and saved.")
            return vector_store
        except Exception as e:
            logging.error(f"Error initializing table vector store: {e}")
            raise

    def parse_schema(self):
        with open(self.schema_sql_path, 'r') as f:
            schema_sql = f.read()
        from utils.schema_inference import infer_schema
        schema = infer_schema(schema_sql)
        return schema

    def select_relevant_tables(self, query: str, top_n: int = 3) -> list:
        try:
            query_embedding = self.embeddings.embed_query(query)
            docs = self.vector_store.similarity_search_by_vector(query_embedding, k=top_n)
            selected_tables = [doc.page_content for doc in docs]
            logging.info(f"Selected tables: {selected_tables}")
            return selected_tables
        except Exception as e:
            logging.error(f"Error selecting tables: {e}")
            raise
