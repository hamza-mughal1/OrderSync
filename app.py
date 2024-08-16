from flask import Flask

# Create the Flask application instance
app = Flask(__name__)


# Define the default route that returns "Home"
@app.route("/")
def home():
    return "Home"


# Import all handlers to manage different routes and models
from handler import *

# Run the Flask app when this script is executed directly
if __name__ == "__main__":
    # Uncomment the following line to run the app on all network interfaces (e.g., in production)
    # app.run(host="0.0.0.0", port=3000)

    # Run the app in debug mode for development
    app.run(debug=True)
