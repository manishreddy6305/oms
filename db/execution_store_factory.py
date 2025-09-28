from db.execution_store import ExecutionStore
from db.mongo_execution_store import MongoConversationStore
from dotenv import load_dotenv
import os

load_dotenv()

def get_conversation_store() -> ExecutionStore:
    backend = os.getenv("CONV_STORE_BACKEND", "mongo").lower()
    if backend == "mongo":
        return MongoConversationStore()
    # Placeholder for future backends:
    # if backend == "dynamodb": return DynamoConversationStore(...)
    raise ValueError(f"Unsupported CONV_STORE_BACKEND={backend}")

