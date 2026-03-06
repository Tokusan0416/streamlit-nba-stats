"""
NBA API data extraction for player statistics.
"""
import pandas as pd
import datetime
import time
import logging
from typing import Optional
from nba_api.stats.endpoints import leaguedashplayerstats

from ..config import Config

logger = logging.getLogger(__name__)


class PlayerStatsExtractor:
    """Extractor for NBA player season statistics."""

    def __init__(self, rate_limit_delay: Optional[float] = None):
        """
        Initialize the extractor.

        Args:
            rate_limit_delay: Delay in seconds between API calls (default from config)
        """
        self.rate_limit_delay = rate_limit_delay or Config.NBA_API_RATE_LIMIT_DELAY
        self.last_request_time: Optional[float] = None

    def _rate_limit(self) -> None:
        """Apply rate limiting between API requests."""
        if self.last_request_time is not None:
            elapsed = time.time() - self.last_request_time
            if elapsed < self.rate_limit_delay:
                sleep_time = self.rate_limit_delay - elapsed
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)

        self.last_request_time = time.time()

    def fetch_season_stats(
        self,
        season: str,
        per_mode: str = "PerGame",
        add_metadata: bool = True
    ) -> pd.DataFrame:
        """
        Fetch player statistics for a specific season from NBA API.

        Args:
            season: Season string in format "YYYY-YY" (e.g., "2024-25")
            per_mode: Statistics mode - "PerGame", "Totals", "Per36", etc.
            add_metadata: Whether to add SEASON and UPDATED_DT columns

        Returns:
            pd.DataFrame: Player statistics dataframe

        Raises:
            Exception: If API request fails
        """
        logger.info(f"Fetching {season} season stats (per_mode={per_mode})...")

        try:
            # Apply rate limiting
            self._rate_limit()

            # Fetch data from NBA API
            stats = leaguedashplayerstats.LeagueDashPlayerStats(
                season=season,
                per_mode_detailed=per_mode,
                timeout=Config.NBA_API_TIMEOUT
            )

            df = stats.get_data_frames()[0]

            if df.empty:
                logger.warning(f"No data returned for season {season}")
                return df

            # Add metadata columns
            if add_metadata:
                df["SEASON"] = season
                df["UPDATED_DT"] = datetime.datetime.now()

            logger.info(f"Successfully fetched {len(df)} player records for {season}")
            return df

        except Exception as e:
            logger.error(f"Failed to fetch stats for season {season}: {str(e)}")
            raise

    def fetch_multiple_seasons(
        self,
        seasons: list[str],
        per_mode: str = "PerGame",
        continue_on_error: bool = True
    ) -> pd.DataFrame:
        """
        Fetch player statistics for multiple seasons.

        Args:
            seasons: List of season strings (e.g., ["2023-24", "2024-25"])
            per_mode: Statistics mode
            continue_on_error: If True, continue fetching other seasons on error

        Returns:
            pd.DataFrame: Combined dataframe of all seasons

        Raises:
            Exception: If fetching fails and continue_on_error is False
        """
        logger.info(f"Fetching stats for {len(seasons)} seasons...")

        all_data = []
        failed_seasons = []

        for i, season in enumerate(seasons, 1):
            try:
                logger.info(f"Progress: {i}/{len(seasons)} - {season}")
                df = self.fetch_season_stats(season, per_mode=per_mode)

                if not df.empty:
                    all_data.append(df)
                else:
                    logger.warning(f"Empty data for season {season}")

            except Exception as e:
                logger.error(f"Failed to fetch season {season}: {str(e)}")
                failed_seasons.append(season)

                if not continue_on_error:
                    raise

        # Combine all dataframes
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(
                f"Successfully fetched {len(combined_df)} total records "
                f"from {len(all_data)}/{len(seasons)} seasons"
            )

            if failed_seasons:
                logger.warning(f"Failed seasons: {', '.join(failed_seasons)}")

            return combined_df
        else:
            logger.error("No data fetched for any season")
            return pd.DataFrame()

    def get_latest_season_data(self, per_mode: str = "PerGame") -> pd.DataFrame:
        """
        Fetch data for the current/latest season.

        Args:
            per_mode: Statistics mode

        Returns:
            pd.DataFrame: Current season player statistics
        """
        current_season = Config.get_current_season()
        logger.info(f"Fetching latest season: {current_season}")
        return self.fetch_season_stats(current_season, per_mode=per_mode)
