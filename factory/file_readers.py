"""
File reader implementations using Factory pattern.
Handles different file formats (CSV, Excel) with a common interface.
"""

import pandas as pd
from abc import ABC, abstractmethod
from pathlib import Path


class FileReader(ABC):
    """Abstract base class for file readers."""
    
    @abstractmethod
    def read(self, file_path: str) -> pd.DataFrame:
        """Read a file and return a pandas DataFrame."""
        pass
    
    @abstractmethod
    def get_supported_extensions(self) -> list[str]:
        """Return list of supported file extensions."""
        pass


class CSVReader(FileReader):
    """Reader for CSV files."""
    
    def read(self, file_path: str) -> pd.DataFrame:
        """Read CSV file with proper encoding handling."""
        try:
            return pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            # Fallback to latin-1 if utf-8 fails
            return pd.read_csv(file_path, encoding='latin-1')
    
    def get_supported_extensions(self) -> list[str]:
        return ['.csv']


class ExcelReader(FileReader):
    """Reader for Excel files."""
    
    def read(self, file_path: str) -> pd.DataFrame:
        """Read Excel file (first sheet only)."""
        return pd.read_excel(file_path, sheet_name=0)
    
    def get_supported_extensions(self) -> list[str]:
        return ['.xlsx', '.xls']


class FileReaderFactory:
    """Factory for creating appropriate file readers based on file extension."""
    
    _readers = {
        '.csv': CSVReader,
        '.xlsx': ExcelReader,
        '.xls': ExcelReader,
    }
    
    @classmethod
    def create_reader(cls, file_path: str) -> FileReader:
        """Create appropriate reader based on file extension."""
        file_extension = Path(file_path).suffix.lower()
        
        if file_extension not in cls._readers:
            supported_extensions = []
            for reader_class in cls._readers.values():
                supported_extensions.extend(reader_class().get_supported_extensions())
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(supported_extensions)}"
            )
        
        return cls._readers[file_extension]()
    
    @classmethod
    def get_supported_filetypes(cls) -> list[tuple[str, str]]:
        """Get file types for GUI file dialogs."""
        filetypes = []
        for reader_class in cls._readers.values():
            reader = reader_class()
            extensions = reader.get_supported_extensions()
            if extensions:
                # Create file type description
                ext_str = ' '.join(f'*{ext}' for ext in extensions)
                filetypes.append((f"{reader.__class__.__name__} files", ext_str))
        return filetypes
