"""
Configuration settings for NBA data pipeline.

Configuration Priority (highest to lowest):
1. Environment variables
2. .env file (if python-dotenv is installed)
3. Default values in this file

File Roles:
- secrets.toml: Authentication credentials ONLY (service account keys, passwords)
- .env: Environment-specific settings (project IDs, table names) - NOT committed to git
- config.py: Application defaults (rate limits, timeouts, constants) - Committed to git

Security Best Practices:
- NEVER commit secrets.toml or .env to git
- Keep authentication separate from configuration
- Use environment variables for deployment environments
"""
import os
from pathlib import Path
from typing import Optional

# Load .env file if exists (optional dependency)
try:
    from dotenv import load_dotenv
    # Look for .env in project root (3 levels up from this file)
    env_path = Path(__file__).parents[3] / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"[Config] Loaded environment from: {env_path}")
except ImportError:
    # python-dotenv not installed, will use environment variables only
    pass


class Config:
    """
    Configuration class for data pipeline settings.

    Environment Variables:
    Required:
        - GCP_PROJECT_ID: Google Cloud Project ID

    Optional (with defaults):
        - PLAYER_SEASON_STATS_TABLE: Full table ID (project.dataset.table)
        - NBA_API_RATE_LIMIT_DELAY: Seconds between API calls (default: 2.0)
        - NBA_API_TIMEOUT: API timeout in seconds (default: 30)
        - HISTORICAL_START_YEAR: First season year (default: 1997)
        - CURRENT_YEAR: Current season start year (default: 2025)
        - BIGQUERY_WRITE_DISPOSITION: Write mode (default: WRITE_APPEND)
    """

    # Google Cloud Project settings (REQUIRED)
    PROJECT_ID: str = os.getenv("GCP_PROJECT_ID", "")

    # BigQuery table IDs
    # Can be overridden with full table ID: "project.dataset.table"
    PLAYER_SEASON_STATS_TABLE_ID: str = os.getenv(
        "PLAYER_SEASON_STATS_TABLE",
        f"{PROJECT_ID}.nba_stats.fact_player_season_stats" if PROJECT_ID else ""
    )

    # NBA API settings (with sensible defaults)
    NBA_API_RATE_LIMIT_DELAY: float = float(
        os.getenv("NBA_API_RATE_LIMIT_DELAY", "2.0")
    )
    NBA_API_TIMEOUT: int = int(os.getenv("NBA_API_TIMEOUT", "30"))

    # Data range settings (with defaults)
    HISTORICAL_START_YEAR: int = int(os.getenv("HISTORICAL_START_YEAR", "1997"))
    CURRENT_YEAR: int = int(os.getenv("CURRENT_YEAR", "2025"))

    # BigQuery write settings (with defaults)
    BIGQUERY_WRITE_DISPOSITION: str = os.getenv(
        "BIGQUERY_WRITE_DISPOSITION", "WRITE_APPEND"
    )

    @classmethod
    def get_current_season(cls) -> str:
        """
        Get the current NBA season string.

        Returns:
            str: Current season in format "YYYY-YY" (e.g., "2024-25")
        """
        year = cls.CURRENT_YEAR
        next_yy = str(year + 1)[2:]
        return f"{year}-{next_yy}"

    @classmethod
    def validate(cls) -> None:
        """
        Validate configuration settings.

        Raises:
            ValueError: If any required configuration is invalid
        """
        if not cls.PROJECT_ID:
            raise ValueError(
                "GCP_PROJECT_ID is required. "
                "Set it via environment variable or create a .env file. "
                "See .env.example for template."
            )

        if not cls.PLAYER_SEASON_STATS_TABLE_ID:
            raise ValueError(
                "PLAYER_SEASON_STATS_TABLE is required. "
                "Set it via environment variable or create a .env file."
            )

        if cls.NBA_API_RATE_LIMIT_DELAY < 0:
            raise ValueError("NBA_API_RATE_LIMIT_DELAY must be non-negative")

        if cls.HISTORICAL_START_YEAR < 1946:  # NBA founded in 1946
            raise ValueError("HISTORICAL_START_YEAR must be 1946 or later")

    @classmethod
    def display_config(cls) -> None:
        """Display current configuration (for debugging)."""
        print("="*60)
        print("Configuration Settings")
        print("="*60)
        print(f"PROJECT_ID: {cls.PROJECT_ID}")
        print(f"PLAYER_SEASON_STATS_TABLE: {cls.PLAYER_SEASON_STATS_TABLE_ID}")
        print(f"NBA_API_RATE_LIMIT_DELAY: {cls.NBA_API_RATE_LIMIT_DELAY}s")
        print(f"NBA_API_TIMEOUT: {cls.NBA_API_TIMEOUT}s")
        print(f"HISTORICAL_START_YEAR: {cls.HISTORICAL_START_YEAR}")
        print(f"CURRENT_YEAR: {cls.CURRENT_YEAR}")
        print(f"CURRENT_SEASON: {cls.get_current_season()}")
        print(f"BIGQUERY_WRITE_DISPOSITION: {cls.BIGQUERY_WRITE_DISPOSITION}")
        print("="*60)


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"[Config] Warning: {e}")
    print("[Config] Please create a .env file based on .env.example")
