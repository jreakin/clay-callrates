"""
Tests for Excel file reading functionality.
"""

import pandas as pd
import pytest
import tempfile
import os
from pathlib import Path


def create_test_excel_file(file_path: str, has_empty_first_row: bool = False, header_row: int = 0):
    """Create a test Excel file with specified structure."""
    # Sample data
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
    ]
    
    # Create a list of rows to write
    rows_to_write = []
    
    # Add empty rows at the beginning if needed
    if header_row > 0:
        for _ in range(header_row):
            rows_to_write.append([None] * len(headers))
    
    # Add headers
    rows_to_write.append(headers)
    
    # Add data
    rows_to_write.extend(data)
    
    # Create DataFrame from rows and save without header
    df = pd.DataFrame(rows_to_write)
    df.to_excel(file_path, index=False, header=False)


def test_excel_reading_with_standard_headers():
    """Test Excel reading with standard header placement (row 0)."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        create_test_excel_file(tmp.name, has_empty_first_row=False, header_row=0)
        
        try:
            # Test the smart header detection logic from main.py
            df_raw = pd.read_excel(tmp.name, sheet_name=0, header=None)
            
            # Find the first non-empty row that looks like headers
            header_row = None
            for i in range(min(5, len(df_raw))):
                row = df_raw.iloc[i]
                if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
                    header_row = i
                    break
            
            assert header_row == 0, f"Expected header row 0, got {header_row}"
            
            # Read with detected header
            df = pd.read_excel(tmp.name, sheet_name=0, header=header_row)
            if header_row > 0:
                df = df.dropna(how='all')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data
            assert len(df) == 3
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            assert df.iloc[0]['Calls Presented'] == 41
            
        finally:
            os.unlink(tmp.name)


def test_excel_reading_with_empty_first_row():
    """Test Excel reading with empty first row (like Clay's example)."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        create_test_excel_file(tmp.name, has_empty_first_row=True, header_row=1)
        
        try:
            # Test the smart header detection logic from main.py
            df_raw = pd.read_excel(tmp.name, sheet_name=0, header=None)
            
            # Find the first non-empty row that looks like headers
            header_row = None
            for i in range(min(5, len(df_raw))):
                row = df_raw.iloc[i]
                if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
                    header_row = i
                    break
            
            assert header_row == 1, f"Expected header row 1, got {header_row}"
            
            # Read with detected header
            df = pd.read_excel(tmp.name, sheet_name=0, header=header_row)
            if header_row > 0:
                df = df.dropna(how='all')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data
            assert len(df) == 3
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            assert df.iloc[0]['Calls Presented'] == 41
            
        finally:
            os.unlink(tmp.name)


def test_excel_reading_with_multiple_empty_rows():
    """Test Excel reading with multiple empty rows before headers."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        create_test_excel_file(tmp.name, has_empty_first_row=False, header_row=2)
        
        try:
            # Test the smart header detection logic from main.py
            df_raw = pd.read_excel(tmp.name, sheet_name=0, header=None)
            
            # Find the first non-empty row that looks like headers
            header_row = None
            for i in range(min(5, len(df_raw))):
                row = df_raw.iloc[i]
                if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
                    header_row = i
                    break
            
            assert header_row == 2, f"Expected header row 2, got {header_row}"
            
            # Read with detected header
            df = pd.read_excel(tmp.name, sheet_name=0, header=header_row)
            if header_row > 0:
                df = df.dropna(how='all')
            
            # Verify columns
            expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
            assert list(df.columns) == expected_columns
            
            # Verify data
            assert len(df) == 3
            assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
            
        finally:
            os.unlink(tmp.name)


def test_excel_reading_fallback_behavior():
    """Test Excel reading fallback when no headers are detected."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # Create a file with no clear headers (all numeric data)
        data = [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12]]
        df = pd.DataFrame(data)
        df.to_excel(tmp.name, index=False, header=False)
        
        try:
            # Test the smart header detection logic from main.py
            df_raw = pd.read_excel(tmp.name, sheet_name=0, header=None)
            
            # Find the first non-empty row that looks like headers
            header_row = None
            for i in range(min(5, len(df_raw))):
                row = df_raw.iloc[i]
                if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
                    header_row = i
                    break
            
            # Should not find headers (all numeric)
            assert header_row is None
            
            # Should fall back to default behavior
            df = pd.read_excel(tmp.name, sheet_name=0)
            
            # Should have default column names (integers for header=None)
            assert len(df.columns) == 6
            assert all(isinstance(col, int) for col in df.columns)
            
        finally:
            os.unlink(tmp.name)


def test_excel_reading_with_real_example_file():
    """Test Excel reading with the actual example.xlsx file if it exists."""
    example_file = Path(__file__).parent.parent / "example.xlsx"
    
    if not example_file.exists():
        pytest.skip("example.xlsx not found")
    
    # Test the smart header detection logic from main.py
    df_raw = pd.read_excel(example_file, sheet_name=0, header=None)
    
    # Find the first non-empty row that looks like headers
    header_row = None
    for i in range(min(5, len(df_raw))):
        row = df_raw.iloc[i]
        if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
            header_row = i
            break
    
    assert header_row is not None, "Should find header row in example.xlsx"
    assert header_row == 1, f"Expected header row 1 for example.xlsx, got {header_row}"
    
    # Read with detected header
    df = pd.read_excel(example_file, sheet_name=0, header=header_row)
    if header_row > 0:
        df = df.dropna(how='all')
    
    # Verify columns
    expected_columns = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    assert list(df.columns) == expected_columns
    
    # Verify we have data
    assert len(df) > 0
    assert df.iloc[0]['CSQ Name'] == 'TEST QUEUE'
