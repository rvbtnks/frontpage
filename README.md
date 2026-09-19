# Frontpage - Self-Hosted Landing Page Dashboard

A lightweight landing page dashboard integrating with **Linkwarden** or **Karakeep** for bookmarks, displaying Hacker News stories, and custom service links. Built with FastAPI.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## Features

- **Dual Bookmark Support**: Linkwarden or Karakeep integration
- **Hacker News Feed**: Real-time frontpage stories via RSS
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

\* Required only if using the respective service

### Getting Your API Token

**Linkwarden**: Settings → API → Generate token

**Karakeep**: Settings/API section → Generate token

## Manual Services

Add custom links from the UI:

1. Click "+" in the Services column
2. Enter name and URL (e.g., "Plex", `http://plex:32400`)
3. Services persist in `/app/data/services.json`

## Project Structure

```
.
├── server.py           # FastAPI backend
├── index.html          # Frontend SPA
├── docker-compose.yml  # Docker Compose config
├── Dockerfile          # Container build instructions
├── requirements.txt    # Python dependencies
└── data/               # Persistent data (created at runtime)
    └── services.json   # Manual services
```


## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve main HTML page |
| `GET` | `/api/collections` | Get all collections from bookmark service |
| `GET` | `/api/links` | Get random bookmarks (`?collection_id=` for Linkwarden, `?tag=` for Karakeep) |
| `GET` | `/api/hackernews` | Fetch HN frontpage stories |
| `GET` | `/api/services` | Get manual services |
| `POST` | `/api/services` | Add a new service |
| `DELETE` | `/api/services/{index}` | Delete service by index |

## Security

- ✅ No hardcoded credentials
- ✅ Generic error messages (internal details hidden)
- ✅ Server-side logging only
- ✅ `.gitignore` configured

**Best Practices**:
1. Never commit `.env` to version control
2. Use strong API tokens
3. Run behind reverse proxy (nginx, Traefik) in production
4. Enable HTTPS for external access

## Development

### Running Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export LINKWARDEN_TOKEN=your_token
python server.py
```

### Building Docker Image

```bash
docker build -t frontpage .
docker run -p 8080:8080 --env-file .env frontpage
```

## Troubleshooting

**Connection Issues**:
- Verify `BOOKMARK_SERVICE` is set correctly
- Ensure `*_HOST` URL is accessible from container
- Check API token validity
- Review logs: `docker compose logs frontpage`

**Data Persistence**: Services stored in `./data/services.json`. Ensure write permissions.

**Port Conflicts**: Modify port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Change host port
```

## License

MIT License

## Acknowledgments

- [Linkwarden](https://linkwarden.app/)
- [Karakeep](https://karakeep.com/)
- [Hacker News](https://news.ycombinator.com/)
- [FastAPI](https://fastapi.tiangolo.com/)
