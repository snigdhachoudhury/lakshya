# Load environment immediately, before any other imports
import os
from dotenv import load_dotenv
load_dotenv()
print(f"[MAIN] .env loaded. OPENAI_API_KEY exists: {bool(os.getenv('OPENAI_API_KEY'))}")

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router
import uvicorn

app = FastAPI(title="Project Lakshya: AI Money Mentor")

# --- 1. MIDDLEWARE (Crucial for Hackathon Demos) ---
# This allows your React frontend (usually port 3000) to call this Backend (port 8000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins for development/demo
    allow_credentials=True,
    allow_methods=["*"],  # Allows GET, POST, etc.
    allow_headers=["*"],
)

# --- 2. ROUTES ---
# This pulls in all the logic from api/routes.py (Upload, Fire, Health Score)
# Your endpoints will now be: 
# http://localhost:8000/api/v1/analyze-portfolio
# http://localhost:8000/api/v1/project-fire
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "project": "Lakshya AI",
        "status": "Online",
        "message": "Spatial Finance Engine Ready"
    }

# --- 3. EXECUTION ---
if __name__ == "__main__":
    # We use "main:app" string format to allow for the 'reload' feature during coding
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)