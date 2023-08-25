import statistics
import pandas as pd
from elasticsearch import Elasticsearch
from pandas import json_normalize

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# Ignores unverified https request warning

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# Ignores DeprecationWarnings

es = Elasticsearch( # Specifies the elasticsearch "location" to store the data
    hosts="https://elastic:pancakes@localhost:9200/",
    verify_certs=False
)

## Loading in margins and dimensions from csv to pandas dataframe
basepath = "C:/Users/lucas/OneDrive/Documenten/RUG/Msc Year 1/Trimester 1" \
           "/Data analysis and programming for OM/Assignment"
margins = pd.read_csv(basepath + "/margins.csv")
dimensions = pd.read_csv(basepath + "/dimensions.csv")

search_body = { # search_body that aggregates on product_id,
    # so giving the demand per product over the whole period
    "size": 0,
    "aggs": {
        "PerProduct": {
            "terms": { # Here we specify that we aggregate on product_id
                "field": "product_id",
                "size": 10000,
                "order": {
                    "_key": "asc"
                }
            }
        }
    }
}

result = es.search(index="sales", body=search_body)
dfProducts = json_normalize(result['aggregations']['PerProduct']['buckets'])
dfProducts.rename(columns={'key': 'product_id'}, inplace=True)

search_body = { # search_body that aggregates on days, so giving the
                # demand per day over all products
    "size": 0,
    "aggs": {
        "PerDay": {
            "terms": { # Here we specify that we aggregate on days
                "field": "day",
                "size": 10000,
                "order": {
                    "_key": "asc"
                }
            }
        }
    }
}

result = es.search(index="sales", body=search_body)
days = result['aggregations']['PerDay']['buckets']
ndays = len(days)
df = pd.DataFrame(list(range(1, ndays + 1)), columns=["Day"])
# Dataframe with the days (1 to 730 in this case). We specify this one, as we
# want to merge our dataframes such that if we have no demand on say day 5,
# we get a zero there instead of ignoring that row

for index, row in dfProducts.iterrows():
    search_body = {
        "size": 10000,  # Needs to be larger than number of product orders
        'query': {  # Here we find the orders with product number
                    # row["product_id"]
            'term': {
                'product_id': row["product_id"]
            }
        },
        "aggs": {  # Here we find the orders per day for said product
            "OrdersPerDay": {
                "terms": {
                    "field": "day",
                    "size": 1000,
                    "order": {
                        "_key": "asc"
                    }
                }
            }
        }
    }
    result = es.search(index="sales", body=search_body)

    secondFrame = pd.DataFrame(result["aggregations"]["OrdersPerDay"]["buckets"])
    # The orders per day
    secondFrame = secondFrame.rename(columns={"key": "Day", "doc_count": "ID" +
                                            str(row["product_id"])})

    df = df.merge(secondFrame, how="left", on=["Day"]).fillna(0)
    # Constructs a dataframe with Orders per day, putting
    # 0 at the places where we had no orders.

Prod_list_mean = []
Prod_list_std = []
for i in range(1, df.shape[1]):
    Prod_list_mean.append(statistics.mean(list(df["ID" + str(i)])))
    Prod_list_std.append(statistics.stdev(list(df["ID" + str(i)])))

dfProducts["AvgOrders"] = Prod_list_mean
dfProducts["StdOrders"] = Prod_list_std
dfProducts["Margins"] = margins["margin"]
dfProducts["Length"] = dimensions["length"]
dfProducts["Width"] = dimensions["width"]
dfProducts["Height"] = dimensions["height"]

dfProducts.to_pickle("dfProducts.pkl")
df.to_pickle("dfOrderPerDay.pkl")