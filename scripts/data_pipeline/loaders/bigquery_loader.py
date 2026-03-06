"""
BigQuery data loading functionality.
"""
import pandas as pd
import logging
from typing import Optional, Literal
from google.cloud import bigquery

from ..client import BigQueryClient
from ..config import Config

logger = logging.getLogger(__name__)


class BigQueryLoader:
    """Loader for writing data to BigQuery tables."""

    def __init__(self, client: Optional[bigquery.Client] = None):
        """
        Initialize the loader.

        Args:
            client: BigQuery client instance (if None, will use default from BigQueryClient)
        """
        self.client = client or BigQueryClient.get_client()

    def load_dataframe(
        self,
        df: pd.DataFrame,
        table_id: str,
        write_disposition: Literal["WRITE_APPEND", "WRITE_TRUNCATE", "WRITE_EMPTY"] = "WRITE_APPEND"
    ) -> bigquery.LoadJob:
        """
        Load a pandas DataFrame to a BigQuery table.

        Args:
            df: DataFrame to load
            table_id: Fully qualified table ID (project.dataset.table)
            write_disposition: How to handle existing data
                - WRITE_APPEND: Append to existing table
                - WRITE_TRUNCATE: Overwrite table
                - WRITE_EMPTY: Only write if table is empty

        Returns:
            bigquery.LoadJob: The completed load job

        Raises:
            Exception: If load fails
        """
        if df.empty:
            logger.warning(f"DataFrame is empty, skipping load to {table_id}")
            return None

        logger.info(f"Loading {len(df)} rows to {table_id} (write_disposition={write_disposition})")

        try:
            job_config = bigquery.LoadJobConfig(
                write_disposition=write_disposition
            )

            job = self.client.load_table_from_dataframe(
                df,
                destination=table_id,
                job_config=job_config
            )

            # Wait for job to complete
            job.result()

            logger.info(
                f"Successfully loaded {len(df)} rows to {table_id}. "
                f"Job ID: {job.job_id}"
            )

            return job

        except Exception as e:
            logger.error(f"Failed to load data to {table_id}: {str(e)}")
            raise

    def load_player_season_stats(
        self,
        df: pd.DataFrame,
        write_disposition: Literal["WRITE_APPEND", "WRITE_TRUNCATE", "WRITE_EMPTY"] = "WRITE_APPEND"
    ) -> bigquery.LoadJob:
        """
        Load player season statistics to the configured table.

        Args:
            df: Player stats DataFrame
            write_disposition: How to handle existing data

        Returns:
            bigquery.LoadJob: The completed load job
        """
        return self.load_dataframe(
            df=df,
            table_id=Config.PLAYER_SEASON_STATS_TABLE_ID,
            write_disposition=write_disposition
        )

    def delete_season_data(self, season: str, table_id: Optional[str] = None) -> int:
        """
        Delete data for a specific season from a table.

        Args:
            season: Season string (e.g., "2024-25")
            table_id: Table ID (if None, uses default player stats table)

        Returns:
            int: Number of rows deleted

        Raises:
            Exception: If delete fails
        """
        table_id = table_id or Config.PLAYER_SEASON_STATS_TABLE_ID

        logger.info(f"Deleting data for season {season} from {table_id}")

        try:
            query = f"""
                DELETE FROM `{table_id}`
                WHERE SEASON = @season
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("season", "STRING", season)
                ]
            )

            query_job = self.client.query(query, job_config=job_config)
            query_job.result()

            rows_deleted = query_job.num_dml_affected_rows
            logger.info(f"Deleted {rows_deleted} rows for season {season}")

            return rows_deleted

        except Exception as e:
            logger.error(f"Failed to delete data for season {season}: {str(e)}")
            raise

    def upsert_season_data(
        self,
        df: pd.DataFrame,
        season: str,
        table_id: Optional[str] = None
    ) -> bigquery.LoadJob:
        """
        Upsert (delete + insert) data for a specific season.
        This ensures no duplicate data for the season.

        Args:
            df: Player stats DataFrame
            season: Season string (e.g., "2024-25")
            table_id: Table ID (if None, uses default player stats table)

        Returns:
            bigquery.LoadJob: The completed load job
        """
        table_id = table_id or Config.PLAYER_SEASON_STATS_TABLE_ID

        logger.info(f"Upserting {len(df)} rows for season {season} to {table_id}")

        # Delete existing data for this season
        self.delete_season_data(season, table_id)

        # Insert new data
        return self.load_dataframe(
            df=df,
            table_id=table_id,
            write_disposition="WRITE_APPEND"
        )

    def get_existing_seasons(self, table_id: Optional[str] = None) -> list[str]:
        """
        Get list of seasons that already exist in the table.

        Args:
            table_id: Table ID (if None, uses default player stats table)

        Returns:
            list[str]: List of existing season strings

        Raises:
            Exception: If query fails
        """
        table_id = table_id or Config.PLAYER_SEASON_STATS_TABLE_ID

        logger.info(f"Fetching existing seasons from {table_id}")

        try:
            query = f"""
                SELECT DISTINCT SEASON
                FROM `{table_id}`
                ORDER BY SEASON DESC
            """

            query_job = self.client.query(query)
            results = query_job.result()

            seasons = [row.SEASON for row in results]
            logger.info(f"Found {len(seasons)} existing seasons")

            return seasons

        except Exception as e:
            logger.error(f"Failed to fetch existing seasons: {str(e)}")
            raise
