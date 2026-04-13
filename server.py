from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import httpx, os, json

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

GEMINI_KEY   = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-flash-preview")
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")

def sb_headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

# ── Static ──────────────────────────────────────────────────────────────────
@app.get("/")
async def root():
    return FileResponse("lexen.html")

# ── Gemini proxy ─────────────────────────────────────────────────────────────
@app.post("/api/gemini")
async def gemini_proxy(request: Request):
    body = await request.json()
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_KEY}"
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(url, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)

# ── Users ─────────────────────────────────────────────────────────────────────
@app.get("/api/users")
async def get_users():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/users?select=*&order=is_guest", headers=sb_headers())
    return JSONResponse(content=r.json())

# ── Passages ──────────────────────────────────────────────────────────────────
@app.get("/api/passages")
async def get_passages():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/passages?select=*&order=year,q_number", headers=sb_headers())
    return JSONResponse(content=r.json())

@app.post("/api/passages")
async def upsert_passage(request: Request):
    body = await request.json()
    h = {**sb_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/passages", headers=h, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)

# ── Vocabulary ────────────────────────────────────────────────────────────────
@app.get("/api/vocabulary")
async def get_vocabulary():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{SUPABASE_URL}/rest/v1/vocabulary?select=*&order=created_at.desc", headers=sb_headers())
    return JSONResponse(content=r.json())

@app.post("/api/vocabulary")
async def upsert_vocabulary(request: Request):
    body = await request.json()
    h = {**sb_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/vocabulary", headers=h, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)

# ── SRS Cards ─────────────────────────────────────────────────────────────────
@app.get("/api/srs_cards/{user_id}")
async def get_srs_cards(user_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/srs_cards?user_id=eq.{user_id}&select=*",
            headers=sb_headers()
        )
    return JSONResponse(content=r.json())

@app.post("/api/srs_cards")
async def upsert_srs_card(request: Request):
    body = await request.json()
    h = {**sb_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/srs_cards", headers=h, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)

@app.post("/api/srs_cards/batch")
async def batch_upsert_srs_cards(request: Request):
    body = await request.json()
    h = {**sb_headers(), "Prefer": "resolution=merge-duplicates,return=representation"}
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/srs_cards", headers=h, json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)

# ── Study Log ─────────────────────────────────────────────────────────────────
@app.get("/api/study_log/{user_id}")
async def get_study_log(user_id: str):
    async with httpx.AsyncClient() as client:
        r = await client.get(
            f"{SUPABASE_URL}/rest/v1/study_log?user_id=eq.{user_id}&select=*&order=created_at.desc&limit=500",
            headers=sb_headers()
        )
    return JSONResponse(content=r.json())

@app.post("/api/study_log")
async def insert_study_log(request: Request):
    body = await request.json()
    async with httpx.AsyncClient() as client:
        r = await client.post(f"{SUPABASE_URL}/rest/v1/study_log", headers=sb_headers(), json=body)
    return JSONResponse(content=r.json(), status_code=r.status_code)
