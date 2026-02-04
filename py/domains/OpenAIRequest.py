from pydantic import BaseModel

class OpenAIRequest(BaseModel):
    model: str
    system: str
    prompt: str
