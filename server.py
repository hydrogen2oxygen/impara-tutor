import json, sys, os
from pathlib import Path

from openai import OpenAI

from py.domains.ImparaDomains import User, UserCreate
from py.domains.OpenAIRequest import OpenAIRequest
from py.services.databaseService import ImparaDB

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

class AngularUIServer:
    def __init__(self):
        self.settings = self.load_settings()
        self.dist_folder = Path(__file__).parent / "ui" / "dist" / "ui"
        if not self.dist_folder.exists():
            print(f"Warning: Dist folder does not exist at {self.dist_folder}")
            print("Make sure to build the Angular app first using 'ng build'")
            self.dist_folder.mkdir(parents=True, exist_ok=True)

        self.app = FastAPI(title="Angular UI Server", version="1.0.0")
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.app.mount("/static", StaticFiles(directory=self.dist_folder), name="static")
        self._add_routes()
        self.PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
        self.db = ImparaDB(os.path.join(self.PROJECT_ROOT, 'data/impara.db'))

    def load_settings(self):
        settings_path = Path(__file__).parent / "settings.json"
        if settings_path.exists():
            with open(settings_path, "r") as f:
                return json.load(f)
        else:
            return {"port": 7000}

    def translate(self, text, to_lang, from_lang=None, api_url="http://localhost:8000/translate", timeout=10.0):
        payload = {"text": text, "to": to_lang}
        if from_lang:
            payload["from"] = from_lang
        headers = {"Content-Type": "application/json; charset=utf-8"}
        response = requests.post(
            api_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=headers,
            timeout=timeout,
        )
        response.raise_for_status()
        return response.json()

    def _extract_output_text(self, data):
        if isinstance(data, dict) and isinstance(data.get("output_text"), str):
            return data["output_text"]
        try:
            for item in data.get("output", []):
                for c in item.get("content", []):
                    if c.get("type") == "output_text" and isinstance(c.get("text"), str):
                        return c["text"]
        except Exception:
            pass
        return ""

    def _add_routes(self):
        @self.app.get('/openAiModels')
        def openAiModels():
            openAiKey = self.settings.get("OpenAI_API_Key")
            if openAiKey is None:
                return {'error': 'No OpenAI key found'}
            client = OpenAI(api_key=openAiKey)
            try:
                models = client.models.list()
                model_names = [model.id for model in models.data]
                return model_names
            except Exception as e:
                return {"error": str(e)}

        @self.app.post('/openAi')
        def openAiInterpretation(request: OpenAIRequest):
            openAiKey = self.settings.get("OpenAI_API_Key")
            if openAiKey is None:
                return {'error': 'No OpenAI key found'}
            client = OpenAI(api_key=openAiKey)
            try:
                response = client.chat.completions.create(
                    model=request.model,
                    messages=[
                        {"role": "system", "content": request.system},
                        {"role": "user", "content": request.prompt}
                    ],
                    temperature=0.5
                )
                detailed_output = {
                    "id": response.id,
                    "model": response.model,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    },
                    "message": response.choices[0].message.content
                }
                return detailed_output
            except Exception as e:
                return {"error": str(e)}

        @self.app.post("/api/openai/respond")
        async def openai_respond(req: OpenAIRequest):
            api_key = self.settings.get("OpenAI_API_Key")
            if not api_key or api_key == "your-api-key-here":
                raise HTTPException(
                    status_code=500,
                    detail="OpenAI_API_Key missing in settings.json"
                )
            payload = {
                "model": req.model,
                "input": [
                    {
                        "role": "system",
                        "content": [
                            { "type": "input_text", "text": req.system }
                        ]
                    },
                    {
                        "role": "user",
                        "content": [
                            { "type": "input_text", "text": req.prompt }
                        ]
                    }
                ],
                "text": { "format": { "type": "json_object" } }
            }
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    response = await client.post(
                        "https://api.openai.com/v1/responses",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"OpenAI error: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"OpenAI request failed: {str(e)}"
                )
            output_text = self._extract_output_text(data)
            if not output_text:
                raise HTTPException(
                    status_code=502,
                    detail="OpenAI response contained no output_text"
                )
            return {
                "raw": output_text
            }

        @self.app.post("/api/translate")
        def translate_endpoint(request: dict):
            text = request.get("text")
            to_lang = request.get("to")
            from_lang = request.get("from", None)
            if not text or not to_lang:
                raise HTTPException(status_code=400, detail="Missing 'text' or 'to' parameter")
            try:
                result = self.translate(text, to_lang=to_lang, from_lang=from_lang)
                return result
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/user")
        def create_user(user: UserCreate):
            try:
                self.db.insert_user(user)
                return self.db.get_user_by_name(user.display_name)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/user")
        def update_user(user: User):
            try:
                self.db.delete_user(user.id)
                updated_user = UserCreate(
                    display_name=user.display_name,
                    email=user.email,
                    bio=user.bio,
                    avatar_path=user.avatar_path
                )
                self.db.insert_user(updated_user)
                return self.db.get_user_by_name(user.display_name)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/user")
        def list_users():
            try:
                users = self.db.list_users()
                return [
                    {
                        "id": u.id,
                        "display_name": u.display_name,
                        "email": u.email,
                        "bio": u.bio,
                        "avatar_path": u.avatar_path,
                        "created_at": u.created_at,
                        "last_active_at": u.last_active_at,
                    }
                    for u in users
            ]
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/user/{user_id}")
        def delete_user(user_id: int):
            try:
                self.db.delete_user(user_id)
                return {"message": f"User with id {user_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/")
        def read_root():
            index_path = self.dist_folder / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"error": "Index file not found. Please build the Angular app first."}

        @self.app.get("/{full_path:path}")
        def read_static(full_path: str):
            if full_path.startswith("api/"):
                raise HTTPException(status_code=404)
            file_path = self.dist_folder / full_path
            if file_path.exists() and file_path.is_file():
                return FileResponse(file_path)
            index_path = self.dist_folder / "index.html"
            if index_path.exists():
                return FileResponse(index_path)
            return {"error": "Index file not found. Please build the Angular app first."}



class TokensRequest(BaseModel):
    text: str
    model: str = "gpt-4o-mini"

if __name__ == "__main__":
    import uvicorn
    server = AngularUIServer()
    port = server.settings.get("port", 7000)
    print(f"Starting server on port {port}")
    print(f"Serving Angular app from: {server.dist_folder}")
    uvicorn.run(server.app, host="localhost", port=port)
