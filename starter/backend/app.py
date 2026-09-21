import os
import sys

# Add the backend root directory to the module path.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask  # noqa: E402
from flask_cors import CORS  # noqa: E402
from movies.movies_api import movies_api  # noqa: E402

app = Flask(__name__)
CORS(app)
app.register_blueprint(movies_api)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
