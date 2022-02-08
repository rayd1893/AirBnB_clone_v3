#!/usr/bin/python3
""" Review object that handles all default RESTFul API actions """
from api.v1.views import app_views
from flask import abort, jsonify, make_response, request
from models import storage
from models.review import Review
from models.user import User
from models.place import Place


@app_views.route('/places/<place_id>/reviews', methods=['GET'],
                 strict_slashes=False)
def get_all_reviews(place_id):
    """Retrieves the list of all reviews"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    allReviewsList = [review.to_dict() for review in place.reviews]
    return jsonify(allReviewsList)


@app_views.route('/reviews/<review_id>', methods=['GET'],
                 strict_slashes=False)
def get_review(review_id):
    """Retrieves a review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    return jsonify(review.to_dict())


@app_views.route('/reviews/<review_id>', methods=['DELETE'],
                 strict_slashes=False)
def delete_review(review_id):
    """Deletes a review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)

    review.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/places/<place_id>/reviews', methods=['POST'],
                 strict_slashes=False)
def post_review(place_id):
    """post a review"""
    place = storage.get(Place, place_id)
    if not place:
        abort(404)
    if not request.get_json():
        abort(400, description="Not a JSON")
    http_request = request.get_json()
    if 'user_id' not in http_request:
        abort(400, description="Missing user_id")
    user = storage.get(User, http_request['user_id'])
    if not user:
        abort(404)
    if 'text' not in http_request:
        abort(400, description="Missing text")
    http_request['place_id'] = place_id
    newReview = Review(**http_request)
    newReview.save()
    return make_response(jsonify(newReview.to_dict()), 201)


@app_views.route('/reviews/<review_id>', methods=['PUT'],
                 strict_slashes=False)
def update_review(review_id):
    """update a review"""
    review = storage.get(Review, review_id)
    if not review:
        abort(404)
    if not request.get_json:
        abort(400, description="Not a JSON")
    http_request = request.get_json()
    ignore = ['id', 'user_id', 'place_id', 'created_at', 'updated_at']
    for key, value in http_request.items():
        if key not in ignore:
            setattr(review, key, value)
    storage.save()
    return make_response(jsonify(review.to_dict()), 200)
