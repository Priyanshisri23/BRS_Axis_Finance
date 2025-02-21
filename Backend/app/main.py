# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, bot, logs, process, user_management
from app.db.base import create_tables
from app.init.folder_manager import create_folder_structure
# from app.process import sftp_handler_axis

app = FastAPI()

origins = [
    "https://brsuat.axisb.com"
    "http://localhost:3000",
    "https://localhost:3000",
    "http://localhost:8000",
    "https://localhost:8000",
    "http://localhost",
    "https://localhost",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the database and create tables
@app.on_event("startup")
def startup_event():
    create_tables()
    create_folder_structure()
    # sftp_handler_axis.sftp_hander()

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])  # For /auth/me endpoint
app.include_router(bot.router, prefix="/bot", tags=["bot"])
app.include_router(user_management.router, prefix="/users", tags=["users"])


app.include_router(process.router, prefix="/process", tags=["process"])
app.include_router(logs.router, prefix="/logs", tags=["logs"])
