import pandas as pd
from elasticsearch import Elasticsearch
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm # Mainly used for the z-statistics
import seaborn as sns; sns.set_theme() # For the heatmap
from gurobipy import Model, GRB
from matplotlib.patches import Rectangle


pd.options.mode.chained_assignment = None # Ignores chained warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Ignores unverified https request warning

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Ignores DeprecationWarnings


## Loading the csv file for sales into the elastic database
es = Elasticsearch( # Specifies the elasticsearch "location" to store the data
    hosts="https://elastic:pancakes@localhost:9200/",
    verify_certs=False
)

## The next lines are commented, as we only want to run them once.
## After all, if we have made the database there is no need to make it again


# Creates the elastic index in which we will put the data
# settings = {
#     'settings': {
#         "number_of_shards" : 3
#     }
# }
# es.indices.create(index="sales", body=settings)
# print("index created")
#
# basepath = "C:/Users/lucas/OneDrive/Documenten/RUG/Msc Year 1/Trimester 1" \
#            "/Data analysis and programming for OM/Assignment"
# import csv_to_elastic # Importing the python functions that allow us to,
#                       # quickly, put the csv data into our elastic database
# csv_to_elastic.ingest_csv_file_into_elastic_index(basepath + "/sales.csv",
# es, "sales", 5000)



## We load in the pandas dataframes (made in DataFrameConstruction)
dfProducts = pd.read_pickle("dfProducts.pkl")
dfOrderPerDay = pd.read_pickle("dfOrderPerDay.pkl")
ndays = dfProducts.shape[0]

# Here we construct an errorbar plot, with as mean the average orders and
# error the standard deviation
dfSorted = dfProducts.sort_values(by = ["AvgOrders"], ascending=False)
# Sorts the dataframe descending by Avg Orders
plt.errorbar(x = range(0, len(dfSorted["AvgOrders"])),
             y = dfSorted["AvgOrders"], xerr = 0, yerr = dfSorted["StdOrders"])
plt.savefig('Errorbar orders.png')
plt.show()

# Here we make a histogram of the average daily profit generated by each product
dfProducts["AvgDailyProfit"] = dfProducts["AvgOrders"] * dfProducts["Margins"]
plt.hist(x=dfProducts["AvgDailyProfit"], bins='auto', color='#0504aa')
plt.xlabel('Average daily profit')
plt.ylabel('Frequency')
plt.title('Histogram of average daily profits')
plt.savefig('Histogram average daily profits.png')
plt.show()

# Here we make a histogram of the volume of each product
dfProducts["Volume"] = dfProducts["Length"] * dfProducts["Height"] *\
                       dfProducts["Width"]
plt.hist(x=dfProducts["Volume"], bins='auto', color='#0504aa')
plt.xlabel('Volume of product (in cubed cm)')
plt.ylabel('Frequency')
plt.title('Histogram of volumes')
plt.savefig('Histogram volumes.png')
plt.show()

# We divide the products up in three different classes,
# the top 20% profit generating products, the following 30% and the bottom 50%
dfProfitSort = dfProducts.sort_values(by=["AvgDailyProfit"])
nrow = dfProfitSort.shape[0]
bottom50 = dfProfitSort[0:(round(0.5*nrow))]
middle30 = dfProfitSort[(round(0.5*nrow)):(round(0.8*nrow))]
top20 = dfProfitSort[(round(0.8*nrow)):nrow]

# We will compute the total profit and the number of products per class and
# display them in a barplot
plt.figure()
totprofits = [sum(bottom50["AvgDailyProfit"]), sum(middle30["AvgDailyProfit"]),
              sum(top20["AvgDailyProfit"])]
plt.bar(["Bottom 50%", "Middle 30%", "Top 20%"], totprofits, color = 'b',
        width = 0.25)
plt.ylabel("Total daily profit (euros)")
plt.title("Total daily profit for the three classes")
plt.savefig('Total daily profit per class.png')
plt.show()

plt.figure()
totsales = [len(bottom50["AvgOrders"]), len(middle30["AvgOrders"]),
            len(top20["AvgOrders"])]
plt.bar(["Bottom 50%", "Middle 30%", "Top 20%"], totsales, color = 'b'
        , width = 0.25)
