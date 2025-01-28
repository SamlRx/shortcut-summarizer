import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the logger
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
