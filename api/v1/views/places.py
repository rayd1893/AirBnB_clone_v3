#!/usr/bin/python3
'''
Import Blueprint to create routes for Amenity
'''
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models import city
from models.amenity import Amenity
from models.city import City
from models.user import User
from models.place import Place
from models.state import State


@app_views.route('/cities/<city_id>/places', methods=['GET'],
                 strict_slashes=False)
def all_places(city_id):
    '''Get all Places from a city'''
    city = storage.get(City, city_id)
    places = []

    if city is None:
        abort(404)
    for place in city.places:
        places.append(place.to_dict())
    return jsonify(places)


@app_views.route('/places/<place_id>', methods=['GET'], strict_slashes=False)
def show_place(place_id):
    '''Show a place'''
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    return jsonify(place.to_dict())


@app_views.route('/places/<place_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_place(place_id):
    '''Delete a place'''
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    place.delete()
    storage.save()
    return jsonify({})


@app_views.route('/cities/<city_id>/places/', methods=['POST'],
                 strict_slashes=False)
def create_place(city_id):
    '''Create a place'''
    city = storage.get(City, city_id)
    if city is None:
        abort(404)
    req = request.get_json()
    if req is None:
        abort(400, {'Not a JSON'})
    if 'user_id' not in req:
        abort(400, {'Missing user_id'})
    user = storage.get(User, req['user_id'])
    if user is None:
        abort(404)
    if 'name' not in req:
        abort(400, {'Missing name'})
    req['city_id'] = city_id
    new_place = Place(**req)
    storage.new(new_place)
    storage.save()
    return new_place.to_dict(), 201


@app_views.route('/places/<place_id>', methods=['PUT'], strict_slashes=False)
def update_place(place_id):
    '''Update a place'''
    ignore = ['id', 'user_id', 'city_id', 'created_at', 'updated_at']
    place = storage.get(Place, place_id)
    if place is None:
        abort(404)
    req = request.get_json()
    if req is None:
        abort(400, {'Not a JSON'})
    for k, v in req.items():
        if k not in ignore:
            setattr(place, k, v)
    place.save()
    return make_response(jsonify(place.to_dict()), 200)


@app_views.route('/places_search', methods=['POST'], strict_slashes=False)
def places_search():
    """Retrieves all places depending of the JSON
    in the body of the request"""
    if request.get_json() is None:
        abort(400, description="Not a JSON")
    http_request = request.get_json()
    if http_request and len(http_request):
        states = http_request.get('states', None)
        cities = http_request.get('cities', None)
        amenities = http_request.get('amenities', None)
    placesList = []
    if not http_request or not len(http_request) or (
            not states and
            not cities and
            not amenities):
        places = storage.all(Place).values()
        for place in placesList:
            placesList.append(place.to_dict())
        return jsonify(placesList)
    if states:
        statesObj = [storage.get(State, stid) for stid in states]
        for state in statesObj:
            if state:
                for city in state.cities:
                    if city:
                        for place in city.places:
                            placesList.append(place)
    if cities:
        citiesObj = [storage.get(City, ciid) for ciid in cities]
        for city in citiesObj:
            if city:
                for place in city.places:
                    placesList.append(place)
    if amenities:
        amenititesObj = [storage.get(Amenity, amid) for amid in amenities]
        if not placesList:
            placesList = storage.all(Place).values()
        newList = []
        for place in placesList:
            for amenity in amenititesObj:
                if all(amenity in place.amenities):
                    newList.append(place)
        placesList = newList

    places = []
    for place in placesList:
        dictplaces = place.to_dict()
        dictplaces.pop('amenities', None)
        places.append(dictplaces)

    return jsonify(places)
