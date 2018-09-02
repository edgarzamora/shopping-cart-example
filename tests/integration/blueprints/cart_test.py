import pytest
from flask import Flask

from blueprints.cart import cart_blueprint
from lib.errors import BaseCartException, error_handler


@pytest.fixture(scope="module")
def test_app():
    test_app = Flask(__name__)

    test_app.register_blueprint(cart_blueprint)

    test_app.register_error_handler(BaseCartException, error_handler)

    yield test_app


@pytest.fixture(scope="module")
def test_client(test_app):
    yield test_app.test_client()


@pytest.fixture()
def test_cart_id(test_client):
    response = test_client.post('/cart')

    cart = response.json

    yield cart.get('cartId')


def test_healthcheck(test_client):
    response = test_client.get("/health")

    assert response.content_type == 'application/json'

    assert response.json == {
        "healthy": True
    }

    assert response.status_code == 200


def test_create_cart_endpoint(test_client):
    response = test_client.post("/cart")

    assert response.content_type == 'application/json'

    cart = response.json

    assert type(cart.get('cartId')) is int
    assert cart.get('cartItems') == {}
    assert response.status_code == 201


def test_get_cart_endpoint(test_client, test_cart_id):
    response = test_client.get('/cart/{}'.format(test_cart_id))

    assert response.content_type == 'application/json'

    cart = response.json

    assert cart.get('cartId') == test_cart_id
    assert cart.get('cartItems') == {}
    assert response.status_code == 200


def test_get_cart_endpoint_cart_doesnt_exist(test_client):
    response = test_client.get('/cart/{}'.format(1))

    assert response.content_type == 'application/json'
    assert response.status_code == 404

    assert response.json == {
        "error": "Cart 1 not found"
    }


def test_add_item_to_cart_endpoint(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})

    assert response.content_type == 'application/json'

    cart = response.json

    assert len(cart.get('cartItems')) == 1
    assert cart.get('cartItems').get("1") == {
        "itemId": 1,
        "quantity": 1
    }


def test_add_item_to_cart_endpoint_no_quantity_provided(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={})

    assert response.content_type == 'application/json'
    assert response.status_code == 400

    assert response.json == {
        "error": "Invalid quantity"
    }


def test_add_item_to_cart_endpoint_invalid_quantity_provided_negative_quantity(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": -1})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Invalid quantity"
    }
    assert response.status_code == 400


def test_add_item_to_cart_endpoint_invalid_quantity_provided_string_quantity(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 'string'})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Invalid quantity"
    }
    assert response.status_code == 400


def test_update_item_quantity_endpoint_no_cart_found(test_client):
    response = test_client.put('/cart/{}/item/{}'.format(2, 1), json={})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Cart 2 not found"
    }
    assert response.status_code == 404


def test_update_item_quantity_endpoint_no_item_found(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200

    response = test_client.put('/cart/{}/item/{}'.format(test_cart_id, 2), json={})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Item 2 not found in cart"
    }
    assert response.status_code == 404


def test_update_item_quantity_endpoint_no_quantity_provided(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200

    response = test_client.put('/cart/{}/item/{}'.format(test_cart_id, 1), json={})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Invalid quantity"
    }
    assert response.status_code == 400


def test_update_item_quantity_endpoint_invalid_quantity_provided_negative_quantity(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200

    response = test_client.put('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": -1})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Invalid quantity"
    }
    assert response.status_code == 400


def test_update_item_quantity_endpoint_invalid_quantity_provided_string_quantity(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200

    response = test_client.put('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 'string'})

    assert response.content_type == 'application/json'

    assert response.json == {
        "error": "Invalid quantity"
    }
    assert response.status_code == 400


def test_update_item_quantity_endpoint_valid_quantity(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200

    response = test_client.put('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 5})

    assert response.content_type == 'application/json'

    cart = response.json

    assert len(cart.get('cartItems')) == 1
    assert cart.get('cartItems').get("1") == {
        "itemId": 1,
        "quantity": 5
    }
    assert response.status_code == 200


def test_add_multiple_items_to_cart_endpoint(test_client, test_cart_id):
    response = test_client.post(
        '/cart/{}/item'.format(test_cart_id),
        json=[
            {
                "itemId": 2,
                "quantity": 1
            },
            {
                "itemId": 3,
                "quantity": 1
            },
            {
                "itemId": 4,
                "quantity": 1
            },
            {
                "itemId": 5,
                "quantity": 1
            }
        ]
    )

    assert response.status_code == 200
    assert len(response.json) == 2
    assert "cart" in list(response.json)
    assert response.json["cart"].get("cartId") == test_cart_id
    assert response.json["cart"].get("cartItems") == {
        "2": {
            "itemId": 2,
            "quantity": 1
        },
        "3": {
            "itemId": 3,
            "quantity": 1
        },
        "4": {
            "itemId": 4,
            "quantity": 1
        },
        "5": {
            "itemId": 5,
            "quantity": 1
        }
    }
    assert "_errors" in list(response.json)
    assert response.json.get("_errors") == []


def test_add_multiple_items_to_cart_endpoint_some_invalid_items(test_client, test_cart_id):
    response = test_client.post(
        '/cart/{}/item'.format(test_cart_id),
        json=[
            {
                "itemId": 2
            },
            {
                "itemId": 3,
                "quantity": 1
            },
            {
                "quantity": 1
            },
            {
                "itemId": 5,
                "quantity": 1
            }
        ]
    )

    assert response.status_code == 200
    assert len(response.json) == 2
    assert "cart" in list(response.json)
    assert response.json["cart"].get("cartId") == test_cart_id
    assert response.json["cart"].get("cartItems") == {
        "3": {
            "itemId": 3,
            "quantity": 1
        },
        "5": {
            "itemId": 5,
            "quantity": 1
        }
    }
    assert "_errors" in list(response.json)
    assert response.json.get("_errors") == [
        {'error': 'Invalid quantity'}, {'error': 'Invalid item format'}
    ]


def test_delete_item_from_cart_endpoint(test_client, test_cart_id):
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})

    assert response.status_code == 200

    response = test_client.delete('/cart/{}/item/{}'.format(test_cart_id, 1))

    assert response.status_code == 204
    assert len(response.data) == 0

    response = test_client.get('/cart/{}'.format(test_cart_id))

    assert response.status_code == 200
    assert response.json.get('cartItems') == {}


def test_delete_item_from_cart_endpoint_item_doesnt_exist(test_client, test_cart_id):
    response = test_client.delete('/cart/{}/item/{}'.format(test_cart_id, 1))

    assert response.content_type == 'application/json'
    assert response.status_code == 404

    assert response.json == {
        "error": "Item 1 not found in cart"
    }


def test_clear_cart_items_endpoint(test_client, test_cart_id):
    # Add items on the cart
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 1), json={"quantity": 1})
    assert response.status_code == 200
    response = test_client.post('/cart/{}/item/{}'.format(test_cart_id, 2), json={"quantity": 1})
    assert response.status_code == 200

    # Clear all items from the cart
    response = test_client.delete('/cart/{}/item'.format(test_cart_id))

    assert response.status_code == 204
    assert len(response.data) == 0

    response = test_client.get('/cart/{}'.format(test_cart_id))

    assert response.status_code == 200
    assert response.json.get('cartItems') == {}
