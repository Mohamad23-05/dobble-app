import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routers import dobble

app = FastAPI(title="Dobble API")

FRONTEND_URL = os.getenv("FRONTEND_URL", "https://dobble-app.onrender.com")
ALLOWED_ORIGINS = [
    FRONTEND_URL,  # production
    "http://localhost:5173",  # local dev
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dobble.router)


@app.get("/")
def root():
    return {"message": "Dobble API running!"}
