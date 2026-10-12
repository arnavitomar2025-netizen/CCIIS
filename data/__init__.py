# Package marker for data module
from .mock_db import get_db, CCIISDatabase

__all__ = ["get_db", "CCIISDatabase"]
