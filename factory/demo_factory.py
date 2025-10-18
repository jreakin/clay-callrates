"""
Demo script showing the Factory pattern implementation.
Demonstrates how the new architecture works without GUI dependencies.
"""

import pandas as pd
from .call_rates_app import CallRatesApplication
from .observers import DetailedConsoleObserver, SilentObserver
from .file_readers import FileReaderFactory
from .data_processors import DataProcessorFactory


def demo_factory_pattern():
    """Demonstrate the Factory pattern implementation."""
    
    print("=" * 80)
    print("FACTORY PATTERN DEMO - CALL RATES PROCESSING")
    print("=" * 80)
    print()
    
    # Demo 1: File Reader Factory
    print("🏭 DEMO 1: File Reader Factory")
    print("-" * 40)
    
    # Show available file types
    filetypes = FileReaderFactory.get_supported_filetypes()
    print(f"Supported file types: {filetypes}")
    
    # Demo creating readers
    try:
        csv_reader = FileReaderFactory.create_reader("test.csv")
        print(f"✅ Created CSV reader: {type(csv_reader).__name__}")
        
        excel_reader = FileReaderFactory.create_reader("test.xlsx")
        print(f"✅ Created Excel reader: {type(excel_reader).__name__}")
        
        # This would raise an error
        # unsupported_reader = FileReaderFactory.create_reader("test.txt")
        
    except ValueError as e:
        print(f"❌ Expected error: {e}")
    
    print()
    
    # Demo 2: Data Processor Factory
    print("🏭 DEMO 2: Data Processor Factory")
    print("-" * 40)
    
    # Show available processors
    processors = DataProcessorFactory.get_available_processors()
    print(f"Available processors: {processors}")
    
    # Demo creating processors
    call_rates_processor = DataProcessorFactory.create_processor("call_rates")
    print(f"✅ Created call rates processor: {type(call_rates_processor).__name__}")
    
    time_series_processor = DataProcessorFactory.create_processor("time_series")
    print(f"✅ Created time series processor: {type(time_series_processor).__name__}")
    
    print()
    
    # Demo 3: Observer Pattern
    print("👀 DEMO 3: Observer Pattern")
    print("-" * 40)
    
    # Create application with different observers
    app = CallRatesApplication()
    
    # Add multiple observers
    app.add_observer(DetailedConsoleObserver())
    app.add_observer(SilentObserver())  # This one won't output anything
    
    print("✅ Added multiple observers to the application")
    print(f"   • Total observers: {len(app.observers)}")
    
    print()
    
    # Demo 4: Processing with example data
    print("🔄 DEMO 4: Processing Example Data")
    print("-" * 40)
    
    try:
        # Read the example file
        reader = FileReaderFactory.create_reader("example.xlsx")
        df = reader.read("example.xlsx")
        
        # Fix column headers if needed (same logic as before)
        if 'Unnamed: 0' in df.columns:
            df.columns = df.iloc[0]
            df = df.drop(df.index[0]).reset_index(drop=True)
        
        print(f"✅ Loaded {len(df)} rows with columns: {list(df.columns)}")
        
        # Process the data
        processor = DataProcessorFactory.create_processor("call_rates")
        result = processor.process(df)
        
        print(f"✅ Processing complete!")
        print(f"   • Result shape: {result.shape}")
        print(f"   • Date range: {len(result)} dates")
        print(f"   • Time intervals: {len(result.columns)}")
        
        # Show sample results
        print("\n📊 Sample Results:")
        print(result.head(2).to_string())
        
        # Save demo output
        result.to_csv("demo_factory_output.csv")
        print(f"\n💾 Demo output saved to: demo_factory_output.csv")
        
    except Exception as e:
        print(f"❌ Demo error: {e}")
    
    print()
    print("=" * 80)
    print("FACTORY PATTERN DEMO COMPLETE")
    print("=" * 80)
    print()
    print("🎯 Key Benefits Demonstrated:")
    print("   ✅ Separation of Concerns - Each class has one responsibility")
    print("   ✅ Extensibility - Easy to add new file types and processors")
    print("   ✅ Testability - Each component can be tested independently")
    print("   ✅ Maintainability - Changes to one part don't affect others")
    print("   ✅ Observer Pattern - Multiple ways to track progress")
    print("=" * 80)


if __name__ == "__main__":
    demo_factory_pattern()
