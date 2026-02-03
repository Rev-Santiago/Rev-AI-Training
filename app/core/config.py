import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Define variables for the rest of the app to use
MODEL_NAME = os.getenv("MODEL_NAME", "gemma") # "gemma" is the fallback