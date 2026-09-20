# Frontpage - Self-Hosted Landing Page Dashboard

A lightweight landing page dashboard integrating with **Linkwarden** or **Karakeep** for bookmarks, displaying a rss feed, and custom service links. Built with FastAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## Features

- **Dual Bookmark Support**: Linkwarden or Karakeep integration
- **News Feed**: Real-time frontpage stories via RSS
- **Manual Services**: Add custom links (Plex, Nextcloud, etc.)
- **Responsive Design**: Clean three-column layout
- **Docker Ready**: Simple deployment with docker-compose

## Quick Start

1. **Create `.env` file**:
   ```bash
   BOOKMARK_SERVICE=linkwarden
   LINKWARDEN_HOST=http://your-linkwarden-host:3000
   LINKWARDEN_TOKEN=your_api_token_here
   LINKWARDEN_COLLECTION_ID=  # Optional
   LINKWARDEN_LIMIT=10
   ```

2. **Start the container**:
   ```bash
   docker compose up -d
   ```

3. **Access**: Navigate to `http://localhost:8080`

> No bookmark service? Leave token empty—app runs without integration.

## Configuration

### General Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOOKMARK_SERVICE` | Select service: `linkwarden` or `karakeep` | `linkwarden` | No |

### Linkwarden Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LINKWARDEN_HOST` | Linkwarden server URL | `http://localhost:3000` | No |
| `LINKWARDEN_TOKEN` | API token | (empty) | No* |
| `LINKWARDEN_COLLECTION_ID` | Filter by collection | (all) | No |
| `LINKWARDEN_LIMIT` | Bookmarks to display | `10` | No |

### Karakeep Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `KARAKEEP_HOST` | Karakeep server URL | `http://localhost:3000` | No |
| `KARAKEEP_TOKEN` | API token | (empty) | No* |
| `KARAKEEP_TAG` | Filter by tag | (all) | No |
| `KARAKEEP_LIMIT` | Bookmarks to display | `10` | No |
