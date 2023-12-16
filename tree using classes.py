#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import plotly.express as px


yelp_data = pd.read_json('yelp_restaurant_data.json')
yelp_data = yelp_data.dropna()
ca_data = pd.read_csv('ca_data.csv')
ca_data.rename(columns={'City': 'city'}, inplace=True)
california_data = pd.read_csv('california_data.csv')

yelp_data['city'] = yelp_data['location'].apply(lambda x: x.get('city') if x else None).str.lower()
yelp_data['primary_category'] = yelp_data['categories'].apply(lambda x: x[0]['title'] if x else None)
price_mapping = {'$': 1, '$$': 2, '$$$': 3, '$$$$': 4}
yelp_data['price_level'] = yelp_data['price'].map(price_mapping)


ca_data['MedianIncome'] = ca_data['Median']
ca_data_processed = ca_data[['city', 'MedianIncome', 'County']].copy()
ca_data_processed.loc[:, 'city'] = ca_data_processed['city'].str.lower()
ca_data_processed.groupby(['city', 'County'])['MedianIncome'].mean().reset_index()
california_data_processed = california_data.groupby('County')[['Poverty', 'Unemployment', 'TotalPop', 'Employed']].mean().reset_index()

yelp_with_demo = pd.merge(yelp_data, ca_data_processed, how='left', on='city')
yelp_with_demo = pd.merge(yelp_with_demo, california_data_processed, how='left', on='County')
yelp_with_demo = yelp_with_demo.dropna()

class RestaurantTree:
    def __init__(self, data):
        self.counties = {}
        self.build_tree(data)

    def build_tree(self, data):
        for _, row in data.iterrows():
            county_name = row['County']
            city_name = row['city']
            cuisine = row['primary_category']
            rating = row['rating']
            restaurant_name = row['name']
            additional_info = {
                'MedianIncome': row['MedianIncome'],
                'Poverty': row['Poverty'],
                'Unemployment': row['Unemployment']
            }

            if county_name not in self.counties:
                self.counties[county_name] = County()
            city = self.counties[county_name].add_city(city_name, additional_info)
            city.add_cuisine(cuisine, rating, restaurant_name)

    def print_tree(self, node=None, indent="", is_city_info=False):
        if node is None:
            node = self.counties
        if isinstance(node, dict):
            for key, val in node.items():
                print(indent + str(key))
                self.print_tree(val, indent + "    ")
        elif isinstance(node, County):
            self.print_tree(node.cities, indent)
        elif isinstance(node, City):
            print(indent + "City Info: " + str(node.info))
            self.print_tree(node.cuisines, indent + "    ")
        elif isinstance(node, Cuisine):
            for rating, restaurants in node.ratings.items():
                print(indent + f"Rating: {rating}")
                for restaurant in restaurants:
                    print(indent + "    - " + restaurant)

class County:
    def __init__(self):
        self.cities = {}

    def add_city(self, city_name, city_info):
        if city_name not in self.cities:
            self.cities[city_name] = City(city_info)
        return self.cities[city_name]

class City:
    def __init__(self, info):
        self.info = info
        self.cuisines = {}

    def add_cuisine(self, cuisine_name, rating, restaurant_name):
        if cuisine_name not in self.cuisines:
            self.cuisines[cuisine_name] = Cuisine()
        self.cuisines[cuisine_name].add_restaurant(rating, restaurant_name)

class Cuisine:
    def __init__(self):
        self.ratings = {}

    def add_restaurant(self, rating, restaurant_name):
        if rating not in self.ratings:
            self.ratings[rating] = set()
        self.ratings[rating].add(restaurant_name)

        
restaurant_tree = RestaurantTree(yelp_with_demo)
restaurant_tree.print_tree()


# In[ ]:




