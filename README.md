Clone the Repository
  git clone https://github.com/kharade-p/data_processing.git
  cd develop

Run the Application
  python process_data.py 

To view data download sqlite browser as per system from below link 
 https://sqlitebrowser.org/dl/
 After installation choose "Open Database" and select sales.db file

Queries to validate results
# -- Total number of records
# SELECT COUNT(*) FROM sales_data;

# -- Total sales by region
# SELECT Region, SUM(TotalSales) FROM sales_data GROUP BY Region;

# -- Average sales amount per transaction
# SELECT AVG(NetSale) FROM sales_data;

# -- Ensure no duplicate OrderIds
# SELECT OrderId, COUNT(*) FROM sales_data GROUP BY OrderId HAVING COUNT(*) > 1;
