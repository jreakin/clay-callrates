"""
Integration tests for the complete call rates processing workflow.
"""

import pandas as pd
import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock


def create_test_excel_file(file_path: str):
    """Create a test Excel file with the same structure as Clay's example."""
    # Sample data matching Clay's example structure
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 12, 10, 2],
        ['TEST QUEUE', '10/14/25 10:00:00 AM', '10/14/25 11:00:00 AM', 25, 20, 5],
        ['TEST QUEUE', '10/14/25 11:00:00 AM', '10/14/25 12:00:00 PM', 30, 28, 2],
        ['TEST QUEUE', '10/14/25 12:00:00 PM', '10/14/25 1:00:00 PM', 15, 12, 3],
    ]
    
    # Create a list of rows to write (like Clay's example with empty first row)
    rows_to_write = []
    
    # Add empty first row (like Clay's example)
    rows_to_write.append([None] * len(headers))
    
    # Add headers
    rows_to_write.append(headers)
    
    # Add data
    rows_to_write.extend(data)
    
    # Create DataFrame from rows and save without header
    df = pd.DataFrame(rows_to_write)
    df.to_excel(file_path, index=False, header=False)


def create_test_csv_file(file_path: str):
    """Create a test CSV file."""
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
    ]
    
    df = pd.DataFrame(data, columns=headers)
    df.to_csv(file_path, index=False, encoding='utf-8')


def process_call_rates_logic(input_file: str):
    """Extract the core processing logic from main.py for testing."""
    # Read the data
    if input_file.endswith('.csv'):
        df = pd.read_csv(input_file, encoding='utf-8-sig')
    else:  # xlsx
        # Smart header detection for Excel files
        df_raw = pd.read_excel(input_file, sheet_name=0, header=None)
        
        # Find the first non-empty row that looks like headers
        header_row = None
        for i in range(min(5, len(df_raw))):  # Check first 5 rows
            row = df_raw.iloc[i]
            # Check if this row contains text that looks like column headers
            if row.notna().any() and any(isinstance(val, str) and ' ' in val for val in row if pd.notna(val)):
                header_row = i
                break
        
        if header_row is not None:
            # Use the identified header row
            df = pd.read_excel(input_file, sheet_name=0, header=header_row)
            # Remove any rows above the header that might be empty
            if header_row > 0:
                df = df.dropna(how='all')  # Remove completely empty rows
        else:
            # Fallback to default behavior
            df = pd.read_excel(input_file, sheet_name=0)
    
    # Clean the data - remove rows where first column is NaN (blank rows)
    df = df.dropna(subset=[df.columns[0]])
    
    # Parse datetime columns
    df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
    df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    
    # Extract date and time components
    df['date'] = df['start_datetime'].dt.date
    df['time'] = df['start_datetime'].dt.time
    df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
    
    # Convert calls to numeric, handling any non-numeric values
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Group by date and time, sum the calls
    result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
    
    # Sort by time (chronological order)
    time_columns = sorted(result.columns, key=lambda x: pd.to_datetime(x, format='%I:%M:%S %p').time())
    result = result[time_columns]
    
    # Sort by date
    result = result.sort_index()
    
    return result


def test_excel_integration_workflow():
    """Test complete Excel processing workflow."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        create_test_excel_file(tmp.name)
        
        try:
            # Process the file
            result = process_call_rates_logic(tmp.name)
            
            # Verify result structure
            assert isinstance(result, pd.DataFrame)
            assert len(result.index) == 1  # One date
            assert len(result.columns) == 5  # Five time intervals
            
            # Verify time columns are in chronological order
            expected_times = ['08:00:00 AM', '09:00:00 AM', '10:00:00 AM', '11:00:00 AM', '12:00:00 PM']
            assert list(result.columns) == expected_times
            
            # Verify aggregation worked correctly
            # 8:00 AM should have 41 + 4 = 45 calls
            assert result.iloc[0]['08:00:00 AM'] == 45
            
            # 9:00 AM should have 18 + 12 = 30 calls
            assert result.iloc[0]['09:00:00 AM'] == 30
            
            # 10:00 AM should have 25 calls
            assert result.iloc[0]['10:00:00 AM'] == 25
            
            # 11:00 AM should have 30 calls
            assert result.iloc[0]['11:00:00 AM'] == 30
            
            # 12:00 PM should have 15 calls
            assert result.iloc[0]['12:00:00 PM'] == 15
            
        finally:
            os.unlink(tmp.name)


def test_csv_integration_workflow():
    """Test complete CSV processing workflow."""
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as tmp:
        create_test_csv_file(tmp.name)
        
        try:
            # Process the file
            result = process_call_rates_logic(tmp.name)
            
            # Verify result structure
            assert isinstance(result, pd.DataFrame)
            assert len(result.index) == 1  # One date
            assert len(result.columns) == 2  # Two time intervals
            
            # Verify time columns are in chronological order
            expected_times = ['08:00:00 AM', '09:00:00 AM']
            assert list(result.columns) == expected_times
            
            # Verify aggregation worked correctly
            # 8:00 AM should have 41 + 4 = 45 calls
            assert result.iloc[0]['08:00:00 AM'] == 45
            
            # 9:00 AM should have 18 calls
            assert result.iloc[0]['09:00:00 AM'] == 18
            
        finally:
            os.unlink(tmp.name)


def test_multiple_dates_integration():
    """Test processing data with multiple dates."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # Create data with multiple dates
        headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        data = [
            ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
            ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
            ['TEST QUEUE', '10/15/25 8:00:00 AM', '10/15/25 9:00:00 AM', 30, 28, 2],
            ['TEST QUEUE', '10/15/25 9:00:00 AM', '10/15/25 10:00:00 AM', 25, 20, 5],
        ]
        
        # Create a list of rows to write
        rows_to_write = []
        
        # Add empty first row
        rows_to_write.append([None] * len(headers))
        
        # Add headers
        rows_to_write.append(headers)
        
        # Add data
        rows_to_write.extend(data)
        
        # Create DataFrame from rows and save without header
        df = pd.DataFrame(rows_to_write)
        df.to_excel(tmp.name, index=False, header=False)
        
        try:
            # Process the file
            result = process_call_rates_logic(tmp.name)
            
            # Verify result structure
            assert isinstance(result, pd.DataFrame)
            assert len(result.index) == 2  # Two dates
            assert len(result.columns) == 2  # Two time intervals
            
            # Verify dates are in chronological order
            dates = list(result.index)
            assert dates[0] == pd.Timestamp('2025-10-14').date()
            assert dates[1] == pd.Timestamp('2025-10-15').date()
            
            # Verify data for each date
            assert result.iloc[0]['08:00:00 AM'] == 41  # 10/14
            assert result.iloc[0]['09:00:00 AM'] == 18  # 10/14
            assert result.iloc[1]['08:00:00 AM'] == 30  # 10/15
            assert result.iloc[1]['09:00:00 AM'] == 25  # 10/15
            
        finally:
            os.unlink(tmp.name)


