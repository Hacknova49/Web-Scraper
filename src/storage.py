"""
Data storage module for different output formats.
"""

import json
import csv
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging


class DataStorage:
    """Handle data storage in various formats."""
    
    def __init__(self, config: Dict):
        """
        Initialize storage with configuration.
        
        Args:
            config: Storage configuration
        """
        self.config = config
        self.logger = logging.getLogger('WebScraper.Storage')
        
    def save(self, data: List[Dict[str, Any]], filename: Optional[str] = None):
        """
        Save data in the configured format.
        
        Args:
            data: List of data dictionaries to save
            filename: Optional custom filename
        """
        if not data:
            self.logger.warning("No data to save")
            return
        
        # Generate filename
        if not filename:
            base_filename = self.config.get('filename', 'scraped_data')
            if self.config.get('include_timestamp', True):
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{base_filename}_{timestamp}"
            else:
                filename = base_filename
        
        # Save in specified format
        output_format = self.config.get('format', 'csv').lower()
        
        if output_format == 'csv':
            self._save_csv(data, filename)
        elif output_format == 'json':
            self._save_json(data, filename)
        elif output_format == 'xlsx':
            self._save_xlsx(data, filename)
        else:
            self.logger.error(f"Unsupported output format: {output_format}")
            
    def _save_csv(self, data: List[Dict[str, Any]], filename: str):
        """Save data as CSV file."""
        try:
            filepath = f"{filename}.csv"
            
            # Get all unique keys from all dictionaries
            all_keys = set()
            for item in data:
                all_keys.update(item.keys())
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=sorted(all_keys))
                writer.writeheader()
                
                for item in data:
                    # Handle list values by converting to string
                    processed_item = {}
                    for key, value in item.items():
                        if isinstance(value, list):
                            processed_item[key] = '; '.join(map(str, value))
                        else:
                            processed_item[key] = value
                    writer.writerow(processed_item)
            
            self.logger.info(f"Data saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving CSV: {e}")
    
    def _save_json(self, data: List[Dict[str, Any]], filename: str):
        """Save data as JSON file."""
        try:
            filepath = f"{filename}.json"
            
            with open(filepath, 'w', encoding='utf-8') as jsonfile:
                json.dump(data, jsonfile, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Data saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving JSON: {e}")
    
    def _save_xlsx(self, data: List[Dict[str, Any]], filename: str):
        """Save data as Excel file."""
        try:
            filepath = f"{filename}.xlsx"
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Handle list columns by converting to string
            for col in df.columns:
                if df[col].dtype == 'object':
                    df[col] = df[col].apply(
                        lambda x: '; '.join(map(str, x)) if isinstance(x, list) else x
                    )
            
            # Save to Excel
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Scraped Data')
            
            self.logger.info(f"Data saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving Excel: {e}")
    
    def save_multiple_sheets(self, data_dict: Dict[str, List[Dict[str, Any]]], filename: str):
        """
        Save multiple datasets to different sheets in Excel.
        
        Args:
            data_dict: Dictionary with sheet names as keys and data as values
            filename: Output filename
        """
        try:
            filepath = f"{filename}.xlsx"
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                for sheet_name, data in data_dict.items():
                    if data:
                        df = pd.DataFrame(data)
                        
                        # Handle list columns
                        for col in df.columns:
                            if df[col].dtype == 'object':
                                df[col] = df[col].apply(
                                    lambda x: '; '.join(map(str, x)) if isinstance(x, list) else x
                                )
                        
                        df.to_excel(writer, index=False, sheet_name=sheet_name)
            
            self.logger.info(f"Multi-sheet data saved to {filepath}")
            
        except Exception as e:
            self.logger.error(f"Error saving multi-sheet Excel: {e}")