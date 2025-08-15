#!/usr/bin/env python3
"""
Example usage of the web scraper.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scraper import WebScraper


def example_basic_scraping():
    """Example of basic scraping functionality."""
    print("=== Basic Scraping Example ===")
    
    # Initialize scraper
    scraper = WebScraper('config.yaml')
    
    # Example: Scrape a single page
    url = "https://quotes.toscrape.com/"
    selectors = {
        'quote': 'span.text',
        'author': 'small.author',
        'tags': 'div.tags a.tag'
    }
    
    try:
        data = scraper.scrape_custom_url(url, selectors)
        if data:
            print(f"Scraped data: {data}")
            scraper.save_data([data], 'quotes_example')
        else:
            print("No data scraped")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_async_scraping():
    """Example of asynchronous scraping."""
    print("=== Async Scraping Example ===")
    
    scraper = WebScraper('config.yaml')
    
    # Multiple URLs to scrape
    urls = [
        "https://quotes.toscrape.com/page/1/",
        "https://quotes.toscrape.com/page/2/",
        "https://quotes.toscrape.com/page/3/"
    ]
    
    selectors = {
        'quotes': 'span.text',
        'authors': 'small.author'
    }
    
    try:
        data = scraper.run_async_scrape(urls, selectors)
        print(f"Scraped {len(data)} pages asynchronously")
        scraper.save_data(data, 'async_quotes_example')
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_configured_target():
    """Example of scraping a configured target."""
    print("=== Configured Target Example ===")
    
    scraper = WebScraper('config.yaml')
    
    try:
        # This would use a target defined in config.yaml
        # data = scraper.scrape_target('example_news')
        # For demo purposes, we'll show the structure
        print("To use configured targets, add them to config.yaml:")
        print("""
targets:
  quotes_site:
    base_url: "https://quotes.toscrape.com"
    selectors:
      quote: "span.text"
      author: "small.author"
      tags: "div.tags a.tag"
    pagination:
      enabled: true
      next_button: "li.next a"
      max_pages: 5
        """)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


def example_custom_processing():
    """Example of custom data processing."""
    print("=== Custom Processing Example ===")
    
    class CustomScraper(WebScraper):
        def parse_data(self, html, selectors):
            """Override parse_data for custom processing."""
            data = super().parse_data(html, selectors)
            
            # Custom processing
            if 'quote' in data and data['quote']:
                data['quote_length'] = len(data['quote'])
                data['quote_words'] = len(data['quote'].split())
            
            return data
    
    scraper = CustomScraper('config.yaml')
    
    url = "https://quotes.toscrape.com/"
    selectors = {
        'quote': 'span.text',
        'author': 'small.author'
    }
    
    try:
        data = scraper.scrape_custom_url(url, selectors)
        if data:
            print(f"Custom processed data: {data}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    print("Web Scraper Examples")
    print("=" * 50)
    
    # Run examples
    example_basic_scraping()
    print()
    
    example_async_scraping()
    print()
    
    example_configured_target()
    print()
    
    example_custom_processing()