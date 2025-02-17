from langchain.memory import ConversationBufferMemory
import logging

class MemoryManager:
    def __init__(self):
        self.memory = ConversationBufferMemory(memory_key="history")

    def get_memory(self, session_id: str):
        if hasattr(self.memory, session_id):
            return getattr(self.memory, session_id)
        else:
            memory_instance = ConversationBufferMemory(memory_key="history")
            setattr(self.memory, session_id, memory_instance)
            logging.info(f"Initialized memory for session {session_id}.")
            return memory_instance

    def clear_memory(self, session_id: str):
        if hasattr(self.memory, session_id):
            delattr(self.memory, session_id)
            logging.info(f"Cleared memory for session {session_id}.")
