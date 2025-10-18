"""
Data processing implementations using Factory pattern.
Handles different types of data processing with a common interface.
"""

import pandas as pd
from abc import ABC, abstractmethod
from typing import Dict, Any


class DataProcessor(ABC):
    """Abstract base class for data processors."""
    
    @abstractmethod
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process the input DataFrame and return processed result."""
        pass
    
    @abstractmethod
    def get_processor_type(self) -> str:
        """Return the type identifier for this processor."""
        pass


class CallRatesProcessor(DataProcessor):
    """Processor for call rate data analysis."""
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process call rate data into time-series format."""
        # Create a copy to avoid SettingWithCopyWarning
        df = df.copy()
        
        # Clean the data - remove rows where first column is NaN (blank rows)
        df = df.dropna(subset=[df.columns[0]])
        
        # Parse datetime columns
        try:
            df['start_datetime'] = pd.to_datetime(df['Interval Start Time'])
            df['end_datetime'] = pd.to_datetime(df['Interval End Time'])
        except Exception as e:
            raise ValueError(
                f"Error parsing datetime columns: {e}. "
                "Make sure your data has 'Interval Start Time' and 'Interval End Time' columns"
            )
        
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
    
    def get_processor_type(self) -> str:
        return "call_rates"


class TimeSeriesProcessor(DataProcessor):
    """Processor for general time series data analysis."""
    
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        """Process general time series data."""
        # Basic time series processing - can be extended
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df = df.set_index('timestamp')
            return df.resample('H').sum()  # Hourly aggregation
        else:
            raise ValueError("Time series processor requires a 'timestamp' column")
    
    def get_processor_type(self) -> str:
        return "time_series"


class DataProcessorFactory:
    """Factory for creating appropriate data processors."""
    
    _processors = {
        "call_rates": CallRatesProcessor,
        "time_series": TimeSeriesProcessor,
    }
    
    @classmethod
    def create_processor(cls, processor_type: str) -> DataProcessor:
        """Create appropriate processor based on type."""
        if processor_type not in cls._processors:
            available_types = list(cls._processors.keys())
            raise ValueError(
                f"Unknown processor type: {processor_type}. "
                f"Available types: {', '.join(available_types)}"
            )
        
        return cls._processors[processor_type]()
    
    @classmethod
    def get_available_processors(cls) -> list[str]:
        """Get list of available processor types."""
        return list(cls._processors.keys())
