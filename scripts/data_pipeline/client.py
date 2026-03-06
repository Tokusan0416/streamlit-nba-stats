"""
BigQuery client initialization and management.
"""
from google.cloud import bigquery
from google.api_core import retry
import logging
from typing import Optional

from .config import Config


logger = logging.getLogger(__name__)


class BigQueryClient:
    """Wrapper class for BigQuery client with common operations."""

    _instance: Optional[bigquery.Client] = None

    @classmethod
    def get_client(cls) -> bigquery.Client:
        """
        Get or create BigQuery client instance (singleton pattern).

        Returns:
            bigquery.Client: Initialized BigQuery client
        """
        if cls._instance is None:
            logger.info(f"Initializing BigQuery client for project: {Config.PROJECT_ID}")
            cls._instance = bigquery.Client(project=Config.PROJECT_ID)
            logger.info("BigQuery client initialized successfully")

        return cls._instance

    @classmethod
    def test_connection(cls) -> bool:
        """
        Test BigQuery connection by listing datasets.

        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            client = cls.get_client()
            datasets = list(client.list_datasets())

            if datasets:
                logger.info("BigQuery connection successful. Datasets found:")
                for dataset in datasets:
                    logger.info(f"  - {dataset.dataset_id}")
            else:
                logger.info("BigQuery connection successful (no datasets yet)")

            return True

        except Exception as e:
            logger.error(f"BigQuery connection failed: {str(e)}")
            return False

    @classmethod
    def reset_client(cls) -> None:
        """Reset the client instance (useful for testing)."""
        if cls._instance is not None:
            cls._instance.close()
            cls._instance = None
            logger.info("BigQuery client reset")
