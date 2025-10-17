# Demo version showing the pandas refactoring improvements
# This demonstrates the same functionality without GUI dependencies

import pandas as pd
import os
from pathlib import Path

def demo_call_rates():
    """Demo version showing the improved pandas processing."""
    
    print("=" * 60)
    print("CALLRATES PANDAS REFACTORING DEMO")
    print("=" * 60)
    print()
    
    # Use the example file
    input_file = "example.xlsx"
    print(f"📁 Processing file: {input_file}")
    print()
    
    # Read the data
    try:
        df = pd.read_excel(input_file)
        print(f"📊 Successfully loaded {len(df)} rows of data")
        print(f"   Raw columns: {list(df.columns)}")
        print()
        
        # The Excel file has headers in the first row, let's fix this
        if 'Unnamed: 0' in df.columns:
            # Use the first row as column names
            df.columns = df.iloc[0]
            df = df.drop(df.index[0]).reset_index(drop=True)
            print(f"   Fixed columns: {list(df.columns)}")
            print()
        
        # Show sample data
        print("📋 SAMPLE DATA (first 3 rows):")
        print(df.head(3).to_string(index=False))
        print()
        
        # Parse datetime columns using pandas (NEW APPROACH)
        print("🔄 PANDAS DATETIME PARSING:")
        print("   Before: Manual string splitting (fragile)")
        print("   After:  pd.to_datetime() (robust)")
        print()
        
        df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
        df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
        df['date'] = df['start_datetime'].dt.date
        df['time_str'] = df['start_datetime'].dt.strftime('%I:%M:%S %p')
        df['calls'] = pd.to_numeric(df['Calls Presented'], errors='coerce').fillna(0).astype(int)
        
        # Group and aggregate using pandas (NEW APPROACH)
        print("📊 PANDAS GROUPBY OPERATIONS:")
        print("   Before: Manual dictionary building with nested loops")
        print("   After:  df.groupby().sum().unstack() (automatic)")
        print()
        
        result = df.groupby(['date', 'time_str'])['calls'].sum().unstack(fill_value=0)
        
        # Sort by time (automatic chronological order)
        time_columns = sorted(result.columns, key=lambda x: pd.to_datetime(x, format='%I:%M:%S %p').time())
        result = result[time_columns]
        result = result.sort_index()
        
        print("🔄 PROCESSING COMPLETE!")
        print(f"   Found {len(result)} unique dates")
        print(f"   Found {len(result.columns)} time intervals")
        print()
        
        # Show the result
        print("📈 PROCESSED DATA PREVIEW:")
        print(result.head().to_string())
        print()
        
        # Save the result
        output_file = "demo_output.csv"
        result.to_csv(output_file)
        print(f"💾 Results saved to: {output_file}")
        print()
        
        print("=" * 60)
        print("KEY IMPROVEMENTS:")
        print("✅ Robust datetime parsing (no more string splitting)")
        print("✅ Automatic chronological sorting")
        print("✅ Cleaner, more maintainable code")
        print("✅ Better error handling")
        print("✅ Same output format as original")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_call_rates()