plt.ylabel("Total products")
plt.title("Total number of products per class")
plt.savefig('Barplot products.png')
plt.show()

# Making a barplot that shows the daily average profits, marking the
# products on the boundary of the product classes
plt.figure()
colours = ["blue"] * nrow
max_profit = dfProfitSort["AvgDailyProfit"].iloc[-1]
plt.bar(range(0, nrow), dfProfitSort["AvgDailyProfit"][::-1],
        color=colours, width = 0.2)
plt.plot([round(0.5*nrow), round(0.5*nrow)], [0,max_profit],
         color='r', linestyle='-', linewidth=2)
plt.plot([round(0.2*nrow), round(0.2*nrow)], [0,max_profit],
         color='r', linestyle='-', linewidth=2)
plt.ylabel("Average daily sales (in euros)")
plt.title("Average daily sales")
plt.savefig('Barplot daily sales.png')
plt.show()

# Calculating the mean and standard deviation for the demand over the
# replenishment period
avg_list = 7 * dfProfitSort["AvgOrders"]
std_list = np.sqrt(7) * dfProfitSort["StdOrders"]

# Calculating the base-stock levels
quantile = [norm.ppf(0.9), norm.ppf(0.95), norm.ppf(0.99)]
# We do everything times 7 (sqrt(7)) because it is based on weekly data
bottom50["Basestock"] = round(bottom50["AvgOrders"] * 7 +
                              np.sqrt(7) * bottom50["StdOrders"] * quantile[0])
middle30["Basestock"] = round(middle30["AvgOrders"] * 7 +
                              np.sqrt(7) * middle30["StdOrders"] * quantile[1])
top20["Basestock"] = round(top20["AvgOrders"] * 7 +
                              np.sqrt(7) * top20["StdOrders"] * quantile[2])

volume_box = 40 * 40 * 20 # in cm^3
bottom50["NrProdPerBox"] = (0.9 * volume_box) // bottom50["Volume"]
# Notice the floor division and that we only use 90% efficiently
middle30["NrProdPerBox"] = (0.9 * volume_box) // middle30["Volume"]
top20["NrProdPerBox"] = (0.9 * volume_box) // top20["Volume"]

# Calculating the correlation matrix:
corr_basis = dfOrderPerDay.drop(columns="Day")
corr_matrix = np.corrcoef(corr_basis, rowvar = False)
plt.figure(figsize=(16, 16), dpi=100)
g = sns.heatmap(corr_matrix, vmin = 0.6, vmax = 0.61, cmap="Blues", cbar = True)
plt.savefig('heat_map.png')
plt.show()

# Finding the product couples
# Firstly, we set the diagonal elements to 1 (as they should equal,
# but sometimes they are 0.9999 right now)
for i in range(len(corr_matrix[0])):
    corr_matrix[i][i] = 1

# We can then find the values between 0.6 and 1 (exclusive), those are the
# relevant correlations over the treshold value
corr_list = [] # List of prod_ids for which we have a high enough correlation
for i in range(len(corr_matrix[0])):
    temp_list = (corr_matrix[i] > 0.6) & (corr_matrix[i] < 1)
    corr_list.append([i + 1 for i, x in enumerate(temp_list) if x])

prod_couples = []
# In this loop we find the combination of top20 products with lower products
for i in top20["product_id"]:
    if len(corr_list[i-1]) > 0: # If there is an element in corr_list
        for j in range(0, len(corr_list[i-1])): # Loop over it
           if (sum(top20["product_id"] == corr_list[i-1][j]) == 0): # Not in top 20%
               prod_couples.append([i, corr_list[i-1][j]])
# In this loop we find the combination of middle30 products with lower products
for i in middle30["product_id"]:
    if len(corr_list[i-1]) > 0: # If there is an element in corr_list
        for j in range(0, len(corr_list[i-1])): # Loop over it
           if ((sum(middle30["product_id"] == corr_list[i-1][j]) == 0) &
                (sum(top20["product_id"] == corr_list[i-1][j]) == 0)):
               # Not in middle 30% and top 20%
               prod_couples.append([i, corr_list[i-1][j]])


print("Number of products couples between classes is", len(prod_couples))
# Highlighting these cells in the heatmap
plt.figure(figsize=(16, 16), dpi=100)
g = sns.heatmap(corr_matrix, vmin = 0.6, vmax = 0.61, cmap="Blues", cbar = True)
for i in prod_couples:
    g.add_patch(Rectangle((i[0], i[1]), 1, 1, fill=False, edgecolor='purple',
                          lw=2))
