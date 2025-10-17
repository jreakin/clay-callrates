Simple python script to digest a report I made exclusively for spitting out calls/hour per CSQ at the call center. 
The report comes from CUIC and is based on the "Contact Service Queue Activity by Interval" report definition.

Required modules:
  - easygui
  - openpyxl

Other modules that are imported but shouldn't need to be installed:
  - csv
  - typing
  - os

Usage is simple. Run the script, select your input CSV or XLSX file, then select where to save the output. 
By design you're able to just feed the report straight into the script without having to clean up the empty line on top or the extra data at the bottom. 
