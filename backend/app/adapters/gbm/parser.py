from abc import ABC, abstractmethod

from app.adapters.gbm.schemas import GBMTransactionInput


class GBMParser(ABC):
    """Base contract for all GBM input parsers."""

    @abstractmethod
    def parse(self, payload: str) -> list[GBMTransactionInput]:
        """Parse an external GBM payload into GBM transaction inputs."""
        raise NotImplementedError
