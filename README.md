# Shopping Cart Example

Cart Service that provides a selection of endpoints for interacting with a 
shopping cart. 

This code has been used as academic resource to explain REST FULL APIs.

### Endpoints


##### Service Healthcheck:
- Method: GET
- Path: `/health`
- Response Body:

```JSON
    {
        "healthy": true
    }
```


##### Create a new cart
- Method: POST
- Path: `/cart`
- Response Body:

```JSON
    {
        "cartId": 1,
        "cartItems": {}
    }
```


##### Get an existing cart:
- Method: POST
- Path: `/cart/<int:cart_id>`
- Response Body:

```JSON
    {
        "cartId": 1,
        "cartItems": {
          "1": {
            "itemId": 1,
            "quantity": 1
          }
        }
    }
```


##### Add an item to a cart:
- Method: POST
- Path: `/cart/<int:cart_id>/item/<int:item_id>`
- Request Body:

```JSON
    {
      "quantity": 1
    }
```

- Response Body:

```JSON
    {
        "cartId": 1,
        "cartItems": {
          "1": {
            "itemId": 1,
            "quantity": 1
          }
        }
    }
```

##### Update an item to a cart:
- Method: PUT
- Path: `/cart/<int:cart_id>/item/<int:item_id>`
- Request Body:

```JSON
    {
      "quantity": 10
    }
```

- Response Body:

```JSON
    {
        "cartId": 1,
        "cartItems": {
          "1": {
            "itemId": 1,
            "quantity": 10
          }
        }
    }
```


##### Add multiple items to a cart:
- Method: POST
- Path: `/cart/<int:cart_id>/item/`
- Request Body:

```JSON
    [
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
```

- Response Body:

```JSON
    {
        "_errors": [],
        "cart": {
            "cartId": 242,
            "cartItems": {
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
        }
    }
```

##### Delete an item from a cart:
- Method: DELETE
- Path: `/cart/<int:cart_id>/item/<int:item_id>`
- Responds with 204 No Content and an empty body


##### Delete all items from a cart:
- Method: DELETE
- Path: `/cart/<int:cart_id>/item`
- Responds with 204 No Content and an empty body

### Running

The service is dockerised, run `docker-compose up` to bring up the service on 
http://localhost:4567

##### Make file:

The app contains a make file which contains some useful commands:

- make venv - Create a virtual environment
- make start_docker and make stop_docker: Start and stop docker.
- make lint: Runs the code quality / linting tools across all applications.
- make test - Run all tests
- make test_unit - Run all unit tests
- make test_integration - Run all integration tests
- make build_docs - Generates Sphinx documentation in /docs and built it in /site


### Things that can be improved:

* Take care about the concurrency problems. For instance, add currency control 
  when we are updating the quantity of the items.

* I would like to implement in a most RESTFUL way the functionality to add
  multiple items on the cart. In my current implementation I implemented a 
  simple solution, but it is not REST FULL, but I'm sure also is the most 
  typical solution we can find in all implementations. 
  
  My current solution basically consist on add an endpoint to add multiple 
  items,then it iterates all items received in the body and validate them. If 
  an item  is correct, then it's added to the cart, if not we capture the 
  error. Finally, the response returns the cart updated with the items added, 
  and a list of errors with the errors in the items which failed. I think 
  it's not a good solution, as breaks the RESTFUL style, and makes hard to 
  identify and handle the errors.  
  
  I think a better solution will be to implement a batch endpoint that allows 
  us to do multiple requests in a single one. It will allows us to treat each 
  request individually, so we also will be able to return individual errors 
  per each request. So, we should call a batch with multiple add single item 
  requests. I was thinking to implement something as 
  Google <https://developers.google.com/drive/api/v3/batch> and 
  Facebook <https://developers.facebook.com/docs/graph-api/making-multiple-requests/> 
  proposed in their APIs.

* In the code you can see some code which is duplicated across multiple 
  endpoints (e.g the response --> jsonfy(content), status_code). I think, that 
  changing the endpoints to work in a class-based instead of functions, will 
  allow us to reduce the duplicate code, creating a parent class with common 
  code. Something like, have a BaseController, which some methods like 
  validate_request(), get_json_response(), ... 
  Something like http://flask.pocoo.org/docs/0.12/views/ using the MethodView, 
  but customizing it to our requirements.
