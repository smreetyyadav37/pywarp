from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict

class WarpSource(ABC):
    """Abstract Base Class for all Ingestion Sources."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection (e.g., connect to Kafka broker)."""
        pass

    @abstractmethod
    async def read_stream(self) -> AsyncGenerator[str, None]:
        """Continuously yield raw log strings to the engine."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Safely teardown the connection."""
        pass

class WarpSink(ABC):
    """Abstract Base Class for all Output Destinations."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    async def connect(self) -> None:
        """Establish the connection (e.g., connect to database)."""
        pass

    @abstractmethod
    async def write(self, data: Dict[str, Any]) -> None:
        """Write the structured JSON/Dictionary to the destination."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Safely teardown the connection."""
        pass