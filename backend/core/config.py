import os
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the backend directory (current working directory)
load_dotenv()

# Direct access to environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_CLOUD_API_KEY = os.getenv("LLAMA_CLOUD_API_KEY")

print(f"[CONFIG] OPENAI_API_KEY loaded: {bool(OPENAI_API_KEY)} - {OPENAI_API_KEY[:30] if OPENAI_API_KEY else 'NONE'}...")

class Config:
    # Direct references to loaded environment variables
    OPENAI_KEY = OPENAI_API_KEY
    LLAMA_CLOUD_KEY = LLAMA_CLOUD_API_KEY
    
    # Financial Constants (India Specific)
    INFLATION_RATE = 0.06  # 6% Average
    EQUITY_EXPECTED_RETURN = 0.12
    DEBT_EXPECTED_RETURN = 0.07
    
    # Avataar.ai Config
    SPATIAL_SCALE_FACTOR = 0.0001 # To scale ₹ crores into 3D units