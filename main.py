from dotenv import load_dotenv
from src.api import app

if __name__ == '__main__':
    load_dotenv()
    app.run()
