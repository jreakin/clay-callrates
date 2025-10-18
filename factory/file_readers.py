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
        """Read Excel file (first sheet only) with proper header handling."""
        # First, read without header assumption to inspect structure
        df_raw = pd.read_excel(file_path, sheet_name=0, header=None)
        
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
            df = pd.read_excel(file_path, sheet_name=0, header=header_row)
            # Remove any rows above the header that might be empty
            if header_row > 0:
                df = df.dropna(how='all')  # Remove completely empty rows
        else:
            # Fallback to default behavior
            df = pd.read_excel(file_path, sheet_name=0)
        
        return df
    
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
            # Deduplicate and sort extensions for a clean error message
            unique_extensions = sorted(set(supported_extensions))
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(unique_extensions)}"
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
