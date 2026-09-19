#!/usr/bin/env python3
"""Landing page backend with Linkwarden or Karakeep integration."""

import json
import logging
import os
import random
import sys
import traceback
from pathlib import Path

import feedparser
import requests
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

# Configure logging to stdout with full tracebacks
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO for production
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Bookmark service selection: "linkwarden" or "karakeep"
BOOKMARK_SERVICE = os.getenv("BOOKMARK_SERVICE", "linkwarden").lower().strip()

if BOOKMARK_SERVICE not in ("linkwarden", "karakeep"):
    logger.warning(f"Invalid BOOKMARK_SERVICE '{BOOKMARK_SERVICE}', defaulting to 'linkwarden'")
    BOOKMARK_SERVICE = "linkwarden"

# Linkwarden config - configurable via environment variables
LINKWARDEN_HOST = os.getenv("LINKWARDEN_HOST", "http://localhost:3000").rstrip('/')
LINKWARDEN_TOKEN = os.getenv("LINKWARDEN_TOKEN", "")
LINKWARDEN_COLLECTION_ID = os.getenv("LINKWARDEN_COLLECTION_ID", None)
LINKWARDEN_LIMIT = int(os.getenv("LINKWARDEN_LIMIT", "10"))

# Karakeep config - configurable via environment variables
KARAKEEP_HOST = os.getenv("KARAKEEP_HOST", "http://localhost:3000").rstrip('/')
KARAKEEP_TOKEN = os.getenv("KARAKEEP_TOKEN", "")
KARAKEEP_TAG = os.getenv("KARAKEEP_TAG", None)
KARAKEEP_LIMIT = int(os.getenv("KARAKEEP_LIMIT", "10"))

# Validate configuration based on selected service
if BOOKMARK_SERVICE == "linkwarden" and not LINKWARDEN_TOKEN:
    logger.warning("LINKWARDEN_TOKEN not set. Linkwarden integration will fail.")
elif BOOKMARK_SERVICE == "karakeep" and not KARAKEEP_TOKEN:
    logger.warning("KARAKEEP_TOKEN not set. Karakeep integration will fail.")

LINKWARDEN_HEADERS = {
    "Authorization": f"Bearer {LINKWARDEN_TOKEN}",
    "Content-Type": "application/json"
} if LINKWARDEN_TOKEN else {}

KARAKEEP_HEADERS = {
    "Authorization": f"Bearer {KARAKEEP_TOKEN}",
    "Content-Type": "application/json"
} if KARAKEEP_TOKEN else {}

# HN RSS - configurable via environment variable
RSS_URL = os.getenv("RSS", "https://hnrss.org/frontpage?count=20")
RSS_TITLE = None  # Will be populated on first fetch

# Data persistence
DATA_DIR = Path("/app/data")
SERVICES_FILE = DATA_DIR / "services.json"


class Service(BaseModel):
    name: str
    url: str


def load_services() -> list[dict]:
    """Load services from JSON file."""
    if SERVICES_FILE.exists():
        try:
            return json.loads(SERVICES_FILE.read_text())
        except Exception as e:
            logger.error(f"Failed to load services: {e}")
    return []


