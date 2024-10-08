from flask import Flask
from flask_swagger_ui import get_swaggerui_blueprint
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


# Create the Flask application instance
app = Flask(__name__)
limiter = Limiter(
    get_remote_address,
    app=app
)



SWAGGER_URL = "/api/docs"  # URL for exposing Swagger UI (without trailing '/')
API_URL = "/static/swagger.json"  # Our API url (can of course be a local resource)

# Call factory function to create our blueprint
swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,  # Swagger UI static files will be mapped to '{SWAGGER_URL}/dist/'
    API_URL,
    config={"app_name": "OrderSync"},
)

app.register_blueprint(swaggerui_blueprint)


# Define the default route that returns "Home"
@app.route("/")
def home():
    return "Home"


# Import all handlers to manage different routes and models
from handler import *

# Run the Flask app when this script is executed directly
if __name__ == "__main__":
    # Uncomment the following line to run the app on all network interfaces (e.g., in production)
    app.run(host="0.0.0.0", port=3000)

    # Run the app in debug mode for development
    # app.run(debug=True)
