import os
from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from io import BytesIO

from backend.routers import dobble

app = FastAPI(title="Dobble API")
FRONTEND_URL = os.getenv("FRONTEND_URL")  # set to https://dobble-app.onrender.com

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

app.include_router(dobble.router)


@app.get("/")
def root():
    return {"message": "Dobble API running!"}
