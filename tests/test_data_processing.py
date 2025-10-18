"""
Tests for call rates data processing functionality.
"""

import pandas as pd
import pytest
from datetime import datetime, date, time


def create_sample_dataframe():
    """Create a sample DataFrame for testing."""
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 41, 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 4, 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 18, 13, 5],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', 12, 10, 2],
        ['TEST QUEUE', '10/14/25 10:00:00 AM', '10/14/25 11:00:00 AM', 25, 20, 5],
        ['TEST QUEUE', '10/15/25 8:00:00 AM', '10/15/25 9:00:00 AM', 30, 28, 2],
        ['TEST QUEUE', '10/15/25 8:00:00 AM', '10/15/25 9:00:00 AM', 15, 12, 3],
    ]
    
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    return pd.DataFrame(data, columns=headers)


def test_datetime_parsing():
    """Test datetime parsing functionality."""
    df = create_sample_dataframe()
    
    # Test the datetime parsing logic from main.py
    try:
        df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
        df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    except Exception as e:
        pytest.fail(f"Error parsing datetime columns: {e}")
    
    # Verify datetime columns were created
    assert 'start_datetime' in df.columns
    assert 'end_datetime' in df.columns
    
    # Verify datetime parsing worked
    assert df['start_datetime'].dtype == 'datetime64[ns]'
    assert df['end_datetime'].dtype == 'datetime64[ns]'
    
    # Verify specific datetime values
    first_start = df['start_datetime'].iloc[0]
    assert first_start.year == 2025
    assert first_start.month == 10
    assert first_start.day == 14
    assert first_start.hour == 8


def test_date_time_extraction():
    """Test date and time component extraction."""
    df = create_sample_dataframe()
    
    # Parse datetime first
    df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
    df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    
    # Test the date/time extraction logic from main.py
    df['date'] = df['start_datetime'].dt.date
    df['time'] = df['start_datetime'].dt.time
    df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
    
    # Verify date extraction
    assert 'date' in df.columns
    assert df['date'].dtype == 'object'  # date objects
    assert df['date'].iloc[0] == date(2025, 10, 14)
    assert df['date'].iloc[5] == date(2025, 10, 15)
    
    # Verify time extraction
    assert 'time' in df.columns
    assert df['time'].dtype == 'object'  # time objects
    assert df['time'].iloc[0] == time(8, 0, 0)
    assert df['time'].iloc[2] == time(9, 0, 0)
    
    # Verify time string formatting
    assert 'time_str' in df.columns
    assert df['time_str'].iloc[0] == '08:00:00 AM'
    assert df['time_str'].iloc[2] == '09:00:00 AM'


def test_calls_numeric_conversion():
    """Test conversion of calls data to numeric."""
    df = create_sample_dataframe()
    
    # Test the numeric conversion logic from main.py
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Verify calls column was created
    assert 'calls' in df.columns
    assert df['calls'].dtype == 'int64'
    
    # Verify numeric values
    assert df['calls'].iloc[0] == 41
    assert df['calls'].iloc[1] == 4
    assert df['calls'].iloc[2] == 18


def test_calls_numeric_conversion_with_non_numeric():
    """Test conversion of calls data with non-numeric values."""
    # Create DataFrame with non-numeric values
    data = [
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', '41', 39, 2],
        ['TEST QUEUE', '10/14/25 8:00:00 AM', '10/14/25 9:00:00 AM', 'invalid', 4, 0],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', '', 13, 5],
        ['TEST QUEUE', '10/14/25 9:00:00 AM', '10/14/25 10:00:00 AM', None, 10, 2],
    ]
    
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    df = pd.DataFrame(data, columns=headers)
    
    # Test the numeric conversion logic from main.py
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Verify conversion results
    assert df['calls'].iloc[0] == 41  # Valid string number
    assert df['calls'].iloc[1] == 0   # Invalid string -> 0
    assert df['calls'].iloc[2] == 0   # Empty string -> 0
    assert df['calls'].iloc[3] == 0   # None -> 0


