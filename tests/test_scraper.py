#!/usr/bin/env python3
"""
Unit tests for the web scraper.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.scraper import WebScraper
from src.utils import validate_url, clean_text, normalize_price
from src.storage import DataStorage


class TestWebScraper(unittest.TestCase):
    """Test cases for WebScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary config file
        self.config_data = {
            'scraper': {
                'timeout': 30,
                'max_retries': 3,
                'rate_limit': 0.1,
                'headers': {
                    'User-Agent': 'Test Agent'
                }
            },
            'targets': {
                'test_target': {
                    'base_url': 'https://example.com',
                    'selectors': {
                        'title': 'h1',
                        'content': 'p'
                    }
                }
            },
            'output': {
                'format': 'json',
                'filename': 'test_output'
            }
        }
        
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        import yaml
        yaml.dump(self.config_data, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        os.unlink(self.temp_config.name)
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = WebScraper(self.temp_config.name)
        self.assertIsNotNone(scraper.config)
        self.assertIsNotNone(scraper.session)
        scraper.close()
    
    @patch('src.scraper.requests.Session.get')
    def test_fetch_html_success(self, mock_get):
        """Test successful HTML fetching."""
        # Mock response
        mock_response = Mock()
        mock_response.text = '<html><body><h1>Test</h1></body></html>'
        mock_response.status_code = 200
        mock_response.headers = {'content-type': 'text/html'}
        mock_get.return_value = mock_response
        
        scraper = WebScraper(self.temp_config.name)
        html = scraper.fetch_html('https://example.com')
        
        self.assertIsNotNone(html)
        self.assertIn('<h1>Test</h1>', html)
        scraper.close()
    
    def test_parse_data(self):
        """Test HTML parsing."""
        html = '''
        <html>
            <body>
                <h1>Test Title</h1>
                <p>Test content paragraph 1</p>
                <p>Test content paragraph 2</p>
            </body>
        </html>
        '''
        
        selectors = {
            'title': 'h1',
            'content': 'p'
        }
        
        scraper = WebScraper(self.temp_config.name)
        data = scraper.parse_data(html, selectors)
        
        self.assertEqual(data['title'], 'Test Title')
        self.assertIsInstance(data['content'], list)
        self.assertEqual(len(data['content']), 2)
        scraper.close()


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_validate_url(self):
        """Test URL validation."""
        self.assertTrue(validate_url('https://example.com'))
        self.assertTrue(validate_url('http://example.com/path'))
        self.assertFalse(validate_url('not-a-url'))
        self.assertFalse(validate_url(''))
    
    def test_clean_text(self):
        """Test text cleaning."""
        dirty_text = "  This   is    messy   text  "
        clean = clean_text(dirty_text)
        self.assertEqual(clean, "This is messy text")
        
        self.assertEqual(clean_text(""), "")
        self.assertEqual(clean_text(None), "")
    
    def test_normalize_price(self):
        """Test price normalization."""
        self.assertEqual(normalize_price("$19.99"), 19.99)
        self.assertEqual(normalize_price("€1,234.56"), 1234.56)
        self.assertEqual(normalize_price("Price: 99"), 99.0)
        self.assertIsNone(normalize_price("No price here"))
        self.assertIsNone(normalize_price(""))


class TestDataStorage(unittest.TestCase):
    """Test cases for data storage."""
    
    def setUp(self):
        """Set up test data."""
        self.test_data = [
            {'title': 'Item 1', 'price': 19.99, 'tags': ['tag1', 'tag2']},
            {'title': 'Item 2', 'price': 29.99, 'tags': ['tag3']},
        ]
        
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_save_json(self):
        """Test JSON saving."""
        config = {'format': 'json', 'filename': 'test'}
        storage = DataStorage(config)
        
        # Change to temp directory
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            storage.save(self.test_data, 'test_output')
            
            # Check if file was created
            self.assertTrue(os.path.exists('test_output.json'))
            
            # Check content
            with open('test_output.json', 'r') as f:
                saved_data = json.load(f)
            
            self.assertEqual(len(saved_data), 2)
            self.assertEqual(saved_data[0]['title'], 'Item 1')
            
        finally:
            os.chdir(original_cwd)
    
    def test_save_csv(self):
        """Test CSV saving."""
        config = {'format': 'csv', 'filename': 'test'}
        storage = DataStorage(config)
        
        original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        try:
            storage.save(self.test_data, 'test_output')
            
            # Check if file was created
            self.assertTrue(os.path.exists('test_output.csv'))
            
            # Check content
            import csv
            with open('test_output.csv', 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
            
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]['title'], 'Item 1')
            
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()