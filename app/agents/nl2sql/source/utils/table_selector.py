import os
import logging
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.docstore.document import Document
from .schema_inference import infer_schema  # Adjust import if needed

logging.basicConfig(level=logging.DEBUG)

class TableSelector:
    def __init__(self, schema_sql_path: str, vector_store_path: str = "rag/table_store.faiss"):
        self.schema_sql_path = schema_sql_path
        self.vector_store_path = vector_store_path
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        self.embeddings = OpenAIEmbeddings(openai_api_key=api_key)
        self.vector_store = self.initialize_vector_store()

    def initialize_vector_store(self):
        try:
            if os.path.exists(self.vector_store_path):
                # If the FAISS file already exists, load it.
                # Only do this if you trust your pickle file source!
                vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                logging.info("FAISS table index loaded.")
            else:
                # If no FAISS file, create a new index from your schema.
                schema = self.parse_schema()
                if not schema:
                    raise ValueError("Schema is empty. Check your schema file and inference logic.")
                
                documents = [Document(page_content=table_name) for table_name in schema.keys()]
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
            logging.debug("SQL SCHEMA:")
            logging.debug(schema_sql)
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

if __name__ == "__main__":
    # Update this path to the location of your schema.sql file.
    
    schema_path = "path/to/schema.sql"
    try:
        selector = TableSelector(schema_sql_path=schema_path)
        # Example usage
        tables = selector.select_relevant_tables("example query", top_n=3)
        print("Selected tables:", tables)
    except Exception as e:
        logging.error("Error in main execution: %s", e)
