import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import router

# FastAPI application initialization
app = FastAPI(
    title="ComicCraft AI",
    description="AI Comic Story Creator powered by Gemini and Stable Diffusion",
    version="1.0.0"
)

# Ensure required runtime output directories exist
os.makedirs(os.path.join("static", "panels"), exist_ok=True)
os.makedirs(os.path.join("static", "exports"), exist_ok=True)

# Mount static folder for images, CSS, and downloaded files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include the routes from app.routes
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)