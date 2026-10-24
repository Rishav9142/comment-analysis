import redis
import json 
import httpx

from fastapi import FastAPI,BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from models import Settings,YoutubeVideo, Task, AnalyzedComment
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from uuid import uuid4
from collections import defaultdict
from pydantic_ai  import Agent
from prompts import COMMENTS_ANALYSIS_PROMPT
load_dotenv()

settings = Settings()
app = FastAPI()

r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/analyze")
def analyze(youtube_video: YoutubeVideo, background_tasks: BackgroundTasks) -> Task:
    parsed_url = urlparse(youtube_video.url)
    parsed_query = parse_qs(parsed_url.query)
    video_id = parsed_query.get("v", [None])[0]


    task_id = str(uuid4())


    if video_id:
        background_tasks.add_task(analyze_comments, task_id, video_id)

    return Task(task_id=task_id, status="pending", result=None)

def analyze_comments(task_id: str, video_id: str) -> None:
    r.set(task_id, json.dumps({"status": "processing", "data": {}}))
    print("SET TASK ID")
    print("PROCESSING COMMENTS")

    comments = get_youtube_comments(video_id, settings.youtube_api_key)
    print("RETREIVED YOUTUBE COMMENTS") 
    analyzed_comments = analyze_comments_ai(comments)
    print("ANALYZED COMMENTS")

    output = defaultdict(list)

    for comment in analyzed_comments:
        output[comment.category ].append({"id": comment.id, "text": comments.get(comment.id, "")})

    print("PROCESS COMPLETED")
    
    r.set(task_id, json.dumps({"status": "completed", "data": output}))

    return comments

def analyze_comments_ai(comments: dict) -> list[AnalyzedComment]:
    agent = Agent(
        "openai:gpt-4 mini",
        system_prompt=COMMENTS_ANALYSIS_PROMPT,
        output_type=list[AnalyzedComment]
    )

    formatted_comments = "<comments>\n"
    for comment_id, comment_text in comments.items():
        fromatted_comments += f'<comment><id>{comment_id}</id><text>{comment_text}</text></comment>\n'
    formatted_comments += "</comments>\n"

    result = agent.run_sync(formatted_comments)

    return result.output