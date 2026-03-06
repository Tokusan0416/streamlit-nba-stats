#!/usr/bin/env python3
"""
Backfill historical player season statistics.

This script fetches player statistics for all historical seasons
and loads them into BigQuery. It is intended for initial data loading
or backfilling missing historical data.

Usage:
    python backfill_player_stats.py [--start-year YYYY] [--end-year YYYY] [--dry-run]

Examples:
    # Backfill all historical data (1997-2025)
    python backfill_player_stats.py

    # Backfill specific year range
    python backfill_player_stats.py --start-year 2020 --end-year 2023

    # Dry run (fetch but don't load to BigQuery)
    python backfill_player_stats.py --dry-run
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
from utils.season_generator import generate_season_list
from extractors.player_stats import PlayerStatsExtractor
from loaders.bigquery_loader import BigQueryLoader


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('backfill_player_stats.log')
    ]
)
logger = logging.getLogger(__name__)


def backfill_player_stats(
    start_year: int,
    end_year: int,
    dry_run: bool = False,
    per_mode: str = "PerGame"
) -> bool:
    """
    Backfill player statistics for specified year range.

    Args:
        start_year: Starting year (e.g., 1997 for 1997-98 season)
        end_year: Ending year (e.g., 2025 for 2025-26 season)
        dry_run: If True, fetch data but don't load to BigQuery
        per_mode: Statistics mode ("PerGame", "Totals", etc.)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info("="*80)
        logger.info("BACKFILL PLAYER STATISTICS")
        logger.info("="*80)
        logger.info(f"Year range: {start_year}-{end_year}")
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

        # Generate season list
        seasons = generate_season_list(start_year, end_year)
        logger.info(f"Generated {len(seasons)} seasons to backfill")

        # Initialize extractor and loader
        extractor = PlayerStatsExtractor()
        loader = BigQueryLoader() if not dry_run else None

        # Fetch data for all seasons
        logger.info("Fetching data from NBA API...")
        combined_df = extractor.fetch_multiple_seasons(
            seasons=seasons,
            per_mode=per_mode,
            continue_on_error=True
        )

        if combined_df.empty:
            logger.error("No data was fetched")
            return False

        logger.info(f"Fetched total of {len(combined_df)} player-season records")

        # Load to BigQuery
        if not dry_run:
            logger.info("Loading data to BigQuery...")
            loader.load_player_season_stats(
                df=combined_df,
                write_disposition="WRITE_APPEND"
            )
            logger.info("Data loaded successfully!")
        else:
            logger.info("DRY RUN: Skipping BigQuery load")
            logger.info(f"Would have loaded {len(combined_df)} records")

        logger.info("="*80)
        logger.info("BACKFILL COMPLETED SUCCESSFULLY")
        logger.info("="*80)

        return True

    except Exception as e:
        logger.error(f"Backfill failed: {str(e)}", exc_info=True)
        return False


def main():
    """Main entry point for the backfill script."""
    parser = argparse.ArgumentParser(
        description="Backfill historical NBA player season statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '--start-year',
        type=int,
        default=Config.HISTORICAL_START_YEAR,
        help=f'Starting year (default: {Config.HISTORICAL_START_YEAR})'
    )

    parser.add_argument(
        '--end-year',
        type=int,
        default=Config.CURRENT_YEAR,
        help=f'Ending year (default: {Config.CURRENT_YEAR})'
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
        help='Fetch data but do not load to BigQuery'
    )

    args = parser.parse_args()

    # Validate arguments
    if args.start_year > args.end_year:
        logger.error(f"start_year ({args.start_year}) must be <= end_year ({args.end_year})")
        sys.exit(1)

    # Run backfill
    success = backfill_player_stats(
        start_year=args.start_year,
        end_year=args.end_year,
        dry_run=args.dry_run,
        per_mode=args.per_mode
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
