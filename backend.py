from flask import Flask, jsonify
from firebase_admin import firestore, initialize_app, credentials

app = Flask(__name__)

# Initialize Firebase with project ID
cred = credentials.Certificate('key.json')
initialize_app(cred)

# Mock list of preferences
mock_preferences = ['italian', 'nearby']


def getRestaurants():
    restaurants = []
    restaurant_docs = firestore.client().collection('restaurants').get()
    for doc in restaurant_docs:
        restaurants.append(doc.to_dict())
    
    return restaurants

userId = "8GjEXLg6ZrdN1pW2OSPWA9CIpVG3"

def getUserPreferences():
 
    prefs = []
    user_prefs = firestore.client().collection('users').document(userId).collection('preferences').get()
    
    for pref in user_prefs:
        prefs.append(pref.to_dict())
              
    return prefs

@app.route('/recommend', methods=['GET'])
def get_recommend_restaurants(user_preferences, restaurants):
    
    getUserPreferences(userId)
    
    matching_restaurants = []
    for restaurant in restaurants:
        if any(pref in restaurant['characteristics'] for pref in user_preferences):
            matching_restaurants.append(restaurant['name'])  # Assuming the restaurant document has a 'name' field
    
    return matching_restaurants

if __name__ == '__main__':
    app.run(debug=True)
