#!/usr/bin/env python3
"""
Update current season player statistics.

This script fetches the latest player statistics for the current NBA season
and updates BigQuery. It is designed to be run periodically (e.g., daily or weekly)
to keep the data fresh during the season.

The script uses an upsert approach: it deletes existing data for the current
season and inserts the latest data, ensuring no duplicates.

Usage:
    python update_current_season.py [--season YYYY-YY] [--dry-run]

Examples:
    # Update current season (auto-detected from config)
    python update_current_season.py

    # Update specific season
    python update_current_season.py --season 2024-25

    # Dry run (fetch but don't update BigQuery)
    python update_current_season.py --dry-run
"""
import argparse
import logging
import sys
from typing import Optional

# Add parent directory to path for imports
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from client import BigQueryClient
from extractors.player_stats import PlayerStatsExtractor
from loaders.bigquery_loader import BigQueryLoader


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('update_current_season.log')
    ]
)
logger = logging.getLogger(__name__)


def update_current_season(
    season: Optional[str] = None,
    dry_run: bool = False,
    per_mode: str = "PerGame"
) -> bool:
    """
    Update player statistics for the current season.

    Args:
        season: Season string (e.g., "2024-25"). If None, uses current season from config
        dry_run: If True, fetch data but don't update BigQuery
        per_mode: Statistics mode ("PerGame", "Totals", etc.)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use current season if not specified
        if season is None:
            season = Config.get_current_season()

        logger.info("="*80)
        logger.info("UPDATE CURRENT SEASON STATISTICS")
        logger.info("="*80)
        logger.info(f"Season: {season}")
        logger.info(f"Per mode: {per_mode}")
        logger.info(f"Dry run: {dry_run}")
        logger.info(f"Target table: {Config.PLAYER_SEASON_STATS_TABLE_ID}")
        logger.info("="*80)

        # Test BigQuery connection
        if not dry_run:
            logger.info("Testing BigQuery connection...")
            if not BigQueryClient.test_connection():
                logger.error("BigQuery connection test failed")
                return False

        # Initialize extractor and loader
        extractor = PlayerStatsExtractor()
        loader = BigQueryLoader() if not dry_run else None

        # Fetch current season data
        logger.info(f"Fetching {season} season data from NBA API...")
        season_df = extractor.fetch_season_stats(
            season=season,
            per_mode=per_mode
        )

        if season_df.empty:
            logger.error(f"No data returned for season {season}")
            return False

        logger.info(f"Fetched {len(season_df)} player records for {season}")

        # Upsert to BigQuery (delete existing + insert new)
        if not dry_run:
            logger.info(f"Upserting data for {season} to BigQuery...")
            logger.info("  1. Deleting existing data for this season...")
            rows_deleted = loader.delete_season_data(season)
            logger.info(f"     Deleted {rows_deleted} existing rows")

            logger.info("  2. Inserting new data...")
            loader.load_player_season_stats(
                df=season_df,
                write_disposition="WRITE_APPEND"
            )
            logger.info("Data updated successfully!")
        else:
            logger.info("DRY RUN: Skipping BigQuery update")
            logger.info(f"Would have upserted {len(season_df)} records for {season}")

        logger.info("="*80)
        logger.info("UPDATE COMPLETED SUCCESSFULLY")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.error(f"Update failed: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point for the update script."""
    parser = argparse.ArgumentParser(
        description="Update current NBA season player statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--season',
        type=str,
        default=None,
        help=f'Season to update (default: current season from config)'
    )

    parser.add_argument(
        '--per-mode',
        type=str,
        default='PerGame',
        choices=['PerGame', 'Totals', 'Per36', 'Per100Possessions'],
        help='Statistics mode (default: PerGame)'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Fetch data but do not update BigQuery'
    )

    args = parser.parse_args()

    # Run update
    success = update_current_season(
        season=args.season,
        dry_run=args.dry_run,
        per_mode=args.per_mode
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
