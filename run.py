import os
from dotenv import load_dotenv
from server import create_app

if __name__ == "__main__":
  # load_dotenv()
  app = create_app(os.getenv('FLASK_CONFIG') or 'default')
  app.run(host='0.0.0.0', port=os.getenv('PORT'), load_dotenv=True)
