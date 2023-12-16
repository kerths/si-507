https://www.yelp.com/developers/v3/manage_app  Use the link to register to get the API key. 
To interact with my program, you need to enter the cuisine, price level, minimum rating and minimum number of reviews. Note that the choices for cuisine are between "chinese", "mexican", "italian", "korean", " japanese", "indian", "french", "spanish", "thai".
After filling out these inputs, you will get the Chart for rating distribution and Chart for review count for the recommended restaurant. then you can make a choice whether you would like to know more about the city or not, and then enter the city name.
I used the requests,pandas,plotly.express packages.

This tree is specifically designed to organize information about restaurants, categorized by county, city, cuisine type, and rating. Additionally, it includes demographic information for each city. Let's break down the structure and content of this tree:
Data Structure:
Top Level - Counties: The highest level of the tree organizes data by counties. Each county is a key in the main dictionary.
Second Level - Cities within Counties: Under each county, there's another dictionary where each key is a city within that county.
City Information: For each city, apart from the restaurant data, there's a special entry under the key 'info', which contains demographic information (Median Income, Poverty, Unemployment).
Third Level - Cuisines in Cities: Within each city, there's a dictionary under the key 'cuisines'. Each key in this dictionary is a type of cuisine, representing the various cuisines available in that city.
Fourth Level - Restaurant Ratings by Cuisine: Under each cuisine, there's another dictionary where each key is a rating score.
Fifth Level - Restaurant Names: This level contains a list of restaurant names that correspond to a particular rating within a specific cuisine.
