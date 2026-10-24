from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel

class Settings(BaseSettings):
    frontend_url: str
    redis_url: str
    youtube_api_key: str
    openai_api_key: str


    model_config = SettingsConfigDict(env_file=".env")

class YoutubeVideo(BaseModel):
    url:str


class Task(BaseModel):
    task_id: str

class AnalyzedComment(BaseModel):
    id: str
    text: str
    category: str

