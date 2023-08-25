This was a project for the course "Data analysis and Programming for Operations Management". The data for this project was partily provided by Belsimpel (Gomibo).

The project considers optimally placing products over two warehouses, one with quick delivery and limited storage space and another with slow delivery but (assumed) unlimited storage space. The storage policy is simple but effective, a base-stock level (the average demand + a standard deviation related mark-up) is stored for every product and for each product we need to find the best warehouse to place the item. The sales lost for placing the item in the slow-delivery warehouse is different based on how often the product is sold. Furthermore, products which are often sold with each other have to be placed in the same warehouse.

To store the sales data elasticsearch has been used, a server (database) which is famous for its quick aggregations. After querying from this database, the sales data has been used to solve the problem using two heuristics and a knapsack formulation. 

A detailed description of the solution methods and results can be found in the file DAPOM_final.pdf

The main file used for this project is main.py, which uses DataFrameConstruction.py and csv_to_elastic.py.
