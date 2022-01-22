import pandas as pd
import os
import matplotlib.pyplot as plt 
from itertools import combinations
from collections import Counter
from fastapi import FastAPI


app = FastAPI()

#Creating all the all_data.csv file
df = pd.read_csv("./Sales_Data/Sales_April_2019.csv")
files = [file for file in os.listdir('./Sales_Data')]
all_months_data = pd.DataFrame()
for file in files:
    df = pd.read_csv("./Sales_Data/"+file)
    all_months_data = pd.concat([all_months_data,df])

all_months_data.to_csv("all_data.csv",index = False)
all_data = pd.read_csv("all_data.csv")
# print(all_data.head())

#Cleaning the data 
nan_df = all_data[all_data.isna().any(axis=1)]
# nan_df.head()

all_data = all_data.dropna(how='all')

#Find Or and delete it
all_data = all_data[all_data["Order Date"].str[0:2] != "Or"]

#Convert columns to correct type
all_data["Quantity Ordered"] = pd.to_numeric(all_data["Quantity Ordered"])
all_data["Price Each"] = pd.to_numeric(all_data["Price Each"])

#Augment data with additional columns
#Adding a month to the column

all_data["Month"] = all_data["Order Date"].str[0:2]
all_data["Month"] = all_data["Month"].astype("int32")

#Add a sales Column
all_data["Sales"] = all_data["Quantity Ordered"] * all_data["Price Each"]
# all_data.head()

#Add a city column
def get_city(address):
    return address.split(',')[1]

def get_state(address):
    return address.split(',')[2].split(' ')[1]

all_data["City"] = all_data["Purchase Address"].apply(lambda x: x.split(',')[1] + ' (' + get_state(x) + ')')

# Q1 : What was the best month for sales? How much was earned that month ?
results_sales = all_data.groupby('Month').sum()

best_month_for_sales = results_sales.to_dict()

@app.get("/best_month_for_sales")
def sales():
    return best_month_for_sales

#Q2) What city has the higest no of sales

highest_sales = all_data.groupby('City').sum()
cities = [city for city , df in all_data.groupby('City')]
results_highest_sales = highest_sales.to_dict()

@app.get("/highest_for_sales")
def higest_sales():
    return (results_highest_sales)

@app.get("/highest_for_sales_cities")
def higest_sales():
    return (cities)

#Q3) what time should we display adds to maintain best customer interaction ?

all_data["Order Date"] = pd.to_datetime(all_data["Order Date"])
all_data['Hour'] = all_data['Order Date'].dt.hour
all_data['Minute'] = all_data['Order Date'].dt.minute

hours = [hour for hour, df in all_data.groupby("Hour")]
best_customer_hours = all_data.groupby(['Hour']).count()
results_best_customer_hours = best_customer_hours.to_dict()

@app.get("/best_customer_hours")
def best_hours():
    return (results_best_customer_hours)

# Q4 How to get the prods that are the most often sold together?
df = all_data[all_data["Order ID"].duplicated(keep=False)]

df['Grouped'] = df.groupby('Order ID')['Product'].transform(lambda x: ','.join(x))

df = df[['Order ID','Grouped']].drop_duplicates()

count = Counter() 

for row in df["Grouped"]:
    row_list = row.split(',')
    count.update(Counter(combinations(row_list,2)))

result_products_sold_together = dict()

for key,value in count.most_common(1000):
   result_products_sold_together[value] = key

@app.get("/products_sold_together")
def product_together():
    return (result_products_sold_together)

#Q5) Which Product sold the most ?
product_group = all_data.groupby('Product')
quantity_ordered = product_group.sum()['Quantity Ordered']

products = [product for product, df in product_group]

@app.get("/products_sold_most")
def product_most():
    return (products)