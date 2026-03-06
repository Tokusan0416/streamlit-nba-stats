"""
Utility functions for generating NBA season identifiers.
"""
from typing import List
import logging

logger = logging.getLogger(__name__)


def generate_season_list(start_year: int, end_year: int) -> List[str]:
    """
    Generate a list of NBA season strings.

    Args:
        start_year (int): Starting year (e.g., 1997 for 1997-98 season)
        end_year (int): Ending year (e.g., 2025 for 2025-26 season)

    Returns:
        List[str]: List of season strings in format "YYYY-YY" (e.g., ["1997-98", "1998-99", ...])

    Example:
        >>> generate_season_list(1997, 1999)
        ['1997-98', '1998-99', '1999-00']
    """
    if start_year > end_year:
        raise ValueError(f"start_year ({start_year}) must be <= end_year ({end_year})")

    if start_year < 1946:  # NBA founded in 1946
        raise ValueError(f"start_year ({start_year}) must be >= 1946 (NBA founded year)")

    seasons = []
    for year in range(start_year, end_year + 1):
        next_yy = str(year + 1)[2:]  # Get last 2 digits of next year
        season_str = f"{year}-{next_yy}"
        seasons.append(season_str)

    logger.info(f"Generated {len(seasons)} seasons from {start_year} to {end_year}")
    return seasons


def get_season_from_year(year: int) -> str:
    """
    Get NBA season string for a given year.

    Args:
        year (int): Year (e.g., 2024 for 2024-25 season)

    Returns:
        str: Season string in format "YYYY-YY" (e.g., "2024-25")

    Example:
        >>> get_season_from_year(2024)
        '2024-25'
    """
    if year < 1946:
        raise ValueError(f"year ({year}) must be >= 1946 (NBA founded year)")

    next_yy = str(year + 1)[2:]
    return f"{year}-{next_yy}"


def parse_season_string(season: str) -> tuple[int, int]:
    """
    Parse NBA season string into start and end years.

    Args:
        season (str): Season string in format "YYYY-YY" (e.g., "2024-25")

    Returns:
        tuple[int, int]: (start_year, end_year) (e.g., (2024, 2025))

    Raises:
        ValueError: If season string format is invalid

    Example:
        >>> parse_season_string("2024-25")
        (2024, 2025)
    """
    try:
        parts = season.split("-")
        if len(parts) != 2:
            raise ValueError

        start_year = int(parts[0])
        end_yy = int(parts[1])

        # Reconstruct full end year
        century = (start_year // 100) * 100
        end_year = century + end_yy

        # Handle century rollover (e.g., 1999-00 -> 1999, 2000)
        if end_yy < (start_year % 100):
            end_year += 100

        if end_year != start_year + 1:
            raise ValueError(f"End year must be start_year + 1")

        return start_year, end_year

    except (ValueError, IndexError) as e:
        raise ValueError(
            f"Invalid season format: '{season}'. Expected format: 'YYYY-YY' (e.g., '2024-25')"
        ) from e
