"""
Utility functions for the web scraper.
"""

import logging
import re
import requests
from urllib.parse import urlparse, urljoin
from urllib.robotparser import RobotFileParser
from typing import Optional


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging configuration.
    
    Args:
        level: Logging level
        
    Returns:
        Configured logger
    """
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scraper.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('WebScraper')


def validate_url(url: str) -> bool:
    """
    Validate if a URL is properly formatted.
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def check_robots_txt(url: str, user_agent: str = '*') -> bool:
    """
    Check if scraping is allowed according to robots.txt.
    
    Args:
        url: URL to check
        user_agent: User agent string
        
    Returns:
        True if allowed, False otherwise
    """
    try:
        parsed_url = urlparse(url)
        robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        return rp.can_fetch(user_agent, url)
        
    except Exception:
        # If we can't check robots.txt, assume it's allowed
        return True


def clean_text(text: str) -> str:
    """
    Clean extracted text by removing extra whitespace and special characters.
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Remove special characters that might cause issues
    text = re.sub(r'[^\w\s\-.,!?():]', '', text)
    
    return text


def extract_domain(url: str) -> Optional[str]:
    """
    Extract domain from URL.
    
    Args:
        url: URL to extract domain from
        
    Returns:
        Domain string or None if invalid
    """
    try:
        parsed = urlparse(url)
        return parsed.netloc
    except Exception:
        return None


def is_valid_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def normalize_price(price_text: str) -> Optional[float]:
    """
    Extract and normalize price from text.
    
    Args:
        price_text: Text containing price
        
    Returns:
        Normalized price as float or None
    """
    if not price_text:
        return None
    
    # Remove currency symbols and extract numbers
    price_match = re.search(r'[\d,]+\.?\d*', price_text.replace(',', ''))
    if price_match:
        try:
            return float(price_match.group())
        except ValueError:
            return None
    
    return None


def get_absolute_url(base_url: str, relative_url: str) -> str:
    """
    Convert relative URL to absolute URL.
    
    Args:
        base_url: Base URL
        relative_url: Relative URL
        
    Returns:
        Absolute URL
    """
    return urljoin(base_url, relative_url)