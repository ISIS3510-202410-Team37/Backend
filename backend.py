from flask import Flask, jsonify
from firebase_admin import firestore, initialize_app, credentials

app = Flask(__name__)

cred = credentials.Certificate('key.json')
initialize_app(cred)


def getRestaurants():
    restaurants = []
    try:
        restaurant_docs = firestore.client().collection('restaurants').get()
        
        for doc in restaurant_docs:
            restaurants.append(doc.to_dict())
    except Exception as e:
        print(f"Error al obtener la lista de restaurantes: {e}")
        return None 

    return restaurants


def getUserPreferences(user):
    prefs = []
    try:
        user_prefs = firestore.client().collection('users').document(user).collection('preferences').get()
        
        for pref in user_prefs:
            prefs.append(pref.to_dict())
    except Exception as e:
        print(f"Error al obtener las preferencias del usuario: {e}")
        return None 

    return prefs


def get_recommend_restaurants_by_tastes(userId):
    
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()
    
    matching_restaurants = []

    if not user_preferences or 'tastes' not in user_preferences[0] or not user_preferences[0]['tastes']:
        return matching_restaurants
    
    for restaurant in restaurants:
        if any(pref in restaurant['foodType'] for pref in user_preferences[0]['tastes']):            
            matching_restaurants.append(restaurant) 
    
    return matching_restaurants

def get_recommend_restaurants_by_price(userId):
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()
    
    matching_restaurants = []
    
    if not user_preferences or 'priceRange' not in user_preferences[0] or not user_preferences[0]['priceRange']:
        return matching_restaurants
    
    for restaurant in restaurants:

        min_price = user_preferences[0]['priceRange']['minPrice']
        max_price = user_preferences[0]['priceRange']['maxPrice']

        avg_price = restaurant['avgPrice']
        
        if min_price <= avg_price <= max_price:
            matching_restaurants.append(restaurant)
    
    return matching_restaurants


def get_recommend_restaurants_by_restrictions(userId):
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()
    
    matching_restaurants = []

    if not user_preferences or 'restrictions' not in user_preferences[0] or not user_preferences[0]['restrictions']:
        return matching_restaurants
    
    for restaurant in restaurants:
        if any(pref in restaurant['dietaryConditions'] for pref in user_preferences[0]['restrictions']):            
            matching_restaurants.append(restaurant) 
    
    return matching_restaurants


@app.route('/recommend/<string:userId>/<string:categoryFilter>', methods=['GET'])
def filter_recommend(userId, categoryFilter):
    if categoryFilter == 'tastes':
        return get_recommend_restaurants_by_tastes(userId)
    elif categoryFilter == 'price':
        return get_recommend_restaurants_by_price(userId)
    elif categoryFilter == 'restrictions':
        return get_recommend_restaurants_by_restrictions(userId)



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
