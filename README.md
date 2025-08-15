# Comprehensive Web Scraper

A robust, scalable web scraper with comprehensive error handling, multiple output formats, and both synchronous and asynchronous scraping capabilities.

## Features

### Core Functionality
- **HTTP Requests**: Robust request handling with retries and timeouts
- **HTML Parsing**: BeautifulSoup with CSS selectors and XPath support
- **Error Handling**: Comprehensive error handling and logging
- **Rate Limiting**: Configurable delays between requests
- **Pagination Support**: Automatic pagination handling
- **Multiple Output Formats**: CSV, JSON, and Excel support

### Advanced Features
- **Async Scraping**: High-performance concurrent scraping
- **Robots.txt Compliance**: Automatic robots.txt checking
- **User-Agent Rotation**: Fake user agent generation
- **Proxy Support**: Ready for proxy integration
- **Configuration-Driven**: YAML-based configuration
- **Modular Architecture**: Clean, maintainable code structure

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd web-scraper
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

Edit `config.yaml` to configure your scraping targets:

```yaml
scraper:
  timeout: 30
  max_retries: 3
  rate_limit: 1  # seconds between requests

targets:
  my_target:
    base_url: "https://example.com"
    selectors:
      title: "h1.title"
      content: "div.content"
    pagination:
      enabled: true
      next_button: "a.next"
      max_pages: 10
```

## Usage

### Command Line Interface

#### Scrape a configured target:
```bash
python main.py --target my_target
```

#### Scrape a custom URL:
```bash
python main.py --url "https://example.com" --selectors '{"title": "h1", "price": ".price"}'
```

#### Async scraping from URL file:
```bash
python main.py --urls-file urls.txt --selectors '{"title": "h1"}' --async
```

#### Interactive mode:
```bash
python main.py
```

### Python API

```python
from src.scraper import WebScraper

# Initialize scraper
scraper = WebScraper('config.yaml')

# Scrape a configured target
data = scraper.scrape_target('my_target')

# Scrape custom URL
selectors = {'title': 'h1', 'price': '.price'}
data = scraper.scrape_custom_url('https://example.com', selectors)

# Async scraping
urls = ['https://example1.com', 'https://example2.com']
data = scraper.run_async_scrape(urls, selectors)

# Save data
scraper.save_data(data, 'my_output')
scraper.close()
```

## Output Formats

### CSV
```bash
# Configure in config.yaml
output:
  format: "csv"
  filename: "scraped_data"
  include_timestamp: true
```

### JSON
```bash
output:
  format: "json"
  filename: "scraped_data"
```

### Excel
```bash
output:
  format: "xlsx"
  filename: "scraped_data"
```

## Error Handling

The scraper includes comprehensive error handling:

- **Request Failures**: Automatic retries with exponential backoff
- **Parsing Errors**: Graceful handling of missing elements
- **Network Issues**: Timeout handling and connection error recovery
- **Data Validation**: URL validation and content type checking
- **Logging**: Detailed logging to file and console

## Rate Limiting & Ethics

- **Configurable Delays**: Set delays between requests
- **Robots.txt Compliance**: Automatic robots.txt checking
- **User-Agent Rotation**: Avoid detection with rotating user agents
- **Respectful Scraping**: Built-in safeguards for ethical scraping

## Advanced Features

### Async Scraping
For high-performance scraping of multiple URLs:

```python
# Scrape 100 URLs concurrently
urls = ['https://example.com/page{}'.format(i) for i in range(1, 101)]
data = scraper.run_async_scrape(urls, selectors)
```

### Custom Data Processing
Extend the scraper with custom processing:

```python
class CustomScraper(WebScraper):
    def custom_parse_data(self, html, selectors):
        data = super().parse_data(html, selectors)
        # Add custom processing
        data['processed_at'] = time.time()
        return data
```

### Pagination Handling
Automatic pagination support:

```yaml
pagination:
  enabled: true
  next_button: "a.next-page"
  max_pages: 50
```

## Logging

Logs are written to `scraper.log` and console:

```
2024-01-15 10:30:15 - WebScraper - INFO - Fetching: https://example.com
2024-01-15 10:30:16 - WebScraper - INFO - Successfully scraped 25 items
```

## Project Structure

```
web-scraper/
├── src/
│   ├── __init__.py
│   ├── scraper.py          # Main scraper class
│   ├── async_scraper.py    # Async scraping functionality
│   ├── storage.py          # Data storage handlers
│   └── utils.py            # Utility functions
├── config.yaml             # Configuration file
├── main.py                 # CLI entry point
├── requirements.txt        # Dependencies
└── README.md              # This file
```

## Legal & Ethical Considerations

- **Respect robots.txt**: The scraper automatically checks robots.txt
- **Rate Limiting**: Always use appropriate delays between requests
- **Terms of Service**: Review website terms before scraping
- **Copyright**: Respect intellectual property rights
- **Personal Data**: Handle personal data according to privacy laws

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
1. Check the logs in `scraper.log`
2. Review the configuration in `config.yaml`
3. Open an issue on GitHub

## Examples

### E-commerce Scraping
```yaml
targets:
  ecommerce:
    base_url: "https://shop.example.com/products"
    selectors:
      name: "h2.product-name"
      price: "span.price"
      rating: "div.rating"
      availability: "span.stock"
```

### News Scraping
```yaml
targets:
  news:
    base_url: "https://news.example.com"
    selectors:
      headline: "h1.headline"
      author: "span.author"
      date: "time.publish-date"
      content: "div.article-body"
```

### Job Listings
```yaml
targets:
  jobs:
    base_url: "https://jobs.example.com"
    selectors:
      title: "h3.job-title"
      company: "span.company-name"
      location: "span.location"
      salary: "span.salary"
```