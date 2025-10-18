"""
Observer pattern implementation for progress tracking and notifications.
Allows different components to observe and react to application events.
"""

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class ProgressObserver(ABC):
    """Abstract base class for progress observers."""
    
    @abstractmethod
    def on_file_selected(self, file_path: str) -> None:
        """Called when a file is selected for processing."""
        pass
    
    @abstractmethod
    def on_data_loaded(self, row_count: int, columns: list[str]) -> None:
        """Called when data is successfully loaded."""
        pass
    
    @abstractmethod
    def on_processing_started(self, processor_type: str) -> None:
        """Called when data processing begins."""
        pass
    
    @abstractmethod
    def on_processing_complete(self, result: pd.DataFrame) -> None:
        """Called when data processing is complete."""
        pass
    
    @abstractmethod
    def on_file_saved(self, output_path: str) -> None:
        """Called when output file is saved."""
        pass
    
    @abstractmethod
    def on_error(self, error_message: str) -> None:
        """Called when an error occurs."""
        pass


class ConsoleProgressObserver(ProgressObserver):
    """Console-based progress observer that prints status messages."""
    
    def on_file_selected(self, file_path: str) -> None:
        print(f"📁 Selected file: {file_path}")
    
    def on_data_loaded(self, row_count: int, columns: list[str]) -> None:
        print(f"📊 Successfully loaded {row_count} rows of data")
        print(f"   Columns: {', '.join(columns[:5])}{'...' if len(columns) > 5 else ''}")
    
    def on_processing_started(self, processor_type: str) -> None:
        print(f"🔄 Starting {processor_type} processing...")
    
    def on_processing_complete(self, result: pd.DataFrame) -> None:
        print(f"✅ Processing complete!")
        print(f"   Found {len(result)} unique dates and {len(result.columns)} time intervals")
    
    def on_file_saved(self, output_path: str) -> None:
        print(f"💾 Results saved to: {output_path}")
    
    def on_error(self, error_message: str) -> None:
        print(f"❌ Error: {error_message}")


class DetailedConsoleObserver(ProgressObserver):
    """More detailed console observer with additional information."""
    
    def on_file_selected(self, file_path: str) -> None:
        print("=" * 60)
        print("CALL RATES PROCESSING STARTED")
        print("=" * 60)
        print(f"📁 Input file: {file_path}")
    
    def on_data_loaded(self, row_count: int, columns: list[str]) -> None:
        print(f"📊 Data loaded successfully:")
        print(f"   • Rows: {row_count:,}")
        print(f"   • Columns: {len(columns)}")
        print(f"   • Column names: {', '.join(columns)}")
    
    def on_processing_started(self, processor_type: str) -> None:
        print(f"🔄 Processing with {processor_type} strategy...")
    
    def on_processing_complete(self, result: pd.DataFrame) -> None:
        print(f"✅ Processing completed successfully!")
        print(f"   • Unique dates: {len(result)}")
        print(f"   • Time intervals: {len(result.columns)}")
        print(f"   • Time range: {result.columns[0]} to {result.columns[-1]}")
        
        # Show sample of results
        print("\n📈 Sample results:")
        print(result.head(3).to_string())
    
    def on_file_saved(self, output_path: str) -> None:
        print(f"💾 Output saved to: {output_path}")
        print("=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)
    
    def on_error(self, error_message: str) -> None:
        print("=" * 60)
        print("❌ ERROR OCCURRED")
        print("=" * 60)
        print(f"Error: {error_message}")
        print("=" * 60)


class SilentObserver(ProgressObserver):
    """Silent observer that doesn't output anything (useful for testing)."""
    
    def on_file_selected(self, file_path: str) -> None:
        pass
    
    def on_data_loaded(self, row_count: int, columns: list[str]) -> None:
        pass
    
    def on_processing_started(self, processor_type: str) -> None:
        pass
    
    def on_processing_complete(self, result: pd.DataFrame) -> None:
        pass
    
    def on_file_saved(self, output_path: str) -> None:
        pass
    
    def on_error(self, error_message: str) -> None:
        pass
