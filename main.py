from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from datetime import datetime, timedelta
import random, string, sqlite3

# Import logger
from logger_middleware import logging_middleware, log

# --------------------- Database Setup ----------------------
conn = sqlite3.connect("urls.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS urls (
    shortcode TEXT PRIMARY KEY,
    long_url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    click_count INTEGER DEFAULT 0
)
""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS clicks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shortcode TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    referrer TEXT,
    ip_address TEXT,
    FOREIGN KEY(shortcode) REFERENCES urls(shortcode)
)
""")
conn.commit()

# ---------------------- App Setup -----------------
app = FastAPI()
app.middleware("http")(logging_middleware)

# ------------------- Models -----------------
class URLRequest(BaseModel):
    url: HttpUrl
    validity: int = 30  # minutes
    shortcode: str | None = None

# -------------- Helpers -----------------
def generate_shortcode(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def is_shortcode_unique(code):
    cursor.execute("SELECT shortcode FROM urls WHERE shortcode=?", (code,))
    return cursor.fetchone() is None

# -------------- API Endpoints -----------------
@app.post("/shorturls")
def create_short_url(data: URLRequest):
    shortcode = data.shortcode or generate_shortcode()
    
    if not is_shortcode_unique(shortcode):
        log("backend", "error", "shortener", "Shortcode already exists")
        raise HTTPException(status_code=400, detail="Shortcode already exists.")
    
    created_at = datetime.utcnow()
    expires_at = created_at + timedelta(minutes=data.validity)
    
    cursor.execute(
        "INSERT INTO urls (shortcode, long_url, created_at, expires_at) VALUES (?, ?, ?, ?)",
        (shortcode, data.url, created_at.isoformat(), expires_at.isoformat())
    )
    conn.commit()
    
    log("backend", "info", "shortener", f"Created short URL {shortcode}")
    return {
        "short_url": f"http://localhost:8000/{shortcode}",
        "shortcode": shortcode,
        "expires_at": expires_at.isoformat()
    }

@app.get("/{shortcode}")
def redirect_to_url(shortcode: str, request: Request):
    cursor.execute("SELECT long_url, expires_at, click_count FROM urls WHERE shortcode=?", (shortcode,))
    row = cursor.fetchone()
    
    if not row:
        log("backend", "error", "redirect", "Shortcode not found")
        raise HTTPException(status_code=404, detail="Shortcode not found.")
    
    long_url, expires_at, click_count = row
    if datetime.fromisoformat(expires_at) < datetime.utcnow():
        log("backend", "error", "redirect", "Link expired")
        raise HTTPException(status_code=410, detail="Link has expired.")
    
    cursor.execute(
        "INSERT INTO clicks (shortcode, timestamp, referrer, ip_address) VALUES (?, ?, ?, ?)",
        (shortcode, datetime.utcnow().isoformat(), request.headers.get("referer"), request.client.host)
    )
    cursor.execute("UPDATE urls SET click_count=? WHERE shortcode=?", (click_count + 1, shortcode))
    conn.commit()
    
    log("backend", "info", "redirect", f"Redirected {shortcode} to {long_url}")
    return RedirectResponse(url=long_url)

@app.get("/shorturls/{shortcode}")
def get_short_url_stats(shortcode: str):
    cursor.execute("SELECT long_url, created_at, expires_at, click_count FROM urls WHERE shortcode=?", (shortcode,))
    row = cursor.fetchone()
    
    if not row:
        log("backend", "error", "stats", "Shortcode not found")
        raise HTTPException(status_code=404, detail="Shortcode not found.")
    
    long_url, created_at, expires_at, click_count = row
    cursor.execute("SELECT timestamp, referrer, ip_address FROM clicks WHERE shortcode=?", (shortcode,))
    clicks = [
        {"timestamp": t, "referrer": r, "ip_address": ip}
        for t, r, ip in cursor.fetchall()
    ]
    
    log("backend", "info", "stats", f"Stats retrieved for {shortcode}")
    return {
        "shortcode": shortcode,
        "original_url": long_url,
        "created_at": created_at,
        "expires_at": expires_at,
        "total_clicks": click_count,
        "click_details": clicks
    }