def test_data_grouping_and_aggregation():
    """Test the core grouping and aggregation logic."""
    df = create_sample_dataframe()
    
    # Parse datetime and extract components
    df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
    df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    df['date'] = df['start_datetime'].dt.date
    df['time'] = df['start_datetime'].dt.time
    df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Test the grouping logic from main.py
    result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
    
    # Verify result structure
    assert isinstance(result, pd.DataFrame)
    assert len(result.index) == 2  # Two unique dates
    assert len(result.columns) == 3  # Three unique time intervals
    
    # Verify aggregation worked correctly
    # 10/14/25 8:00:00 AM should have 41 + 4 = 45 calls
    assert result.loc[date(2025, 10, 14), '08:00:00 AM'] == 45
    
    # 10/14/25 9:00:00 AM should have 18 + 12 = 30 calls
    assert result.loc[date(2025, 10, 14), '09:00:00 AM'] == 30
    
    # 10/14/25 10:00:00 AM should have 25 calls
    assert result.loc[date(2025, 10, 14), '10:00:00 AM'] == 25
    
    # 10/15/25 8:00:00 AM should have 30 + 15 = 45 calls
    assert result.loc[date(2025, 10, 15), '08:00:00 AM'] == 45


def test_time_column_sorting():
    """Test chronological sorting of time columns."""
    df = create_sample_dataframe()
    
    # Parse datetime and extract components
    df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
    df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    df['date'] = df['start_datetime'].dt.date
    df['time'] = df['start_datetime'].dt.time
    df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Group and aggregate
    result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
    
    # Test the time sorting logic from main.py
    time_columns = sorted(result.columns, key=lambda x: pd.to_datetime(x, format='%I:%M:%S %p').time())
    result_sorted = result[time_columns]
    
    # Verify time columns are in chronological order
    expected_order = ['08:00:00 AM', '09:00:00 AM', '10:00:00 AM']
    assert list(result_sorted.columns) == expected_order


def test_date_sorting():
    """Test sorting by date."""
    df = create_sample_dataframe()
    
    # Parse datetime and extract components
    df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
    df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    df['date'] = df['start_datetime'].dt.date
    df['time'] = df['start_datetime'].dt.time
    df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
    df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
    
    # Group and aggregate
    result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
    
    # Sort by time
    time_columns = sorted(result.columns, key=lambda x: pd.to_datetime(x, format='%I:%M:%S %p').time())
    result = result[time_columns]
    
    # Test the date sorting logic from main.py
    result = result.sort_index()
    
    # Verify dates are in chronological order
    dates = list(result.index)
    assert dates[0] == date(2025, 10, 14)
    assert dates[1] == date(2025, 10, 15)


def test_empty_dataframe_handling():
    """Test handling of empty DataFrame."""
    # Create empty DataFrame with correct columns
    headers = ['CSQ Name', 'Interval Start Time', 'Interval End Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    df = pd.DataFrame(columns=headers)
    
    # Test that processing doesn't crash with empty data
    try:
        df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
        df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
        df['date'] = df['start_datetime'].dt.date
        df['time'] = df['start_datetime'].dt.time
        df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
        df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
        
        result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
        
        # Should return empty DataFrame
        assert len(result) == 0
        
    except Exception as e:
        pytest.fail(f"Empty DataFrame processing failed: {e}")


def test_missing_required_columns():
    """Test handling of missing required columns."""
    # Create DataFrame with missing required columns
    data = [['TEST QUEUE', '10/14/25 8:00:00 AM', 41, 39, 2]]
    headers = ['CSQ Name', 'Interval Start Time', 'Calls Presented', 'Calls Handled', 'Calls Abandoned']
    df = pd.DataFrame(data, columns=headers)
    
    # Test that missing columns raise appropriate error
    with pytest.raises(KeyError):
        df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
        df['end_datetime'] = pd.to_datetime(df['Interval End Time'])  # This should fail
