from flask import Flask, jsonify
from firebase_admin import firestore, initialize_app, credentials

app = Flask(__name__)

# Initialize Firebase with project ID
cred = credentials.Certificate('key.json')
initialize_app(cred)


def getRestaurants():
    restaurants = []
    restaurant_docs = firestore.client().collection('restaurants').get()
    for doc in restaurant_docs:
        restaurants.append(doc.to_dict())
    
    return restaurants

userId = "8GjEXLg6ZrdN1pW2OSPWA9CIpVG3"

def getUserPreferences(user):
    prefs = []
    user_prefs = firestore.client().collection('users').document(user).collection('preferences').get()
    
    for pref in user_prefs:
        prefs.append(pref.to_dict())

    return prefs



def get_recommend_restaurants_by_tastes():
    
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()
    
    matching_restaurants = []
    for restaurant in restaurants:
        if any(pref in restaurant['foodType'] for pref in user_preferences[0]['tastes']):            
            matching_restaurants.append(restaurant)  # Assuming the restaurant document has a 'name' field
    
    return matching_restaurants

def get_recommend_restaurants_by_price(user_id):
    user_preferences = getUserPreferences(user_id)
    restaurants = getRestaurants()
    
    matching_restaurants = []
    for restaurant in restaurants:

        min_price = user_preferences[0]['priceRange']['minPrice']
        max_price = user_preferences[0]['priceRange']['maxPrice']

        avg_price = restaurant['avgPrice']
        
        if min_price <= avg_price <= max_price:
            matching_restaurants.append(restaurant)
    
    return matching_restaurants


def get_recommend_restaurants_by_restrictions():
    
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()
    
    matching_restaurants = []
    for restaurant in restaurants:
        if any(pref in restaurant['dietaryConditions'] for pref in user_preferences[0]['restrictions']):            
            matching_restaurants.append(restaurant)  # Assuming the restaurant document has a 'name' field
    
    return matching_restaurants

@app.route('/recommend', methods=['GET'])
def filter_recommend(categoryFilter):
    
    if categoryFilter == 'tastes':
        get_recommend_restaurants_by_tastes()
    elif categoryFilter == 'price':
        get_recommend_restaurants_by_price()
    elif categoryFilter == 'restrictions':
        get_recommend_restaurants_by_restrictions()

if __name__ == '__main__':
    app.run(debug=True)