def test_output_csv_format():
    """Test that the output can be saved as CSV in the expected format."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as input_file:
        create_test_excel_file(input_file.name)
        
        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as output_file:
            try:
                # Process the file
                result = process_call_rates_logic(input_file.name)
                
                # Save as CSV
                result.to_csv(output_file.name)
                
                # Read back and verify
                saved_result = pd.read_csv(output_file.name, index_col=0)
                
                # Verify structure is preserved
                assert len(saved_result) == len(result)
                assert len(saved_result.columns) == len(result.columns)
                
                # Verify data is preserved
                assert saved_result.iloc[0]['08:00:00 AM'] == result.iloc[0]['08:00:00 AM']
                
            finally:
                os.unlink(input_file.name)
                os.unlink(output_file.name)


def test_error_handling_missing_columns():
    """Test error handling for files with missing required columns."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # Create file with missing columns
        data = [['TEST QUEUE', '10/14/25 8:00:00 AM', 41, 39, 2]]
        headers = ['CSQ Name', 'Interval Start Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        df = pd.DataFrame(data, columns=headers)
        empty_row = pd.DataFrame([[None] * len(headers)], columns=headers)
        df_with_empty = pd.concat([empty_row, df], ignore_index=True)
        df_with_empty.to_excel(tmp.name, index=False, header=False)
        
        try:
            # This should raise a KeyError for missing 'Interval End Time'
            with pytest.raises(KeyError):
                process_call_rates_logic(tmp.name)
                
        finally:
            os.unlink(tmp.name)


def test_error_handling_invalid_datetime():
    """Test error handling for invalid datetime formats."""
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        # Create file with invalid datetime
        data = [['TEST QUEUE', 'invalid datetime', '10/14/25 9:00:00 AM', 41, 39, 2]]
        headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
        
        # Create a list of rows to write
        rows_to_write = []
        
        # Add empty first row
        rows_to_write.append([None] * len(headers))
        
        # Add headers
        rows_to_write.append(headers)
        
        # Add data
        rows_to_write.extend(data)
        
        # Create DataFrame from rows and save without header
        df = pd.DataFrame(rows_to_write)
        df.to_excel(tmp.name, index=False, header=False)
        
        try:
            # This should raise an error for invalid datetime
            with pytest.raises((pd.errors.ParserError, ValueError)):
                process_call_rates_logic(tmp.name)
                
        finally:
            os.unlink(tmp.name)


def test_real_example_file_integration():
    """Test integration with the actual example.xlsx file if it exists."""
    example_file = Path(__file__).parent.parent / "example.xlsx"
    
    if not example_file.exists():
        pytest.skip("example.xlsx not found")
    
    try:
        # Process the real example file
        result = process_call_rates_logic(str(example_file))
        
        # Verify result structure
        assert isinstance(result, pd.DataFrame)
        assert len(result.index) > 0  # Should have at least one date
        assert len(result.columns) > 0  # Should have at least one time interval
        
        # Verify time columns are in chronological order
        time_columns = list(result.columns)
        for i in range(len(time_columns) - 1):
            current_time = pd.to_datetime(time_columns[i], format='%I:%M:%S %p').time()
            next_time = pd.to_datetime(time_columns[i + 1], format='%I:%M:%S %p').time()
            assert current_time <= next_time, f"Time columns not in chronological order: {time_columns[i]} > {time_columns[i + 1]}"
        
        # Verify we have reasonable data
        assert result.sum().sum() > 0  # Should have some calls
        
    except Exception as e:
        pytest.fail(f"Integration test with real example file failed: {e}")
