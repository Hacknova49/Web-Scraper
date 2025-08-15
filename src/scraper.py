"""
Main web scraper module with comprehensive error handling and features.
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import yaml
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential
from .utils import setup_logging, validate_url, check_robots_txt
from .storage import DataStorage
from .async_scraper import AsyncScraper


class WebScraper:
    """
    A comprehensive web scraper with error handling, rate limiting, and multiple output formats.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the scraper with configuration."""
        self.config = self._load_config(config_path)
        self.session = requests.Session()
        self.ua = UserAgent()
        self.storage = DataStorage(self.config.get('output', {}))
        self.logger = setup_logging()
        
        # Setup session headers
        self._setup_session()
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            self.logger.error(f"Configuration file {config_path} not found")
            raise
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing configuration file: {e}")
            raise
    
    def _setup_session(self):
        """Setup session with headers and configuration."""
        headers = self.config.get('scraper', {}).get('headers', {})
        if not headers.get('User-Agent'):
            headers['User-Agent'] = self.ua.random
        
        self.session.headers.update(headers)
        
        # Setup timeout
        timeout = self.config.get('scraper', {}).get('timeout', 30)
        self.session.timeout = timeout
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML content from URL with retry logic and error handling.
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if failed
        """
        try:
            # Validate URL
            if not validate_url(url):
                self.logger.error(f"Invalid URL: {url}")
                return None
            
            # Check robots.txt compliance
            if not check_robots_txt(url, self.session.headers.get('User-Agent', '')):
                self.logger.warning(f"Robots.txt disallows scraping: {url}")
                return None
            
            self.logger.info(f"Fetching: {url}")
            
            response = self.session.get(url)
            response.raise_for_status()
            
            # Check content type
            content_type = response.headers.get('content-type', '')
            if 'text/html' not in content_type:
                self.logger.warning(f"Non-HTML content type: {content_type}")
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed for {url}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching {url}: {e}")
            raise
    
    def parse_data(self, html: str, selectors: Dict[str, str]) -> Dict[str, Any]:
        """
        Parse HTML content using CSS selectors.
        
        Args:
            html: HTML content to parse
            selectors: Dictionary of field names and CSS selectors
            
        Returns:
            Dictionary of parsed data
        """
        try:
            soup = BeautifulSoup(html, 'lxml')
            data = {}
            
            for field, selector in selectors.items():
                try:
                    elements = soup.select(selector)
                    if elements:
                        # Handle multiple elements
                        if len(elements) == 1:
                            data[field] = elements[0].get_text(strip=True)
                        else:
                            data[field] = [elem.get_text(strip=True) for elem in elements]
                    else:
                        data[field] = None
                        self.logger.warning(f"No elements found for selector: {selector}")
                        
                except Exception as e:
                    self.logger.error(f"Error parsing field {field} with selector {selector}: {e}")
                    data[field] = None
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error parsing HTML: {e}")
            return {}
    
    def scrape_single_page(self, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Scrape a single page.
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            Parsed data or None if failed
        """
        html = self.fetch_html(url)
        if html:
            data = self.parse_data(html, selectors)
            data['url'] = url  # Add source URL
            data['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
            return data
        return None
    
    def scrape_with_pagination(self, target_config: Dict) -> List[Dict[str, Any]]:
        """
        Scrape multiple pages with pagination support.
        
        Args:
            target_config: Configuration for the target site
            
        Returns:
            List of scraped data from all pages
        """
        all_data = []
        base_url = target_config['base_url']
        selectors = target_config['selectors']
        pagination_config = target_config.get('pagination', {})
        
        if not pagination_config.get('enabled', False):
            # Single page scraping
            data = self.scrape_single_page(base_url, selectors)
            if data:
                all_data.append(data)
            return all_data
        
        # Multi-page scraping
        current_url = base_url
        max_pages = pagination_config.get('max_pages', 10)
        next_selector = pagination_config.get('next_button')
        page_count = 0
        
        while current_url and page_count < max_pages:
            self.logger.info(f"Scraping page {page_count + 1}: {current_url}")
            
            # Scrape current page
            html = self.fetch_html(current_url)
            if not html:
                break
                
            data = self.parse_data(html, selectors)
            if data:
                data['url'] = current_url
                data['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                data['page_number'] = page_count + 1
                all_data.append(data)
            
            # Find next page URL
            if next_selector:
                soup = BeautifulSoup(html, 'lxml')
                next_link = soup.select_one(next_selector)
                if next_link and next_link.get('href'):
                    current_url = urljoin(current_url, next_link['href'])
                else:
                    break
            else:
                break
            
            page_count += 1
            
            # Rate limiting
            rate_limit = self.config.get('scraper', {}).get('rate_limit', 1)
            time.sleep(rate_limit)
        
        self.logger.info(f"Scraped {len(all_data)} items from {page_count} pages")
        return all_data
    
    def scrape_target(self, target_name: str) -> List[Dict[str, Any]]:
        """
        Scrape a configured target.
        
        Args:
            target_name: Name of the target in configuration
            
        Returns:
            List of scraped data
        """
        targets = self.config.get('targets', {})
        if target_name not in targets:
            self.logger.error(f"Target '{target_name}' not found in configuration")
            return []
        
        target_config = targets[target_name]
        self.logger.info(f"Starting scrape for target: {target_name}")
        
        try:
            data = self.scrape_with_pagination(target_config)
            self.logger.info(f"Successfully scraped {len(data)} items for {target_name}")
            return data
        except Exception as e:
            self.logger.error(f"Error scraping target {target_name}: {e}")
            return []
    
    def scrape_custom_url(self, url: str, selectors: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Scrape a custom URL with provided selectors.
        
        Args:
            url: URL to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            Scraped data or None if failed
        """
        return self.scrape_single_page(url, selectors)
    
    def run_async_scrape(self, urls: List[str], selectors: Dict[str, str]) -> List[Dict[str, Any]]:
        """
        Run asynchronous scraping for multiple URLs.
        
        Args:
            urls: List of URLs to scrape
            selectors: CSS selectors for data extraction
            
        Returns:
            List of scraped data
        """
        async_scraper = AsyncScraper(self.config)
        return asyncio.run(async_scraper.scrape_urls(urls, selectors))
    
    def save_data(self, data: List[Dict[str, Any]], filename: Optional[str] = None):
        """
        Save scraped data using the storage module.
        
        Args:
            data: List of data dictionaries to save
            filename: Optional custom filename
        """
        self.storage.save(data, filename)
    
    def close(self):
        """Clean up resources."""
        self.session.close()