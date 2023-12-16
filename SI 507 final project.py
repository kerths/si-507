#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import json

def search_yelp(api_key, location, categories, limit=50):
    url = "https://api.yelp.com/v3/businesses/search"
    headers = {
        "Authorization": "Bearer " + api_key
    }
    params = {
        "location": location,
        "categories": categories,
        "limit": limit
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "API request failed", "status_code": response.status_code}

api_key = "CLt7PDWX0uhbzplx51QvciKXML36IE8plFa6Ki0aclQ18qMnU06awBQhsnZRf8mnVsTqsKPePbbxCmTi_Dr39AJOF2oNKWOuJUlNLAhNUmQH2PCeyZmibuqA-oVRZXYx"

types_of_restaurants = ["chinese", "mexican", "italian", "korean", "japanese", "indian", "french", "spanish", "thai"]
results = []

for category in types_of_restaurants:
    result = search_yelp(api_key, "California", category, limit=200 // len(types_of_restaurants))
    results.extend(result['businesses'])

with open('yelp_restaurant_data.json', 'w') as f:
    json.dump(results, f, indent=4)
print(f"Saved {len(results)} restaurant records to yelp_restaurant_data.json")


# In[1]:


import pandas as pd
kaggle_income = pd.read_csv('kaggle_income.csv', encoding='latin1')
ca_data = kaggle_income[kaggle_income['State_ab'] == 'CA'].copy()
ca_data.loc[:, 'County'] = ca_data['County'].str.replace(' County', '')
ca_data.to_csv('ca_data.csv', index=False)
acs2015_census_tract_data = pd.read_csv('acs2015_census_tract_data.csv',encoding='latin1')
california_data = acs2015_census_tract_data[acs2015_census_tract_data['State'] == 'California']
california_data.to_csv('california_data.csv', index=False)


# In[ ]:


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


def create_tree_with_additional_info(data):
    tree = {}
    for index, row in data.iterrows():
        county = row['County']
        city = row['city']
        cuisine = row['primary_category']
        rating = row['rating']
        restaurant_name = row['name']
        additional_info = {
            'MedianIncome': row['MedianIncome'],
            'Poverty': row['Poverty'],
            'Unemployment': row['Unemployment']
        }

        if county not in tree:
            tree[county] = {}
        if city not in tree[county]:
            tree[county][city] = {'info': additional_info, 'cuisines': {}}
        if cuisine not in tree[county][city]['cuisines']:
            tree[county][city]['cuisines'][cuisine] = {}
        if rating not in tree[county][city]['cuisines'][cuisine]:
            tree[county][city]['cuisines'][cuisine][rating] = []
        if restaurant_name not in tree[county][city]['cuisines'][cuisine][rating]:
            tree[county][city]['cuisines'][cuisine][rating].append(restaurant_name)

    return tree

def print_tree_with_additional_info(node, indent="", is_city_info=False):
    if isinstance(node, dict):
        for key, val in node.items():
            if is_city_info and key == 'info':
                print(indent + "City Info: " + str(val))
            else:
                print(indent + str(key))
                next_level_is_city_info = key == 'cuisines'
                print_tree_with_additional_info(val, indent + "    ", next_level_is_city_info)
    elif isinstance(node, list):
        for val in node:
            print(indent + "- " + val)
    else:
        print(indent + "Data: " + str(node))

tree_with_info = create_tree_with_additional_info(yelp_with_demo)


def get_recommendations(cuisine, price_level, rating, review_count, data):
    filtered_data = data[
        (data['primary_category'].str.lower() == cuisine.lower()) &
        (data['price_level'] == price_level) &
        (data['rating'] >= rating) &
        (data['review_count'] >= review_count)
    ]

    filtered_data = filtered_data.drop_duplicates(subset=['name', 'city'])

    return filtered_data



def display_recommendations(recommendations):
    fig = px.bar(recommendations, x='name', y='rating', color='city', title='Rating Distribution of Recommended Restaurants')
    fig.write_html('recommendations.html')
    print("Chart for rating distribution has been saved as recommendations.html. You can view it in a web browser.")

def display_review_count(recommendations):
    fig = px.bar(recommendations, x='name', y='review_count', color='city', title='Review Count of Recommended Restaurants')
    fig.write_html('review_count_recommendations.html')
    print("Chart for review count has been saved as review_count_recommendations.html. You can view it in a web browser.")

valid_cuisines = ["chinese", "mexican", "italian", "korean", "japanese", "indian", "french", "spanish", "thai"]

def interactive_prompt_with_city_info(tree):
    print("Welcome to the Restaurant Recommendation System! Please enter your preferences to get recommendations.")

    cuisine = input("Please enter your preferred cuisine (e.g., 'Chinese'): ").lower()
    while cuisine not in valid_cuisines:
        print(f"Invalid cuisine. Valid options are: {', '.join(valid_cuisines)}.")
        cuisine = input("Please enter your preferred cuisine (e.g., 'Chinese'): ").lower()

    price = int(input("Please enter your price level (1 = '$', 2 = '$$', 3 = '$$$', 4 = '$$$$'): "))
    while price not in [1, 2, 3, 4]:
        print("Invalid price level. Valid options are 1, 2, 3, 4.")
        price = int(input("Please enter your price level (1 = '$', 2 = '$$', 3 = '$$$', 4 = '$$$$'): "))

    rating = float(input("Enter minimum rating (1-5): "))
    while not (1 <= rating <= 5):
        print("Invalid rating. Valid options are between 1 and 5.")
        rating = float(input("Enter minimum rating (1-5): "))

    review_count = int(input("Enter minimum number of reviews: "))

    recommendations = get_recommendations(cuisine, price, rating, review_count, yelp_with_demo)
    
    if not recommendations.empty:
        print("Based on your preferences, we recommend the following restaurants:")
        print(recommendations[['name', 'city', 'rating', 'review_count']])
        display_recommendations(recommendations)
        display_review_count(recommendations)

        city_info_request = input("Would you like to know more about any of these cities? Enter 'yes' or 'no': ").lower()
        if city_info_request == 'yes':
            city_name = input("Enter the name of the city you want to know more about: ").lower()
            city_info = get_city_info(tree, city_name)
            if city_info:
                print(f"Information for {city_name.capitalize()}: {city_info}")
            else:
                print("Sorry, we don't have information on that city.")
    else:
        print("Sorry, no restaurants found matching your preferences.")

def get_city_info(tree, city_name):
    for county in tree:
        if city_name in tree[county]:
            return tree[county][city_name]['info']
    return "No information available for this city."


tree_with_info = create_tree_with_additional_info(yelp_with_demo)
interactive_prompt_with_city_info(tree_with_info)


# In[ ]:




