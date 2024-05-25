from flask import Flask, jsonify
from firebase_admin import firestore, initialize_app, credentials

app = Flask(__name__)

cred = credentials.Certificate("key.json")
initialize_app(cred)


def getRestaurants():
    restaurants = []
    try:
        restaurant_docs = firestore.client().collection("restaurants").get()

        for doc in restaurant_docs:
            restaurant_data = doc.to_dict()
            restaurant_data["docId"] = doc.id
            restaurants.append(restaurant_data)

    except Exception as e:
        print(f"Error al obtener la lista de restaurantes: {e}")
        return None

    return restaurants


def getUserPreferences(user):
    prefs = []
    try:
        user_prefs = (
            firestore.client()
            .collection("users")
            .document(user)
            .collection("preferences")
            .get()
        )

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

    if (
        not user_preferences
        or "tastes" not in user_preferences[0]
        or not user_preferences[0]["tastes"]
    ):
        return matching_restaurants

    for restaurant in restaurants:
        if any(
            pref in restaurant["foodType"] for pref in user_preferences[0]["tastes"]
        ):
            matching_restaurants.append(restaurant)

    return matching_restaurants


def get_recommend_restaurants_by_price(userId):
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()

    matching_restaurants = []

    if (
        not user_preferences
        or "priceRange" not in user_preferences[0]
        or not user_preferences[0]["priceRange"]
    ):
        return matching_restaurants

    for restaurant in restaurants:

        min_price = user_preferences[0]["priceRange"]["minPrice"]
        max_price = user_preferences[0]["priceRange"]["maxPrice"]

        avg_price = restaurant["avgPrice"]

        if min_price <= avg_price <= max_price:
            matching_restaurants.append(restaurant)

    return matching_restaurants


def get_recommend_restaurants_by_restrictions(userId):
    user_preferences = getUserPreferences(userId)
    restaurants = getRestaurants()

    matching_restaurants = []

    if (
        not user_preferences
        or "restrictions" not in user_preferences[0]
        or not user_preferences[0]["restrictions"]
    ):
        return matching_restaurants

    for restaurant in restaurants:
        if any(
            pref in restaurant["dietaryConditions"]
            for pref in user_preferences[0]["restrictions"]
        ):
            matching_restaurants.append(restaurant)

    return matching_restaurants


@app.route("/recommend/<string:userId>/<string:categoryFilter>", methods=["GET"])
def filter_recommend(userId, categoryFilter):
    if categoryFilter == "tastes":
        return get_recommend_restaurants_by_tastes(userId)
    elif categoryFilter == "price":
        return get_recommend_restaurants_by_price(userId)
    elif categoryFilter == "restrictions":
        return get_recommend_restaurants_by_restrictions(userId)


@app.route("/most_liked/<string:userLat>/<string:userLong>", methods=["GET"])
def get_most_liked_restaurants(userLat, userLong):

    restaurants = getRestaurants()
    sorted_restaurants = sorted(restaurants, key=lambda x: x["likes"], reverse=True)
    nearby_restaurants = [
        restaurant
        for restaurant in sorted_restaurants
        if is_nearby_restaurant(restaurant, userLat, userLong)
    ]

    return nearby_restaurants[:5]


def is_nearby_restaurant(item, userLat, userLong):

    restaurant_lat = float(item["latitud"])
    restaurant_long = float(item["longitud"])

    def calculate_distance_in_km(lat1, lon1, lat2, lon2):
        R = 6371.0  # Radius of the Earth in kilometers

        lat1_rad = radians(lat1)
        lon1_rad = radians(lon1)
        lat2_rad = radians(lat2)
        lon2_rad = radians(lon2)

        dlon = lon2_rad - lon1_rad
        dlat = lat2_rad - lat1_rad

        a = sin(dlat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        distance = R * c
        return distance

    distance = calculate_distance_in_km(
        userLat, userLong, restaurant_lat, restaurant_long
    )

    return distance <= 0.5

@app.route("/dishes_by_price_range/<string:minPrice>/<string:maxPrice><string:userLat>/<string:userLong>", methods=["GET"])
def get_dishes_by_price_range_endpoint(minPrice, maxPrice, userLat, userLong):
    min_price = float(minPrice)
    max_price = float(maxPrice)
    user_lat = float(userLat)
    user_long = float(userLong)

    dishes = get_dishes_by_price_range(min_price, max_price, user_lat, user_long)
    return dishes


def get_dishes_by_price_range(min_price, max_price, user_lat, user_long):
    dishes = []

    try:
        restaurant_docs = firestore.client().collection("restaurants").get()

        for doc in restaurant_docs:
            restaurant_data = doc.to_dict()
            restaurant_data["docId"] = doc.id

            if is_nearby_restaurant(restaurant_data, user_lat, user_long):
                dish_docs = (
                    firestore.client()
                    .collection("restaurants")
                    .document(doc.id)
                    .collection("dishes")
                    .get()
                )

                for dish in dish_docs:
                    dish_data = dish.to_dict()
                    dish_data["restaurantId"] = doc.id
                    dish_data["restaurantName"] = restaurant_data["name"]

                    if min_price <= dish_data["price"] <= max_price:
                        dishes.append(dish_data)

    except Exception as e:
        print(f"Error al obtener los platos: {e}")
        return None

    return dishes

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
