# Angular UI Server

This project contains a FastAPI server that serves the Angular UI application.

## Setup Instructions

1. **Build the Angular Application**
   ```bash
   cd ui
   npm install
   ng build
   ```
   
   Or for development builds:
   ```bash
   ng build --configuration development
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Server**
   ```bash
   python server.py
   ```

The server will start on port 7000 by default (configurable in `settings.json`).

## Configuration

The server can be configured using the `settings.json` file:

```json
{
  "port": 7000
}
```

Change the `port` value to use a different port number.

## Notes

- Make sure to build the Angular application before starting the server
- The server expects the built files to be in `ui/dist/ui/`
- The server handles SPA routing by serving `index.html` for non-existent routes