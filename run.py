import os
from server import create_app
from dotenv import load_dotenv

load_dotenv()
app = create_app()
