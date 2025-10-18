"""
Main entry point using Factory and Observer patterns.
Demonstrates clean separation of concerns and extensible architecture.
"""

from .call_rates_app import CallRatesApplication
from .observers import ConsoleProgressObserver, DetailedConsoleObserver, SilentObserver


def main():
    """Main entry point for the call rates application."""
    
    # Create the application
    app = CallRatesApplication()
    
    # Add observers (you can add multiple observers)
    app.add_observer(ConsoleProgressObserver())
    
    # Uncomment for more detailed output:
    # app.add_observer(DetailedConsoleObserver())
    
    # Uncomment for silent mode (useful for testing):
    # app.add_observer(SilentObserver())
    
    # Run the application
    print("🚀 Starting Call Rates Processing Application")
    print(f"📋 Available processors: {', '.join(app.get_available_processors())}")
    print(f"📁 Supported file types: {[ft[0] for ft in app.get_supported_file_types()]}")
    print()
    
    success = app.run(processor_type="call_rates")
    
    if success:
        print("\n🎉 Application completed successfully!")
    else:
        print("\n❌ Application completed with errors.")


if __name__ == "__main__":
    main()
