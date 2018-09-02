"""Bluprints for the Cart resource."""

from flask import Blueprint, jsonify, request

import lib.storage as storage
from lib.models.item import Item
from lib.errors import InvalidQuantityException, BaseCartException, \
    InvalidItemException

cart_blueprint = Blueprint("cart", __name__)


@cart_blueprint.route("/health")
def healthcheck():
    """Return a response which allows users know if API is up and running.."""
    return jsonify({"healthy": True})


@cart_blueprint.route("/cart", methods=["POST"])
def create_cart_endpoint():
    """Return a new Cart."""
    cart = storage.create_cart()

    return jsonify(cart.to_json()), 201


@cart_blueprint.route("/cart/<int:cart_id>", methods=["GET"])
def get_cart_endpoint(cart_id):
    """Return a Cart identified by `cart_id`."""
    cart = storage.get_cart(cart_id)

    return jsonify(cart.to_json()), 200


@cart_blueprint.route("/cart/<int:cart_id>/item", methods=["DELETE"])
def clear_cart_items_endpoint(cart_id):
    """Clear all items from the Cart `cart_id`."""
    cart = storage.get_cart(cart_id)

    cart.remove_all_items()

    return "", 204


@cart_blueprint.route("/cart/<int:cart_id>/item/<int:item_id>",
                      methods=["POST"])
def add_item_to_cart_endpoint(cart_id, item_id):
    """Add the Item `item_id` to the Cart `cart_id`."""
    cart = storage.get_cart(cart_id)

    request_body = request.get_json()

    if "quantity" not in request_body:
        raise InvalidQuantityException

    quantity = request_body.get("quantity")

    item = Item(item_id, quantity)

    cart.add_item(item)

    return jsonify(cart.to_json()), 200


@cart_blueprint.route("/cart/<int:cart_id>/item/<int:item_id>",
                      methods=["PUT"])
def update_item_to_cart_endpoint(cart_id, item_id):
    """Update the Item `item_id` on the Cart `cart_id`."""
    cart = storage.get_cart(cart_id)
    item = cart.get_item_by_id(item_id)

    request_body = request.get_json()

    if "quantity" not in request_body:
        raise InvalidQuantityException

    quantity = request_body.get("quantity")
    item.set_quantity(quantity)

    return jsonify(cart.to_json()), 200


@cart_blueprint.route("/cart/<int:cart_id>/item", methods=["POST"])
def add_multiple_items_to_cart_endpoint(cart_id):
    """Add multiple items to the cart.."""
    cart = storage.get_cart(cart_id)

    request_body = request.get_json()

    errors = []
    for item in request_body:

        try:
            if "quantity" not in item:
                raise InvalidQuantityException

            if "itemId" not in item:
                raise InvalidItemException

            quantity = item.get("quantity")
            item_id = item.get("itemId")

            item = Item(item_id, quantity)
            cart.add_item(item)
        except BaseCartException as error:
            errors.append(error.to_dict())

    response = {
        "cart": cart.to_json(),
        "_errors": errors
    }

    return jsonify(response), 200


@cart_blueprint.route("/cart/<int:cart_id>/item/<int:item_id>",
                      methods=["DELETE"])
def delete_item_from_cart_endpoint(cart_id, item_id):
    """Delete the Item `item_id` from the Cart `cart_id`."""
    cart = storage.get_cart(cart_id)

    item = cart.get_item_by_id(item_id)

    cart.remove_item(item)

    return "", 204
