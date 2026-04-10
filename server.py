from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx, os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash-lite")

@app.get("/")
async def root():
    return FileResponse("lexen.html")

@app.post("/api/gemini")
async def gemini_proxy(request: Request):
    body = await request.json()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(url, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)