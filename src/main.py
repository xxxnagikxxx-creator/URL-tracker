from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.telegram_auth.routers import auth_router
from src.live_checker.routers import live_checker_router

ALLOWED_CORS_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

ALLOWED_CORS_ORIGIN_REGEX = (
    r"^https://.*\.(ru\.tuna\.am|ngrok-free\.app|trycloudflare\.com)$"
)

app = FastAPI(title="Live Checker", description="Сервис для проверки сервера на ответ")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_CORS_ORIGINS,
    allow_origin_regex=ALLOWED_CORS_ORIGIN_REGEX,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "live_checker"}

app.include_router(auth_router)
app.include_router(live_checker_router)
