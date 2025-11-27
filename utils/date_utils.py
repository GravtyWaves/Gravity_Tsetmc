"""
Utility module for date conversion and validation functions
"""

import jdatetime
import datetime
from typing import Optional


def jalali_to_gregorian(jalali_str: str) -> Optional[datetime.date]:
    """
    Convert Jalali date string (YYYY-MM-DD) to Gregorian date.
    
    Args:
        jalali_str: Date string in YYYY-MM-DD format (Jalali)
    
    Returns:
        datetime.date object in Gregorian calendar or None if invalid
    """
    try:
        parts = jalali_str.split('-')
        if len(parts) != 3:
            return None
        year, month, day = map(int, parts)
        jalali_date = jdatetime.date(year, month, day)
        gregorian_date = jalali_date.togregorian()
        return gregorian_date
    except Exception as e:
        return None


def gregorian_to_jalali(gregorian_date: datetime.date) -> str:
    """
    Convert Gregorian date to Jalali date string (YYYY-MM-DD).
    
    Args:
        gregorian_date: datetime.date object in Gregorian calendar
    
    Returns:
        Date string in YYYY-MM-DD format (Jalali)
    """
    try:
        jalali_date = jdatetime.date.fromgregorian(date=gregorian_date)
        return str(jalali_date)
    except Exception as e:
        return None


def timestamp_to_jalali(timestamp: int) -> Optional[str]:
    """
    Convert Unix timestamp to Jalali date string.
    
    Args:
        timestamp: Unix timestamp (seconds since epoch)
    
    Returns:
        Date string in YYYY-MM-DD format (Jalali) or None if invalid
    """
    try:
        gregorian_date = datetime.datetime.fromtimestamp(timestamp).date()
        return gregorian_to_jalali(gregorian_date)
    except Exception as e:
        return None


def validate_jalali_date(date_str: str) -> bool:
    """
    Validate if a string is a valid Jalali date in YYYY-MM-DD format.
    
    Args:
        date_str: Date string to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        parts = date_str.split('-')
        if len(parts) != 3:
            return False
        year, month, day = map(int, parts)
        jdatetime.date(year, month, day)
        return True
    except Exception:
        return False
