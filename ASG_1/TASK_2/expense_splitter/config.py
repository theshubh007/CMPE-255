from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
