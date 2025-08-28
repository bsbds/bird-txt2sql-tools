from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Abstract base class for text-to-SQL agents."""

    @abstractmethod
    async def ainvoke(self, state: dict[str, Any]) -> dict[str, Any]:
        """Invoke the agent asynchronously with the given state."""
        pass


class AgentFactory(ABC):
    """Abstract factory for creating agents from configuration."""

    @abstractmethod
    def create_agent(
        self, config_path: str, storage_root: str | None = None
    ) -> Agent:
        """Create an agent from configuration."""
        pass
