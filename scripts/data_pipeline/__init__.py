"""
NBA Data Pipeline

A modular data pipeline for extracting NBA statistics from the NBA API
and loading them into Google BigQuery.
"""

__version__ = "1.0.0"

from .config import Config
from .client import BigQueryClient

__all__ = ["Config", "BigQueryClient"]
