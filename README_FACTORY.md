# Factory Pattern Implementation

This branch demonstrates a refactored version of the call rates processing script using **Factory** and **Observer** design patterns.

## 🏗️ Architecture Overview

The original monolithic 86-line function has been refactored into a clean, modular architecture:

```
clay-callrates/
├── main.py                    # Original implementation (for comparison)
├── main_factory.py           # New factory pattern implementation
├── call_rates_app.py         # Main application orchestrator
├── file_readers.py           # Factory pattern for file reading
├── data_processors.py        # Factory pattern for data processing
├── observers.py              # Observer pattern for progress tracking
├── demo_factory.py           # Demo showing all patterns in action
└── README_FACTORY.md         # This documentation
```

## 🎯 Design Patterns Used

### 1. Factory Pattern 🏭

**File Reader Factory:**
- `CSVReader` - Handles CSV files
- `ExcelReader` - Handles Excel files (.xlsx, .xls)
- Easy to extend with new file formats

**Data Processor Factory:**
- `CallRatesProcessor` - Original call rates processing logic
- `TimeSeriesProcessor` - General time series processing
- Easy to add new processing strategies

### 2. Observer Pattern 👀

**Progress Observers:**
- `ConsoleProgressObserver` - Basic console output
- `DetailedConsoleObserver` - Detailed progress information
- `SilentObserver` - No output (useful for testing)

## 🚀 Usage

### Run the Factory Pattern Version:
```bash
uv run --project clay-callrates python main_factory.py
```

### Run the Demo:
```bash
uv run --project clay-callrates python demo_factory.py
```

### Compare with Original:
```bash
uv run --project clay-callrates python main.py
```

## ✨ Benefits of the New Architecture

### **Separation of Concerns**
- File I/O is separate from data processing
- GUI interactions are separate from business logic
- Each class has a single responsibility

### **Extensibility**
- Add new file formats without changing existing code
- Add new processing strategies easily
- Add new output formats (JSON, XML, etc.)

### **Testability**
- Mock file readers for unit tests
- Test processing logic independently
- Mock observers for testing

### **Maintainability**
- Each class has a single responsibility
- Easy to modify one part without affecting others
- Clear interfaces between components

## 🔧 Adding New Features

### Add a New File Format:
```python
class JSONReader(FileReader):
    def read(self, file_path: str) -> pd.DataFrame:
        return pd.read_json(file_path)
    
    def get_supported_extensions(self) -> list[str]:
        return ['.json']

# Register in factory
FileReaderFactory._readers['.json'] = JSONReader
```

### Add a New Processor:
```python
class CustomProcessor(DataProcessor):
    def process(self, df: pd.DataFrame) -> pd.DataFrame:
        # Your custom processing logic
        return processed_df
    
    def get_processor_type(self) -> str:
        return "custom"

# Register in factory
DataProcessorFactory._processors['custom'] = CustomProcessor
```

### Add a New Observer:
```python
class FileLogObserver(ProgressObserver):
    def __init__(self, log_file: str):
        self.log_file = log_file
    
    def on_file_selected(self, file_path: str) -> None:
        with open(self.log_file, 'a') as f:
            f.write(f"File selected: {file_path}\n")
    
    # Implement other observer methods...

# Use in application
app = CallRatesApplication()
app.add_observer(FileLogObserver("processing.log"))
```

## 📊 Performance Comparison

| Aspect | Original | Factory Pattern |
|--------|----------|-----------------|
| Lines of Code | 86 lines | ~400 lines (but modular) |
| Testability | Difficult | Easy |
| Extensibility | Hard | Easy |
| Maintainability | Poor | Excellent |
| Separation of Concerns | None | Complete |

## 🧪 Testing

The new architecture makes testing much easier:

```python
# Test file reader independently
def test_csv_reader():
    reader = CSVReader()
    df = reader.read("test.csv")
    assert len(df) > 0

# Test processor independently
def test_call_rates_processor():
    processor = CallRatesProcessor()
    # Create test DataFrame
    result = processor.process(test_df)
    assert result is not None

# Test with mock observers
def test_application_with_mock_observer():
    app = CallRatesApplication()
    mock_observer = Mock()
    app.add_observer(mock_observer)
    # Test application flow
```

## 🎓 Learning Objectives

This implementation demonstrates:

1. **Factory Pattern** - Creating objects without specifying their exact classes
2. **Observer Pattern** - Notifying multiple objects about events
3. **Separation of Concerns** - Each class has one responsibility
4. **Dependency Injection** - Dependencies are injected rather than created
5. **Interface Segregation** - Small, focused interfaces
6. **Open/Closed Principle** - Open for extension, closed for modification

## 🔄 Migration Path

To migrate from the original to the factory pattern:

1. **Keep original** - `main.py` remains unchanged
2. **Use new version** - `main_factory.py` for new features
3. **Gradual migration** - Replace components one at a time
4. **Full migration** - Eventually replace `main.py` with `main_factory.py`

This approach ensures backward compatibility while providing a path to modern, maintainable code.
