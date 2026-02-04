import json, sys, os
from pathlib import Path

from openai import OpenAI

from py.domains.OpenAIRequest import OpenAIRequest

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests


def load_settings():
    """Load settings from settings.json file."""
    settings_path = Path(__file__).parent / "settings.json"
    if settings_path.exists():
        with open(settings_path, "r") as f:
            return json.load(f)
    else:
        return {"port": 7000}

def translate(
        text: str,
        to_lang: str,
        from_lang: str | None = None,
        api_url: str = "http://localhost:8000/translate",
        timeout: float = 10.0,
) -> dict:
    """
    Translate text using the Free Translate API.

    :param text: Text to translate (Unicode safe)
    :param to_lang: Target language code, e.g. 'en'
    :param from_lang: Source language code, e.g. 'ru' (optional, auto-detect if None)
    :param api_url: Translation API endpoint
    :param timeout: Request timeout in seconds
    :return: Parsed JSON response from API
    """

    payload = {
        "text": text,
        "to": to_lang,
    }

    if from_lang:
        payload["from"] = from_lang

    headers = {
        "Content-Type": "application/json; charset=utf-8"
    }

    response = requests.post(
        api_url,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers=headers,
        timeout=timeout,
    )

    response.raise_for_status()
    return response.json()


class TokensRequest(BaseModel):
    text: str
    model: str = "gpt-4o-mini"


def _extract_output_text(data: dict) -> str:
    # Responses API often provides output_text; otherwise fall back to output[...]
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


def create_app():
    """Create and configure the FastAPI application."""
    settings = load_settings()

    dist_folder = Path(__file__).parent / "ui" / "dist" / "ui"
    if not dist_folder.exists():
        print(f"Warning: Dist folder does not exist at {dist_folder}")
        print("Make sure to build the Angular app first using 'ng build'")
        dist_folder.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="Angular UI Server", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=dist_folder), name="static")

    @app.get("/")
    def read_root():
        index_path = dist_folder / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Index file not found. Please build the Angular app first."}

    @app.get("/{full_path:path}")
    def read_static(full_path: str):
        file_path = dist_folder / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)

        index_path = dist_folder / "index.html"
        if index_path.exists():
            return FileResponse(index_path)
        return {"error": "Index file not found. Please build the Angular app first."}

    @app.get('/openAiModels')
    def openAiModels():
        openAiKey = settings.get("OpenAI_API_Key")
        if openAiKey is None:
            return {'error': 'No OpenAI key found'}
        client = OpenAI(api_key=openAiKey)
        try:
            models = client.models.list()
            print(models)
            model_names = [model.id for model in models.data]
            return model_names
        except Exception as e:
            return {"error": str(e)}

    @app.post('/openAi')
    def openAiInterpretation(request: OpenAIRequest):
        openAiKey = settings.get("OpenAI_API_Key")
        if openAiKey is None:
            return {'error': 'No OpenAI key found'}
        client = OpenAI(api_key=openAiKey)

        try:
            print(request.prompt)
            response = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "system", "content": request.system},
                    {"role": "user", "content": request.prompt}
                ],
                temperature=0.5
            )
            print(response)
            # Structure a detailed response
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

    @app.post("/api/openai/respond")
    async def openai_respond(req: OpenAIRequest):
        api_key = settings.get("OpenAI_API_Key")
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
            # optional, aber sehr hilfreich
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

        output_text = _extract_output_text(data)
        if not output_text:
            raise HTTPException(
                status_code=502,
                detail="OpenAI response contained no output_text"
            )

        # hier absichtlich KEIN Parsing-Zwang:
        # der Client entscheidet, ob JSON, Text, Tokens usw.
        return {
            "raw": output_text
        }

    @app.post("/api/translate")
    def translate_endpoint(request: dict):
        text = request.get("text")
        to_lang = request.get("to")
        from_lang = request.get("from", None)

        if not text or not to_lang:
            raise HTTPException(status_code=400, detail="Missing 'text' or 'to' parameter")

        try:
            result = translate(text, to_lang=to_lang, from_lang=from_lang)
            print(result["translatedText"])
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app, settings


if __name__ == "__main__":
    import uvicorn

    app, settings = create_app()
    port = settings.get("port", 7000)

    print(f"Starting server on port {port}")
    print(f"Serving Angular app from: {Path(__file__).parent / 'ui' / 'dist' / 'ui'}")

    uvicorn.run(app, host="localhost", port=port)
