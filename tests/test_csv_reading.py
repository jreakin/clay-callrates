"""
Tests for CSV file reading functionality.
"""

import pandas as pd
import pytest
import tempfile
import os
from pathlib import Path


def create_test_csv_file(file_path: str, encoding: str = 'utf-8'):
    """Create a test CSV file with call rates data."""
    # Sample data
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
        ['TEST QUEUE', '10/14/25 10:00:00 AM', '10/14/25 11:00:00 AM', 25, 20, 5],
    ]
    
    # Create DataFrame and save as CSV
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(file_path, index=False, encoding=encoding)


def test_csv_reading_utf8():
    """Test CSV reading with UTF-8 encoding."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as tmp:
        create_test_csv_file(tmp.name, encoding='utf-8')
        
        try:
            # Test the CSV reading logic from main.py
            df = pd.read_csv(tmp.name, encoding='utf-8-sig')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data
            assert len(df) == 4
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            assert df.iloc[0]['Calls Presented'] == 41
            assert df.iloc[3]['Calls Presented'] == 25
            
        finally:
            os.unlink(tmp.name)


def test_csv_reading_latin1_fallback():
    """Test CSV reading with Latin-1 encoding fallback."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='latin-1') as tmp:
        # Create CSV with Latin-1 encoding
        headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        data = [
            ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
            ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ]
        
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(tmp.name, index=False, encoding='latin-1')
        
        try:
            # Test the CSV reading logic with fallback from main.py
            try:
                df = pd.read_csv(tmp.name, encoding='utf-8-sig')
            except UnicodeDecodeError:
                # Fallback to latin-1 if utf-8 fails
                df = pd.read_csv(tmp.name, encoding='latin-1')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data
            assert len(df) == 2
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            assert df.iloc[0]['Calls Presented'] == 41
            
        finally:
            os.unlink(tmp.name)


def test_csv_reading_with_empty_rows():
    """Test CSV reading with empty rows that should be filtered out."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as tmp:
        # Create CSV with empty rows
        headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        data = [
            ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
            ['', '', '', '', '', ''],  # Empty row
            ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
            [None, None, None, None, None, None],  # None row
        ]
        
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(tmp.name, index=False, encoding='utf-8')
        
        try:
            # Test the CSV reading logic from main.py
            df = pd.read_csv(tmp.name, encoding='utf-8-sig')
            
            # Clean the data - remove rows where first column is NaN (blank rows)
            df_cleaned = df.dropna(subset=[df.columns[0]])
            
            # Verify that empty rows are removed
            assert len(df_cleaned) == 2  # Only 2 non-empty rows
            assert df_cleaned.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            assert df_cleaned.iloc[1]['CSQ Name'] == 'TEST QUEUE'
            
        finally:
            os.unlink(tmp.name)


def test_csv_reading_with_special_characters():
    """Test CSV reading with special characters in data."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as tmp:
        # Create CSV with special characters
        headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        data = [
            ['TEST QUEUE & SUPPORT', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
            ['TEST-QUEUE_123', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ]
        
        df = pd.DataFrame(data, columns=headers)
        df.to_csv(tmp.name, index=False, encoding='utf-8')
        
        try:
            # Test the CSV reading logic from main.py
            df = pd.read_csv(tmp.name, encoding='utf-8-sig')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data with special characters
            assert len(df) == 2
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE & SUPPORT'
            assert df.iloc[1]['CSQ Name'] == 'TEST-QUEUE_123'
            
        finally:
            os.unlink(tmp.name)


def test_csv_reading_file_not_found():
    """Test CSV reading with non-existent file."""
    non_existent_file = "non_existent_file.csv"
    
    with pytest.raises(FileNotFoundError):
        pd.read_csv(non_existent_file, encoding='utf-8-sig')


def test_csv_reading_malformed_csv():
    """Test CSV reading with malformed CSV data."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w', encoding='utf-8') as tmp:
        # Create malformed CSV (missing quotes, wrong number of columns)
        malformed_content = """CSQ Name,Interval Start Time,Interval End Time,Calls Presented
TEST QUEUE,10/14/25 8:00:00 AM,10/14/25 9:00:00 AM,41
TEST QUEUE,10/14/25 8:00:00 AM,10/14/25 9:00:00 AM,4,5,6
"""
        tmp.write(malformed_content)
        tmp.flush()
        
        try:
            # This should raise an error due to malformed CSV
            with pytest.raises((pd.errors.ParserError, ValueError)):
                pd.read_csv(tmp.name, encoding='utf-8-sig')
                
        finally:
            os.unlink(tmp.name)