def save_services(services: list[dict]) -> None:
    """Save services to JSON file."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SERVICES_FILE.write_text(json.dumps(services, indent=2))


def linkwarden_request(endpoint: str, params: dict = None) -> dict:
    """Make request to Linkwarden API with error logging."""
    url = f"{LINKWARDEN_HOST}{endpoint}"
    logger.debug(f"Linkwarden request: {url} params={params}")
    
    try:
        resp = requests.get(url, headers=LINKWARDEN_HEADERS, params=params, timeout=10)
        logger.debug(f"Linkwarden response status: {resp.status_code}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Linkwarden: {e}")
        raise HTTPException(502, "Cannot connect to Linkwarden")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to Linkwarden: {e}")
        raise HTTPException(504, "Linkwarden request timed out")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from Linkwarden: {e}")
        raise HTTPException(resp.status_code, "Linkwarden API error")
    except Exception as e:
        logger.error(f"Unexpected error in Linkwarden request: {e}")
        raise HTTPException(500, "Unexpected error occurred")


def karakeep_request(endpoint: str, params: dict = None) -> dict:
    """Make request to Karakeep API with error logging."""
    url = f"{KARAKEEP_HOST}{endpoint}"
    logger.debug(f"Karakeep request: {url} params={params}")
    
    try:
        resp = requests.get(url, headers=KARAKEEP_HEADERS, params=params, timeout=10)
        logger.debug(f"Karakeep response status: {resp.status_code}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Karakeep: {e}")
        raise HTTPException(502, "Cannot connect to Karakeep")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to Karakeep: {e}")
        raise HTTPException(504, "Karakeep request timed out")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from Karakeep: {e}")
        raise HTTPException(resp.status_code, "Karakeep API error")
    except Exception as e:
        logger.error(f"Unexpected error in Karakeep request: {e}")
        raise HTTPException(500, "Unexpected error occurred")


@app.get("/")
async def index():
    """Serve the main page."""
    return FileResponse("/app/index.html")


@app.get("/api/collections")
async def get_collections():
    """Get all collections from the configured bookmark service."""
    if BOOKMARK_SERVICE == "linkwarden":
        data = linkwarden_request("/api/v1/collections")
        collections = [{"id": c["id"], "name": c["name"]} for c in data.get("response", data)]
    else:  # karakeep
        data = karakeep_request("/api/v1/collections")
        collections = [{"id": c["id"], "name": c["name"]} for c in data.get("response", data)]
    
    logger.info(f"Returning {len(collections)} collections")
    return collections


@app.get("/api/links")
async def get_links(collection_id: int = None, tag: str = None):
    """Get random links from the configured bookmark service (Linkwarden or Karakeep)."""
    if BOOKMARK_SERVICE == "linkwarden":
        # Use env var collection_id if not provided in request
        if collection_id is None and LINKWARDEN_COLLECTION_ID:
            try:
                collection_id = int(LINKWARDEN_COLLECTION_ID)
            except (ValueError, TypeError):
                pass
        
        params = {"limit": max(50, LINKWARDEN_LIMIT * 5)}  # Fetch more than we need to randomize
        if collection_id:
            params["collectionId"] = collection_id
        
        data = linkwarden_request("/api/v1/links", params)
        links = data.get("response", data)
        
        # Handle if links is wrapped in another structure
        if isinstance(links, dict) and "links" in links:
            links = links["links"]
        
        logger.info(f"Got {len(links)} links from Linkwarden")
        
        # Randomize and take configured limit
        random.shuffle(links)
        selected = links[:LINKWARDEN_LIMIT]
        
        # Return simplified link data
        result = []
        for link in selected:
            result.append({
                "id": link.get("id"),
                "name": link.get("name") or link.get("title") or link.get("url", "Untitled"),
                "url": link.get("url"),
                "description": link.get("description", ""),
                "collection": link.get("collection", {}).get("name", "")
            })
    else:  # karakeep
        # Use env var tag if not provided in request
        if tag is None and KARAKEEP_TAG:
            tag = KARAKEEP_TAG
        
        params = {"limit": max(50, KARAKEEP_LIMIT * 5)}  # Fetch more than we need to randomize
        if tag:
            params["tag"] = tag
        
        data = karakeep_request("/api/v1/links", params)
        links = data.get("response", data)
        
        # Handle if links is wrapped in another structure
        if isinstance(links, dict) and "links" in links:
            links = links["links"]
        
        logger.info(f"Got {len(links)} links from Karakeep")
        
        # Randomize and take configured limit
        random.shuffle(links)
        selected = links[:KARAKEEP_LIMIT]
        
        # Return simplified link data
        result = []
        for link in selected:
            result.append({
                "id": link.get("id"),
                "name": link.get("name") or link.get("title") or link.get("url", "Untitled"),
                "url": link.get("url"),
                "description": link.get("description", ""),
                "tags": link.get("tags", [])
            })
    
    return result


@app.get("/api/hackernews")
async def get_hackernews():
    """Fetch RSS feed and return items with feed title."""
    global RSS_TITLE
    try:
        feed = feedparser.parse(RSS_URL)
        # Update the feed title from RSS
        if feed.feed.get("title"):
            RSS_TITLE = feed.feed.get("title")
        
        items = []
        for entry in feed.entries[:20]:
            items.append({
                "title": entry.get("title", "Untitled"),
                "url": entry.get("link", ""),
                "comments_url": entry.get("comments", ""),
                "published": entry.get("published", ""),
            })
        logger.info(f"Fetched {len(items)} RSS items from {RSS_URL}")
        return items
    except Exception as e:
        logger.error(f"RSS error: {e}")
        raise HTTPException(502, "Failed to fetch RSS feed")


@app.get("/api/rss-title")
async def get_rss_title():
    """Return the current RSS feed title."""
    return {"title": RSS_TITLE or "Hacker News"}


@app.get("/api/services")
async def get_services():
    """Get all manual services."""
    return load_services()


@app.post("/api/services")
async def add_service(service: Service):
    """Add a new service."""
    services = load_services()
    services.append({"name": service.name, "url": service.url})
    save_services(services)
    logger.info(f"Added service: {service.name}")
    return {"status": "ok"}


@app.delete("/api/services/{index}")
async def delete_service(index: int):
    """Delete a service by index."""
    services = load_services()
    if 0 <= index < len(services):
        removed = services.pop(index)
        save_services(services)
        logger.info(f"Deleted service: {removed['name']}")
        return {"status": "ok"}
    raise HTTPException(404, "Service not found")


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Catch-all exception handler with full logging."""
    logger.error(f"Unhandled exception: {exc}")
    logger.error(traceback.format_exc())
    # Don't expose traceback to clients in production
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
