"""Shopping Cart Example app."""
import os

from flask import Flask
from flask_cors import CORS
from blueprints.cart import cart_blueprint
from lib.errors import BaseCartException, error_handler


def main():
    """Initialise the Shopping Cart Example app."""
    app = Flask(__name__)

    app.register_blueprint(cart_blueprint)

    app.register_error_handler(BaseCartException, error_handler)

    CORS(app)

    app.run(
        host=os.environ.get('HOST', '0.0.0.0'),
        port=os.environ.get('PORT', '4567')
    )


if __name__ == "__main__":
    main()
