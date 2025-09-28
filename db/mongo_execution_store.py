from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.errors import PyMongoError, DuplicateKeyError
from db.execution_store import ExecutionStore
from typing import List, Dict, Optional, Any
from datetime import datetime
from objects.execution import Execution
import os

class MongoConversationStore(ExecutionStore):
    """
    Env vars:
      MONGO_URI (e.g. mongodb://localhost:27017)
      MONGO_DB  (e.g. orchestrator)
      MONGO_COLLECTION (optional, default: conversations)
    """

    def __init__(
        self,
        uri: Optional[str] = None,
        db_name: Optional[str] = None,
        collection_name: Optional[str] = None,
        client_kwargs: Optional[Dict[str, Any]] = None,
    ):
        uri = uri or os.getenv("MONGO_URI", "mongodb://host.docker.internal:27017")
        db_name = db_name or os.getenv("MONGO_DB", "god_level_knowledge")
        collection_name = collection_name or os.getenv("MONGO_COLLECTION", "executions")
        client_kwargs = client_kwargs or {}

        self._client = MongoClient(uri, **client_kwargs)
        self._db = self._client[db_name]
        self._col: Collection = self._db[collection_name]

        # Ensure fast lookup & uniqueness per key
        self._col.create_index("key", unique=True)

    def save(self, execution: Execution) -> None:
        """
        Insert if not exists; full replace (overwrite) if exists.
        """

        execution.updated_at = datetime.utcnow()

        try:
            # Try fast insert (will raise DuplicateKeyError if already present)
            self._col.insert_one(execution.to_dict())
            return
        except DuplicateKeyError:            
            self._col.replace_one({"key": execution.key}, execution.to_dict(), upsert=False)
        except PyMongoError as e:
            raise RuntimeError(f"Mongo save_messages failed: {e}") from e

    def get(self, key: str) -> Optional[Execution]:
        try:
            doc = self._col.find_one({"key": key})
            if not doc:
                return None
            return Execution.from_dict(doc)
        except PyMongoError as e:
            raise RuntimeError(f"Mongo fetch_messages failed: {e}") from e

    def close(self) -> None:
        self._client.close()
