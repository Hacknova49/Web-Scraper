#!/usr/bin/env python3
"""
Main entry point for the web scraper application.
"""

import argparse
import sys
from typing import Dict, List
from src.scraper import WebScraper


def main():
    """Main function to run the web scraper."""
    parser = argparse.ArgumentParser(description='Comprehensive Web Scraper')
    parser.add_argument('--config', default='config.yaml', help='Configuration file path')
    parser.add_argument('--target', help='Target name from configuration to scrape')
    parser.add_argument('--url', help='Custom URL to scrape')
    parser.add_argument('--selectors', help='JSON string of CSS selectors for custom URL')
    parser.add_argument('--async', action='store_true', help='Use async scraping for multiple URLs')
    parser.add_argument('--urls-file', help='File containing URLs to scrape (one per line)')
    parser.add_argument('--output', help='Output filename (without extension)')
    
    args = parser.parse_args()
    
    try:
        # Initialize scraper
        scraper = WebScraper(args.config)
        
        if args.target:
            # Scrape configured target
            data = scraper.scrape_target(args.target)
            if data:
                scraper.save_data(data, args.output)
            else:
                print(f"No data scraped for target: {args.target}")
                
        elif args.url and args.selectors:
            # Scrape custom URL
            import json
            try:
                selectors = json.loads(args.selectors)
                data = scraper.scrape_custom_url(args.url, selectors)
                if data:
                    scraper.save_data([data], args.output)
                else:
                    print(f"No data scraped from URL: {args.url}")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format for selectors")
                sys.exit(1)
                
        elif args.urls_file and args.selectors:
            # Scrape multiple URLs from file
            import json
            try:
                selectors = json.loads(args.selectors)
                
                # Read URLs from file
                with open(args.urls_file, 'r') as f:
                    urls = [line.strip() for line in f if line.strip()]
                
                if args.async:
                    # Use async scraping
                    data = scraper.run_async_scrape(urls, selectors)
                else:
                    # Use synchronous scraping
                    data = []
                    for url in urls:
                        result = scraper.scrape_custom_url(url, selectors)
                        if result:
                            data.append(result)
                
                if data:
                    scraper.save_data(data, args.output)
                    print(f"Scraped {len(data)} URLs successfully")
                else:
                    print("No data scraped from URLs")
                    
            except json.JSONDecodeError:
                print("Error: Invalid JSON format for selectors")
                sys.exit(1)
            except FileNotFoundError:
                print(f"Error: URLs file not found: {args.urls_file}")
                sys.exit(1)
                
        else:
            # Interactive mode
            run_interactive_mode(scraper)
            
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'scraper' in locals():
            scraper.close()


def run_interactive_mode(scraper: WebScraper):
    """Run scraper in interactive mode."""
    print("=== Web Scraper Interactive Mode ===")
    print("Available targets:")
    
    targets = scraper.config.get('targets', {})
    if targets:
        for i, target_name in enumerate(targets.keys(), 1):
            print(f"{i}. {target_name}")
        
        print(f"{len(targets) + 1}. Custom URL")
        print("0. Exit")
        
        while True:
            try:
                choice = input("\nSelect an option: ").strip()
                
                if choice == '0':
                    break
                elif choice.isdigit():
                    choice_num = int(choice)
                    target_names = list(targets.keys())
                    
                    if 1 <= choice_num <= len(target_names):
                        # Scrape selected target
                        target_name = target_names[choice_num - 1]
                        print(f"\nScraping target: {target_name}")
                        data = scraper.scrape_target(target_name)
                        
                        if data:
                            scraper.save_data(data)
                            print(f"Successfully scraped {len(data)} items")
                        else:
                            print("No data scraped")
                            
                    elif choice_num == len(target_names) + 1:
                        # Custom URL scraping
                        url = input("Enter URL to scrape: ").strip()
                        if url:
                            print("Enter CSS selectors (format: field_name:selector)")
                            print("Example: title:h1, price:.price, description:p.desc")
                            selectors_input = input("Selectors: ").strip()
                            
                            if selectors_input:
                                # Parse selectors
                                selectors = {}
                                for pair in selectors_input.split(','):
                                    if ':' in pair:
                                        key, value = pair.split(':', 1)
                                        selectors[key.strip()] = value.strip()
                                
                                if selectors:
                                    data = scraper.scrape_custom_url(url, selectors)
                                    if data:
                                        scraper.save_data([data])
                                        print("Successfully scraped custom URL")
                                    else:
                                        print("No data scraped from custom URL")
                                else:
                                    print("No valid selectors provided")
                            else:
                                print("No selectors provided")
                        else:
                            print("No URL provided")
                    else:
                        print("Invalid choice")
                else:
                    print("Invalid input")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")
    else:
        print("No targets configured. Please add targets to config.yaml")


if __name__ == "__main__":
    main()