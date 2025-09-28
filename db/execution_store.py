from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from objects.execution import Execution


# ---------- Storage Interface (extend for other NoSQL backends) ----------

class ExecutionStore(ABC):
    @abstractmethod
    def save(self, execution: Execution) -> None:
        """Persist (create or replace) the full message list for an issue."""
        ...

    @abstractmethod
    def get(self, key: str) -> Dict[str, Any]:
        """Return previously saved messages; empty list if none."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Release underlying resources."""
        ...
