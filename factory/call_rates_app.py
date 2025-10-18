"""
Main application class using Factory and Observer patterns.
Orchestrates the call rates processing workflow.
"""

import easygui
from typing import List, Optional
import pandas as pd

from .file_readers import FileReaderFactory
from .data_processors import DataProcessorFactory
from .observers import ProgressObserver


class CallRatesApplication:
    """Main application class that orchestrates the call rates processing workflow."""
    
    def __init__(self):
        self.observers: List[ProgressObserver] = []
        self.file_reader_factory = FileReaderFactory()
        self.processor_factory = DataProcessorFactory()
    
    def add_observer(self, observer: ProgressObserver) -> None:
        """Add a progress observer to the application."""
        self.observers.append(observer)
    
    def remove_observer(self, observer: ProgressObserver) -> None:
        """Remove a progress observer from the application."""
        if observer in self.observers:
            self.observers.remove(observer)
    
    def _notify_observers(self, method_name: str, *args, **kwargs) -> None:
        """Notify all observers of an event."""
        for observer in self.observers:
            try:
                method = getattr(observer, method_name)
                method(*args, **kwargs)
            except Exception as e:
                # Don't let observer errors break the main flow
                print(f"Observer error: {e}")
    
    def _get_input_file(self) -> Optional[str]:
        """Get input file from user using GUI."""
        try:
            filetypes = self.file_reader_factory.get_supported_filetypes()
            filetypes.append(('All files', '*.*'))
            
            input_file = easygui.fileopenbox(
                msg='Select the input file (can be csv or xlsx). Only the first sheet of Excel files will be read.',
                default='*',
                multiple=False,
                filetypes=filetypes
            )
            
            if input_file:
                self._notify_observers('on_file_selected', input_file)
            
            return input_file
        except Exception as e:
            self._notify_observers('on_error', f"Error selecting input file: {e}")
            return None
    
    def _get_output_file(self) -> Optional[str]:
        """Get output file location from user using GUI."""
        try:
            output_file = easygui.filesavebox(
                "Select location to save output csv.",
                title="Save Location",
                default="output.csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            return output_file
        except Exception as e:
            self._notify_observers('on_error', f"Error selecting output file: {e}")
            return None
    
    def _load_data(self, file_path: str) -> Optional[pd.DataFrame]:
        """Load data from file using appropriate reader."""
        try:
            reader = self.file_reader_factory.create_reader(file_path)
            df = reader.read(file_path)
            
            self._notify_observers('on_data_loaded', len(df), list(df.columns))
            return df
        except Exception as e:
            self._notify_observers('on_error', f"Error loading data: {e}")
            return None
    
    def _process_data(self, df: pd.DataFrame, processor_type: str = "call_rates") -> Optional[pd.DataFrame]:
        """Process data using appropriate processor."""
        try:
            processor = self.processor_factory.create_processor(processor_type)
            self._notify_observers('on_processing_started', processor_type)
            
            result = processor.process(df)
            self._notify_observers('on_processing_complete', result)
            return result
        except Exception as e:
            self._notify_observers('on_error', f"Error processing data: {e}")
            return None
    
    def _save_result(self, result: pd.DataFrame, output_path: str) -> bool:
        """Save processing result to file."""
        try:
            result.to_csv(output_path)
            self._notify_observers('on_file_saved', output_path)
            return True
        except Exception as e:
            self._notify_observers('on_error', f"Error saving file: {e}")
            return False
    
    def run(self, processor_type: str = "call_rates") -> bool:
        """
        Run the complete call rates processing workflow.
        
        Args:
            processor_type: Type of processor to use (default: "call_rates")
            
        Returns:
            bool: True if processing completed successfully, False otherwise
        """
        try:
            # Step 1: Get input file
            input_file = self._get_input_file()
            if not input_file:
                return False
            
            # Step 2: Load data
            df = self._load_data(input_file)
            if df is None:
                return False
            
            # Step 3: Process data
            result = self._process_data(df, processor_type)
            if result is None:
                return False
            
            # Step 4: Get output file and save
            output_file = self._get_output_file()
            if not output_file:
                return False
            
            success = self._save_result(result, output_file)
            return success
            
        except Exception as e:
            self._notify_observers('on_error', f"Unexpected error: {e}")
            return False
    
    def get_available_processors(self) -> List[str]:
        """Get list of available processor types."""
        return self.processor_factory.get_available_processors()
    
    def get_supported_file_types(self) -> List[tuple[str, str]]:
        """Get list of supported file types for GUI."""
        return self.file_reader_factory.get_supported_filetypes()
