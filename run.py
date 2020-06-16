import os
from server import create_app

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
