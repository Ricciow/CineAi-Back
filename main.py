
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from dotenv import load_dotenv
from routes.conversation import router as conversationRouter

app = FastAPI()
load_dotenv()

origins = os.environ.get("FRONTEND_URLS", "").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(conversationRouter)
