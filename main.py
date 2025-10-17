# Use this with the "TRENDING WITH VIEWS" report I made.
# If you don't have access to that, any "Handled and Abandoned Trending" report with the  "Contact Service Queue Activity by Interval" view works as well.

import pandas as pd
import easygui
import os
from pathlib import Path

def process_call_rates():
    """Process call rate data using pandas and proper datetime parsing."""
    
    # Get input file
    input_spreadsheet = easygui.fileopenbox(
        msg='Select the input file (can be csv or xlsx). Only the first sheet of Excel files will be read.',
        default='*',
        multiple=False,
        filetypes=['*.csv', '*.xlsx']
    )
    
    if not input_spreadsheet:
        print('No input file selected.')
        return
    
    # Read the data
    try:
        if input_spreadsheet.endswith('.csv'):
            df = pd.read_csv(input_spreadsheet, encoding='utf-8-sig')
        else:  # xlsx
            df = pd.read_excel(input_spreadsheet, sheet_name=0)
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Clean the data - remove rows where first column is NaN (blank rows)
    df = df.dropna(subset=[df.columns[0]])
    
    # Parse datetime columns
    try:
        df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
        df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
    except Exception as e:
        print(f"Error parsing datetime columns: {e}")
        print("Make sure your data has 'Interval Start Time' and 'Interval End Time' columns")
        return
    
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
    
    # Get output file location
    output_csv = easygui.filesavebox(
        "Select location to save output csv.",
        title="Save Location",
        default="output.csv",
        filetypes=["*.csv"]
    )
    
    if not output_csv:
        print('No output file selected.')
        return
    
    # Save the result
    try:
        result.to_csv(output_csv)
        print(f"Successfully saved results to {output_csv}")
        print(f"Processed {len(df)} rows of data")
        print(f"Found {len(result)} unique dates and {len(result.columns)} time intervals")
    except Exception as e:
        print(f"Error saving file: {e}")

if __name__ == "__main__":
    process_call_rates()