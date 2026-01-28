import json
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware


def load_settings():
    """Load settings from settings.json file."""
    settings_path = Path(__file__).parent / "settings.json"
    if settings_path.exists():
        with open(settings_path, "r") as f:
            return json.load(f)
    else:
        # Return default settings if file doesn't exist
        return {"port": 7000}


def create_app():
    """Create and configure the FastAPI application."""
    settings = load_settings()

    # Define the path to the Angular dist folder
    dist_folder = Path(__file__).parent / "ui" / "dist" / "ui"

    if not dist_folder.exists():
        print(f"Warning: Dist folder does not exist at {dist_folder}")
        print("Make sure to build the Angular app first using 'ng build'")
        # Create a temporary empty directory for the static files mount
        dist_folder.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="Angular UI Server", version="1.0.0")

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Serve static files from the dist folder
    app.mount("/static", StaticFiles(directory=dist_folder), name="static")

    @app.get("/")
    def read_root():
        """Serve the main index.html file."""
        index_path = dist_folder / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return {"error": "Index file not found. Please build the Angular app first."}

    @app.get("/{full_path:path}")
    def read_static(full_path: str):
        """Serve static files or fallback to index.html for SPA routing."""
        file_path = dist_folder / full_path

        # If the requested file exists, serve it
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        # Otherwise, serve index.html to handle SPA routing
        index_path = dist_folder / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        else:
            return {"error": "Index file not found. Please build the Angular app first."}

    return app, settings


if __name__ == "__main__":
    import uvicorn
    
    app, settings = create_app()
    
    port = settings.get("port", 7000)
    
    print(f"Starting server on port {port}")
    print(f"Serving Angular app from: {Path(__file__).parent / 'ui' / 'dist' / 'ui'}")
    
    uvicorn.run(app, host="0.0.0.0", port=port)