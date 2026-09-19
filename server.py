#!/usr/bin/env python3
"""Landing page backend with Linkwarden integration."""

import json
import logging
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
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

app = FastAPI()

# Linkwarden config
LINKWARDEN_HOST = "http://192.168.1.21:3000"
LINKWARDEN_TOKEN = "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..UoI5UIt0x7MFbiJV.PaGvBXvmWR-tgbPyumm47DtEHPK1R9zYmUp2sUAVqe3wprE10E3WypwIbdHHTLiOE8x6zh-hWlwNQh-oMgH0bwiVC1tXszOSp3_Yq1eWfdxkB4dt4T_Z.7j8f2jyqPE6n9azO2XCDUQ"
LINKWARDEN_HEADERS = {
    "Authorization": f"Bearer {LINKWARDEN_TOKEN}",
    "Content-Type": "application/json"
}

# HN RSS
HN_RSS_URL = "https://hnrss.org/frontpage?count=20"

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
    """Make request to Linkwarden API with full error logging."""
    url = f"{LINKWARDEN_HOST}{endpoint}"
    logger.info(f"Linkwarden request: {url} params={params}")
    
    try:
        resp = requests.get(url, headers=LINKWARDEN_HEADERS, params=params, timeout=10)
        logger.info(f"Linkwarden response status: {resp.status_code}")
        logger.debug(f"Linkwarden response body: {resp.text[:500]}")
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error to Linkwarden: {e}")
        raise HTTPException(502, f"Cannot connect to Linkwarden: {e}")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout connecting to Linkwarden: {e}")
        raise HTTPException(504, f"Linkwarden request timed out: {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error from Linkwarden: {e}")
        logger.error(f"Response body: {resp.text}")
        raise HTTPException(resp.status_code, f"Linkwarden error: {resp.text}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(500, f"Unexpected error: {e}")


@app.get("/")
async def index():
    """Serve the main page."""
    return FileResponse("/app/index.html")


@app.get("/api/collections")
async def get_collections():
    """Get all collections from Linkwarden."""
    data = linkwarden_request("/api/v1/collections")
    # Return just the list of collections with id and name
    collections = [{"id": c["id"], "name": c["name"]} for c in data.get("response", data)]
    logger.info(f"Returning {len(collections)} collections")
    return collections


@app.get("/api/links")
async def get_links(collection_id: int = None):
    """Get random links from Linkwarden."""
    params = {"limit": 50}  # Fetch more than we need to randomize
    if collection_id:
        params["collectionId"] = collection_id
    
    data = linkwarden_request("/api/v1/links", params)
    links = data.get("response", data)
    
    # Handle if links is wrapped in another structure
    if isinstance(links, dict) and "links" in links:
        links = links["links"]
    
    logger.info(f"Got {len(links)} links from Linkwarden")
    
    # Randomize and take 10
    random.shuffle(links)
    selected = links[:10]
    
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
    
    return result


@app.get("/api/hackernews")
async def get_hackernews():
    """Fetch HN frontpage RSS."""
    try:
        feed = feedparser.parse(HN_RSS_URL)
        items = []
        for entry in feed.entries[:20]:
            items.append({
                "title": entry.get("title", "Untitled"),
                "url": entry.get("link", ""),
                "comments_url": entry.get("comments", ""),
                "published": entry.get("published", ""),
            })
        logger.info(f"Fetched {len(items)} HN items")
        return items
    except Exception as e:
        logger.error(f"HN RSS error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(502, f"Failed to fetch HN: {e}")


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
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": traceback.format_exc()}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