plt.savefig('heat_map_marked.png')
plt.show()

##### Optimization ######
# Calculating the average daily profit loss per product, which is the demand
# loss percentage times the average daily profit
bottom50["AvgProfitLoss"] = 0.5 * bottom50["AvgDailyProfit"]
middle30["AvgProfitLoss"] = 0.3 * middle30["AvgDailyProfit"]
top20["AvgProfitLoss"] = 0.2 * top20["AvgDailyProfit"]

# The dataframe that will be used in all optimization procedures
dfMerged = pd.concat([top20, middle30, bottom50], axis = 0) # Merging the dataframes
dfMerged["BoxesNeeded"] = -(dfMerged["Basestock"] // -dfMerged["NrProdPerBox"])
# We use ceiling division here, but since this is not defined with a simple
# operator in python, we use the floor division operator in a smart way
dfMerged = dfMerged.sort_values(by = ["product_id"])

dfMerged["Ratio"] = dfMerged["AvgProfitLoss"] / dfMerged["BoxesNeeded"]
dfMerged = dfMerged.sort_values(by = ["product_id"])

## Heuristic 1:
# In this heuristic, we will place a base-stock level of products in boxes
# for the product with the highest AvgProfitLoss, then fill boxes with the
# second highest AvgProfitLoss etc. until all boxes are full
# Flaws:
# 1. Assumes that the product_ids follow on each other (so 1,2,3 not 1,2,5 etc.)
# 2. Background: Correlations calculated between classes based on Profit, not
# products that on average have the highest Profit Loss

def heuristic1(dataframe, boxes):
    boxes_available = boxes
    dfPop = dataframe.copy()  # No reference!
    dfPop = dfPop.sort_values(by=["AvgProfitLoss"], ascending=False)

    prod_ids_first = [] # This will contain the products that are stored in
                        # the first warehouse
    i = 0
    while i < dfPop.shape[0]: # dfPop will contain the products that are not in
                              # the first warehouse yet
        prod_id = dfPop.iloc[i, 0]
        corr_prods = []

        # In this loop we check if we need to add other products to the first
        # warehouse too
        for j in range(0, len(prod_couples)):
            if prod_id == prod_couples[j][0]: # First element is highest sale value
                corr_prods.append(prod_couples[j][1] - 1)
        if len(corr_prods) > 0:
            corr_prods.append(prod_id - 1)
            row_indices = corr_prods
        else:
            row_indices = [prod_id - 1]

        tot_size_needed = np.sum(dataframe.iloc[row_indices, -2])
        # Total size needed to fit the product and its correlated products

        if (tot_size_needed <= boxes_available): # If we have enough room available
            # We can assign the products to the boxes
            boxes_available -= tot_size_needed

            for k in range(0, len(row_indices)): # Loop over the row_indices
                # Remove the indices from the dataframe such that we do not
                # assign the product to a box twice
                dfPop.drop(dfPop[(dfPop['product_id'] == row_indices[k] + 1)].index,
                            inplace=True)
                prod_ids_first.append(row_indices[k] + 1)

            i -= 1 # Since we removed a row at place i, what was row i + 1 is now
            # row i and therefore we want i to stay the same. Since we add one later
            # we place -1 here. Notice that the rows after row i that were removed
            # (those from the correlated products), are irrelevant for our choice of i

        # Small if statement to make sure we do not run the loop longer than necessary
        if (boxes_available == 0):
            break

        i += 1
    return prod_ids_first

prod_ids_first = heuristic1(dfMerged, 960)
prod_ids_first.sort()
# Now we also find the products that are stored in the second warehouse:
prod_ids_second = [x for x in range(1, nrow + 1) if x not in prod_ids_first]

# The actual loss made with this policy:
total_loss = 0
for i in range(0, len(prod_ids_second)):
    total_loss += dfMerged.iloc[prod_ids_second[i] - 1, -3]
# Can do this since dfMerged is sorted on product id
print("The total daily cost of implementing Heuristic 1 is: €", round(total_loss, 2),
      sep = "")



## Heuristic 2:
# In this heuristic, we will place a base-stock level of products in boxes
# for the product with the highest ratio AvgProfitLoss / BoxesNeeded, then
# fill boxes with the second highest ratio etc. until all boxes are full
# Flaws:
# 1. Assumes that the product_ids follow on each other (so 1,2,3 not 1,2,5 etc.)
# 2. Does not consider the ratio of the correlated products
# 3. Background: Correlations calculated between classes based on Profit, not
# products that on average have the highest Profit Loss
def heuristic2(dataframe, boxes):
    boxes_available = boxes
    dfPop = dataframe.copy() # No reference!
    dfPop = dfPop.sort_values(by = ["Ratio"], ascending = False) # No reference!

    prod_ids_first = [] # This will contain the products that are stored in
    # the first warehouse
    i = 0
    while i < dfPop.shape[0]: # dfPop will contain the products that are not in
                               # the first warehouse yet
        prod_id = dfPop.iloc[i, 0]
        corr_prods = []

        # In this loop we check if we need to add other products to the first
        # warehouse too
        for j in range(0, len(prod_couples)):
            if prod_id == prod_couples[j][0]: # First element is highest sale value
                corr_prods.append(prod_couples[j][1] - 1)
        if len(corr_prods) > 0:
            corr_prods.append(prod_id - 1)
            row_indices = corr_prods
        else:
            row_indices = [prod_id - 1]

        tot_size_needed = np.sum(dataframe.iloc[row_indices, -2])
        # Total size needed to fit the product and its correlated products
        # Notice the -2 now since we added a column to dfMerged


        if (tot_size_needed <= boxes_available): # If we have enough room
            # available we can assign the products to the boxes
            boxes_available -= tot_size_needed

            for k in range(0, len(row_indices)): # Loop over the row_indices
                # Remove the indices from the dataframe such that we do not assign
                # the product to a box twice
                dfPop.drop(dfPop[(dfPop['product_id'] == row_indices[k] + 1)].index,
                           inplace=True)
                prod_ids_first.append(row_indices[k] + 1)

            i -= 1  # Since we removed a row at place i, what was row i + 1 is now
            # row i and therefore we want i to stay the same. Since we add one later
            # we place -1 here. Notice that the rows after row i that were removed
            # (those from the correlated products), are irrelevant for our choice of i

        # Small if statement to make sure we do not run the loop longer than necessary
        if (boxes_available == 0):
            break

        i += 1

    return prod_ids_first

prod_ids_first = heuristic2(dfMerged, 960)
prod_ids_first.sort()
# Now we also find the products that are stored in the second warehouse:
prod_ids_second = [x for x in range(1, nrow + 1) if x not in prod_ids_first]

# The actual loss made with this policy:
total_loss = 0
for i in range(0, len(prod_ids_second)):
    total_loss += dfMerged.iloc[prod_ids_second[i] - 1, -3]
# Can do this since dfMerged is sorted on product id
print("The total daily cost of implementing Heuristic 2 is: €",
      round(total_loss, 2), sep = "")

## Knapsack problem:
def Knapsack(dataframe, boxes):
    m = Model("Knapsack problem")
    x = m.addVars(nrow, vtype=GRB.BINARY)
    c = dataframe["AvgProfitLoss"] # Costs of adding product to second warehouse
    p = dataframe["BoxesNeeded"] # Boxes needed per product

    # The constraint that makes sure no more than 960 boxes are used
    m.addConstr(sum(p[j] * (1 - x[j]) for j in range(len(x))) <= boxes)

    # The constraints that make sure correlated products are in the same warehouse
    for i,j in prod_couples:
        m.addConstr(x[i-1] * (1 - x[j-1]) == 0)
        m.addConstr(x[j - 1] * (1 - x[i - 1]) == 0)

    m.setObjective(sum(c[j] * x[j] for j in range(len(x))), GRB.MINIMIZE)
    m.setParam('OutputFlag', 0)
    m.optimize()

    return m.X

prod_ids_second = Knapsack(dfMerged, 960) # Recall our definition specified
# the x-variables as the products stored in the second (!) warehouse
prod_ids_second = [i + 1 for i in range(0, len(prod_ids_second))
                   if prod_ids_second[i] > 0]
prod_ids_first = [x for x in range(1, nrow + 1) if x not in prod_ids_second]

total_loss = 0
for i in range(0, len(prod_ids_second)):
    total_loss += dfMerged.iloc[prod_ids_second[i] - 1, -3]
print("The total daily cost of implementing the Knapsack solution is: €",
      round(total_loss, 2), sep = "")
print("The products stored in the first warehouse are:", prod_ids_first)


#### Senstivity Analysis ####
# On the available boxes
dfSensCost = pd.DataFrame({"Percentage": [], "Heuristic 1": [],
                           "Heuristic 2": [], "Knapsack": []})
for i in range(0, 41):
    print(i)
    percentage = i * 0.05
    boxes_available = 960 * percentage
    h1_first = heuristic1(dfMerged, boxes_available)
    h2_first = heuristic2(dfMerged, boxes_available)
    k_second = Knapsack(dfMerged, boxes_available)
    k_second = [i + 1 for i in range(0, len(k_second)) if k_second[i] > 0]
    h1_second = [x for x in range(1, nrow + 1) if x not in h1_first]
    h2_second = [x for x in range(1, nrow + 1) if x not in h2_first]
    h1_costs = 0
    h2_costs = 0
    k_costs = 0
    for i in range(0, len(k_second)):
        k_costs += dfMerged.iloc[k_second[i] - 1, -3]
    for i in range(0, len(h1_second)):
        h1_costs += dfMerged.iloc[h1_second[i] - 1, -3]
    for i in range(0, len(h2_second)):
        h2_costs += dfMerged.iloc[h2_second[i] - 1, -3]
    cost_frame = pd.DataFrame({"Percentage": [percentage],
                               "Heuristic 1": [h1_costs],
                               "Heuristic 2": [h2_costs],
                               "Knapsack": [k_costs]})
    dfSensCost = pd.concat([dfSensCost, cost_frame], ignore_index=True, axis = 0)

print(dfSensCost)

plt.plot(dfSensCost.iloc[:, 0], dfSensCost.iloc[:, -1])
plt.xlabel("Percentage of total (960 boxes)")
plt.ylabel("Average daily profit loss")

for i in range(0, 41):
    plt.scatter(dfSensCost.iloc[i, 0], dfSensCost.iloc[i, -1], color = "purple")
plt.savefig('Costs_knapsack.png')
plt.show()

dfSensCost["K-h1"] = dfSensCost["Heuristic 1"] - dfSensCost["Knapsack"]
dfSensCost["K-h2"] = dfSensCost["Heuristic 2"] - dfSensCost["Knapsack"]

plt.plot(dfSensCost.iloc[:, 0], dfSensCost.iloc[:, -2], color = "green",
         label = "Heuristic 1")
plt.plot(dfSensCost.iloc[:, 0], dfSensCost.iloc[:, -1], color = "red",
         label = "Heuristic 2")
plt.xlabel("Percentage of total (960 boxes)")
plt.ylabel("Cost difference (euros)")
plt.legend(loc ="upper right")
plt.savefig('Cost_difference.png')
plt.show()

# On the average daily profit loss
dfSensCost2 = pd.DataFrame({"Percentage": [], "Knapsack": []})
for i in range(0, 41):
    print(i)
    percentage = i * 0.05
    dfCopy = dfMerged.copy()
    dfCopy["AvgProfitLoss"] = percentage * dfCopy["AvgProfitLoss"]
    k_second = Knapsack(dfCopy, 960)
    k_second = [i + 1 for i in range(0, len(k_second)) if k_second[i] > 0]
    k_costs = 0
    for i in range(0, len(k_second)):
        k_costs += dfCopy.iloc[k_second[i] - 1, -3]
    cost_frame = pd.DataFrame({"Percentage": [percentage], "Knapsack": [k_costs]})
    dfSensCost2 = pd.concat([dfSensCost2, cost_frame], ignore_index=True, axis = 0)

plt.plot(dfSensCost2.iloc[:, 0], dfSensCost2.iloc[:, 1])
plt.xlabel("Percentage of average daily profit loss")
plt.ylabel("Average daily profit loss")

print(dfSensCost2)
for i in range(0, 41):
    plt.scatter(dfSensCost2.iloc[i, 0], dfSensCost2.iloc[i, 1], color = "purple")
plt.savefig('Costs_knapsack_2.png')
plt.show()