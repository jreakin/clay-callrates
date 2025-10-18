"""
Factory pattern implementation for call rates processing.

This package contains the refactored version of the call rates processing
using Factory and Observer design patterns for better separation of concerns,
extensibility, and maintainability.
"""

from .file_readers import FileReaderFactory, FileReader, CSVReader, ExcelReader
from .data_processors import DataProcessorFactory, DataProcessor, CallRatesProcessor, TimeSeriesProcessor
from .observers import ProgressObserver, ConsoleProgressObserver, DetailedConsoleObserver, SilentObserver
from .call_rates_app import CallRatesApplication

__all__ = [
    # Factories
    'FileReaderFactory',
    'DataProcessorFactory',
    
    # File Readers
    'FileReader',
    'CSVReader', 
    'ExcelReader',
    
    # Data Processors
    'DataProcessor',
    'CallRatesProcessor',
    'TimeSeriesProcessor',
    
    # Observers
    'ProgressObserver',
    'ConsoleProgressObserver',
    'DetailedConsoleObserver',
    'SilentObserver',
    
    # Main Application
    'CallRatesApplication',
]
