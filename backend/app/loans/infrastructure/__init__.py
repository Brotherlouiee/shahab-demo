"""Local/test adapters for the serving loan catalogue port."""

from .in_memory_catalogue import InMemoryServingLoanCatalogueRepository
from .sqlalchemy_catalogue import SqlAlchemyServingLoanCatalogueRepository

__all__ = ["InMemoryServingLoanCatalogueRepository", "SqlAlchemyServingLoanCatalogueRepository"]
