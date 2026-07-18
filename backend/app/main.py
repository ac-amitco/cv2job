from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import cv, jobs, meta

app = FastAPI(title="cv2job API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(meta.router, prefix="/api")
app.include_router(cv.router, prefix="/api")
app.include_router(jobs.router, prefix="/api")
