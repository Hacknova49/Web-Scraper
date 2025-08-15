"""
Asynchronous web scraper for high-performance scraping.
"""

import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from bs4 import BeautifulSoup
from .utils import setup_logging, validate_url


class AsyncScraper:
    """Asynchronous web scraper for concurrent requests."""
    
    def __init__(self, config: Dict):
        """Initialize async scraper with configuration."""
        self.config = config
        self.logger = setup_logging()
        self.semaphore = asyncio.Semaphore(10)  # Limit concurrent requests
        
    async def fetch_html(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """
        Asynchronously fetch HTML content from URL.
        
        Args:
            session: aiohttp session
            url: URL to fetch
            
        Returns:
            HTML content or None if failed
        """
        async with self.semaphore:
            try:
                if not validate_url(url):
                    self.logger.error(f"Invalid URL: {url}")
                    return None
                
                timeout = aiohttp.ClientTimeout(
                    total=self.config.get('scraper', {}).get('timeout', 30)
                )
                
                async with session.get(url, timeout=timeout) as response:
                    response.raise_for_status()
                    content = await response.text()
                    self.logger.info(f"Successfully fetched: {url}")
                    return content
                    
            except asyncio.TimeoutError:
                self.logger.error(f"Timeout fetching {url}")
                return None
            except aiohttp.ClientError as e:
                self.logger.error(f"Client error fetching {url}: {e}")
                return None
            except Exception as e:
                self.logger.error(f"Unexpected error fetching {url}: {e}")
                return None
    
    def parse_data(self, html: str, selectors: Dict[str, str], url: str) -> Dict[str, Any]:
        """
        Parse HTML content using CSS selectors.
        
        Args:
            html: HTML content to parse
            selectors: Dictionary of field names and CSS selectors
            url: Source URL
            
        Returns:
            Dictionary of parsed data
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            data = {'url': url, 'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')}
            
            for field, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        if len(elements) == 1:
                            data[field] = elements[0].get_text(strip=True)
                        else:
                            data[field] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        data[field] = None
                        self.logger.warning(f"No elements found for selector: {selector}")
                        
                except Exception as e:
                    self.logger.error(f"Error parsing field {field}: {e}")
                    data[field] = None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML from {url}: {e}")
            return {'url': url, 'error': str(e)}
    
    async def scrape_single_url(self, session: aiohttp.ClientSession, url: str, 
                               selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Scrape a single URL asynchronously.
        
        Args:
            session: aiohttp session
            url: URL to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            Parsed data or None if failed
        """
        html = await self.fetch_html(session, url)
        if html:
            return self.parse_data(html, selectors, url)
        return None
    
    async def scrape_urls(self, urls: List[str], selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Scrape multiple URLs concurrently.
        
        Args:
            urls: List of URLs to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            List of scraped data
        """
        headers = self.config.get('scraper', {}).get('headers', {})
        
        connector = aiohttp.TCPConnector(limit=100, limit_per_host=10)
        timeout = aiohttp.ClientTimeout(
            total=self.config.get('scraper', {}).get('timeout', 30)
        )
        
        async with aiohttp.ClientSession(
            headers=headers, 
            connector=connector, 
            timeout=timeout
        ) as session:
            
            tasks = [
                self.scrape_single_url(session, url, selectors) 
                for url in urls
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out None results and exceptions
            valid_results = []
            for result in results:
                if isinstance(result, dict):
                    valid_results.append(result)
                elif isinstance(result, Exception):
                    self.logger.error(f"Task failed with exception: {result}")
            
            self.logger.info(f"Successfully scraped {len(valid_results)} out of {len(urls)} URLs")
            return valid_results