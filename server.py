import json, sys, os
from pathlib import Path

from openai import OpenAI

from py.domains.ImparaDomainsORM import User, Language, Languages, Course, Lesson, DictEntry, DictSense, DictTranslation, DictExample, UserSenseState
from py.domains.OpenAIRequest import OpenAIRequest
from py.services.databaseServiceORM import ImparaDB

import httpx
from fastapi import Body, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests

class ImparaServer:
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
        def create_user(payload: dict = Body(...)):
            try:
                user = User(**payload)
                self.db.insert_user(user)
                return self.db.get_user_by_name(user)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/user")
        def update_user(payload: dict = Body(...)):
            try:
                user = User(**payload)
                self.db.delete_user(user.id)
                self.db.insert_user(user)
                return self.db.get_user_by_name(user)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/user")
        def list_users():
            try:
                return self.db.list_users()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/user/{user_id}")
        def delete_user(user_id: int):
            try:
                self.db.delete_user(user_id)
                return {"message": f"User with id {user_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== COURSE ENDPOINTS ====================

        @self.app.get("/api/courses")
        def list_courses():
            try:
                return self.db.list_courses()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/courses/user/{user_id}")
        def list_courses_by_user(user_id: int):
            try:
                return self.db.list_courses_by_user(user_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/courses/target-language/{target_language}")
        def list_courses_by_target_language(target_language: str):
            try:
                return self.db.list_courses_by_target_language(target_language)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/course/{course_id}")
        def get_course(course_id: int):
            try:
                course = self.db.get_course(course_id)
                if course is None:
                    raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found")
                return course
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/course")
        def create_course(payload: dict = Body(...)):
            try:
                course = Course(**payload)
                return self.db.insert_course(course)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/course/{course_id}")
        def update_course(course_id: int, payload: dict = Body(...)):
            try:
                course = self.db.update_course(course_id, **payload)
                if course is None:
                    raise HTTPException(status_code=404, detail=f"Course with id {course_id} not found")
                return course
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/course/{course_id}")
        def delete_course(course_id: int):
            try:
                self.db.delete_course(course_id)
                return {"message": f"Course with id {course_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/languages")
        def list_languages():
            try:
                return self.db.list_languages()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/language")
        def create_user_language(payload: dict = Body(...)):
            try:
                language = Language(**payload)
                self.db.insert_language(language)
                return self.db.list_user_languages(language.user_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/language/{user_id}")
        def list_user_languages(user_id: int):
            try:
                return self.db.list_user_languages(user_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== LESSON ENDPOINTS ====================

        @self.app.get("/api/lessons")
        def list_lessons():
            try:
                return self.db.list_lessons()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/lessons/user/{user_id}")
        def list_lessons_by_user(user_id: int):
            try:
                return self.db.list_lessons_by_user(user_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/lessons/course/{course_id}")
        def list_lessons_by_course(course_id: int):
            try:
                return self.db.list_lessons_by_course(course_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/lessons/top-level/course/{course_id}")
        def list_top_level_lessons(course_id: int):
            try:
                return self.db.list_top_level_lessons(course_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/lesson/{lesson_id}")
        def get_lesson(lesson_id: int):
            try:
                lesson = self.db.get_lesson(lesson_id)
                if lesson is None:
                    raise HTTPException(status_code=404, detail=f"Lesson with id {lesson_id} not found")
                return lesson
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/lesson")
        def create_lesson(payload: dict = Body(...)):
            try:
                lesson = Lesson(**payload)
                return self.db.insert_lesson(lesson)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/lesson/{lesson_id}")
        def update_lesson(lesson_id: int, payload: dict = Body(...)):
            try:
                lesson = self.db.update_lesson(lesson_id, **payload)
                if lesson is None:
                    raise HTTPException(status_code=404, detail=f"Lesson with id {lesson_id} not found")
                return lesson
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/lesson/{lesson_id}")
        def delete_lesson(lesson_id: int):
            try:
                self.db.delete_lesson(lesson_id)
                return {"message": f"Lesson with id {lesson_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== DICT_ENTRY ENDPOINTS ====================

        @self.app.get("/api/dict-entries")
        def list_dict_entries():
            try:
                return self.db.list_dict_entries()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-entries/language/{language}")
        def list_dict_entries_by_language(language: str):
            try:
                return self.db.list_dict_entries_by_language(language)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-entry/lemma/{language}/{lemma}")
        def get_dict_entry_by_lemma(language: str, lemma: str):
            try:
                entry = self.db.get_dict_entry_by_lemma(language, lemma)
                if entry is None:
                    raise HTTPException(status_code=404, detail=f"DictEntry not found")
                return entry
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-entry/{entry_id}")
        def get_dict_entry(entry_id: int):
            try:
                entry = self.db.get_dict_entry(entry_id)
                if entry is None:
                    raise HTTPException(status_code=404, detail=f"DictEntry with id {entry_id} not found")
                return entry
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/dict-entry")
        def create_dict_entry(payload: dict = Body(...)):
            try:
                entry = DictEntry(**payload)
                return self.db.insert_dict_entry(entry)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/dict-entry/{entry_id}")
        def update_dict_entry(entry_id: int, payload: dict = Body(...)):
            try:
                entry = self.db.update_dict_entry(entry_id, **payload)
                if entry is None:
                    raise HTTPException(status_code=404, detail=f"DictEntry with id {entry_id} not found")
                return entry
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/dict-entry/{entry_id}")
        def delete_dict_entry(entry_id: int):
            try:
                self.db.delete_dict_entry(entry_id)
                return {"message": f"DictEntry with id {entry_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== DICT_SENSE ENDPOINTS ====================

        @self.app.get("/api/dict-senses")
        def list_dict_senses():
            try:
                return self.db.list_dict_senses()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-senses/entry/{entry_id}")
        def list_dict_senses_by_entry(entry_id: int):
            try:
                return self.db.list_dict_senses_by_entry(entry_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-sense/{sense_id}")
        def get_dict_sense(sense_id: int):
            try:
                sense = self.db.get_dict_sense(sense_id)
                if sense is None:
                    raise HTTPException(status_code=404, detail=f"DictSense with id {sense_id} not found")
                return sense
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/dict-sense")
        def create_dict_sense(payload: dict = Body(...)):
            try:
                sense = DictSense(**payload)
                return self.db.insert_dict_sense(sense)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/dict-sense/{sense_id}")
        def update_dict_sense(sense_id: int, payload: dict = Body(...)):
            try:
                sense = self.db.update_dict_sense(sense_id, **payload)
                if sense is None:
                    raise HTTPException(status_code=404, detail=f"DictSense with id {sense_id} not found")
                return sense
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/dict-sense/{sense_id}")
        def delete_dict_sense(sense_id: int):
            try:
                self.db.delete_dict_sense(sense_id)
                return {"message": f"DictSense with id {sense_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== DICT_TRANSLATION ENDPOINTS ====================

        @self.app.get("/api/dict-translations")
        def list_dict_translations():
            try:
                return self.db.list_dict_translations()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-translations/sense/{sense_id}")
        def list_dict_translations_by_sense(sense_id: int):
            try:
                return self.db.list_dict_translations_by_sense(sense_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-translations/language/{target_language}")
        def list_dict_translations_by_language(target_language: str):
            try:
                return self.db.list_dict_translations_by_language(target_language)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-translation/{translation_id}")
        def get_dict_translation(translation_id: int):
            try:
                translation = self.db.get_dict_translation(translation_id)
                if translation is None:
                    raise HTTPException(status_code=404, detail=f"DictTranslation with id {translation_id} not found")
                return translation
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/dict-translation")
        def create_dict_translation(payload: dict = Body(...)):
            try:
                translation = DictTranslation(**payload)
                return self.db.insert_dict_translation(translation)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/dict-translation/{translation_id}")
        def update_dict_translation(translation_id: int, payload: dict = Body(...)):
            try:
                translation = self.db.update_dict_translation(translation_id, **payload)
                if translation is None:
                    raise HTTPException(status_code=404, detail=f"DictTranslation with id {translation_id} not found")
                return translation
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/dict-translation/{translation_id}")
        def delete_dict_translation(translation_id: int):
            try:
                self.db.delete_dict_translation(translation_id)
                return {"message": f"DictTranslation with id {translation_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== DICT_EXAMPLE ENDPOINTS ====================

        @self.app.get("/api/dict-examples")
        def list_dict_examples():
            try:
                return self.db.list_dict_examples()
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-examples/sense/{sense_id}")
        def list_dict_examples_by_sense(sense_id: int):
            try:
                return self.db.list_dict_examples_by_sense(sense_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/dict-example/{example_id}")
        def get_dict_example(example_id: int):
            try:
                example = self.db.get_dict_example(example_id)
                if example is None:
                    raise HTTPException(status_code=404, detail=f"DictExample with id {example_id} not found")
                return example
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/dict-example")
        def create_dict_example(payload: dict = Body(...)):
            try:
                example = DictExample(**payload)
                return self.db.insert_dict_example(example)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/dict-example/{example_id}")
        def update_dict_example(example_id: int, payload: dict = Body(...)):
            try:
                example = self.db.update_dict_example(example_id, **payload)
                if example is None:
                    raise HTTPException(status_code=404, detail=f"DictExample with id {example_id} not found")
                return example
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/dict-example/{example_id}")
        def delete_dict_example(example_id: int):
            try:
                self.db.delete_dict_example(example_id)
                return {"message": f"DictExample with id {example_id} deleted"}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # ==================== USER_SENSE_STATE ENDPOINTS ====================

        @self.app.get("/api/user-sense-states/user/{user_id}")
        def list_user_sense_states(user_id: int):
            try:
                return self.db.list_user_sense_states(user_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/user-sense-states/sense/{sense_id}")
        def list_user_sense_states_by_sense(sense_id: int):
            try:
                return self.db.list_user_sense_states_by_sense(sense_id)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.get("/api/user-sense-state/{user_id}/{sense_id}")
        def get_user_sense_state(user_id: int, sense_id: int):
            try:
                state = self.db.get_user_sense_state(user_id, sense_id)
                if state is None:
                    raise HTTPException(status_code=404, detail=f"UserSenseState not found")
                return state
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.post("/api/user-sense-state")
        def create_user_sense_state(payload: dict = Body(...)):
            try:
                state = UserSenseState(**payload)
                return self.db.insert_user_sense_state(state)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.put("/api/user-sense-state/{user_id}/{sense_id}")
        def update_user_sense_state(user_id: int, sense_id: int, payload: dict = Body(...)):
            try:
                state = self.db.update_user_sense_state(user_id, sense_id, **payload)
                if state is None:
                    raise HTTPException(status_code=404, detail=f"UserSenseState not found")
                return state
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        @self.app.delete("/api/user-sense-state/{user_id}/{sense_id}")
        def delete_user_sense_state(user_id: int, sense_id: int):
            try:
                self.db.delete_user_sense_state(user_id, sense_id)
                return {"message": f"UserSenseState deleted for user {user_id} and sense {sense_id}"}
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
    server = ImparaServer()
    port = server.settings.get("port", 7000)
    print(f"Starting server on port {port}")
    print(f"Serving Angular app from: {server.dist_folder}")
    uvicorn.run(server.app, host="localhost", port=port)
