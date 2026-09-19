# Frontpage - Self-Hosted Landing Page Dashboard

A lightweight, self-hosted landing page dashboard that integrates with **Linkwarden** or **Karakeep** for bookmark management, displays Hacker News stories, and allows manual service links. Built with FastAPI and served as a single-page application.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12+-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)

## Features

- **Dual Bookmark Service Support**: Choose between Linkwarden or Karakeep for bookmark integration
- **Hacker News Feed**: Real-time HN frontpage stories via RSS
- **Manual Services**: Add custom service links (e.g., Plex, Nextcloud, etc.)
- **Three-Column Layout**: Clean, responsive design with dedicated sections
- **Environment-Based Configuration**: No hardcoded credentials
- **Docker Ready**: Easy deployment with docker-compose

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   index.html    │────▶│   server.py      │────▶│  Linkwarden     │
│   (Frontend)    │     │   (FastAPI)      │     │  OR Karakeep    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │  Hacker News RSS │
                       └──────────────────┘
```

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Access to a Linkwarden or Karakeep instance (optional, for bookmark integration)

### Installation

1. **Clone or download this repository**

2. **Configure environment variables**

   Create a `.env` file in the project root:
   
   ```bash
   # Select bookmark service: "linkwarden" or "karakeep"
   BOOKMARK_SERVICE=linkwarden
   
   # Linkwarden configuration (if using Linkwarden)
   LINKWARDEN_HOST=http://your-linkwarden-host:3000
   LINKWARDEN_TOKEN=your_api_token_here
   LINKWARDEN_COLLECTION_ID=  # Optional: filter by collection ID
   LINKWARDEN_LIMIT=10        # Number of bookmarks to display
   
   # Karakeep configuration (if using Karakeep)
   # KARAKEEP_HOST=http://your-karakeep-host:3000
   # KARAKEEP_TOKEN=your_api_token_here
   # KARAKEEP_TAG=  # Optional: filter by tag
   # KARAKEEP_LIMIT=10  # Number of bookmarks to display
   ```

   > **Note**: If you don't have Linkwarden or Karakeep, leave the token empty. The app will run without bookmark integration.

3. **Start the container**
   ```bash
   docker compose up -d
   ```

4. **Access the dashboard**

   Open your browser and navigate to: `http://localhost:8080`

## Configuration Options

### General Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOOKMARK_SERVICE` | Select bookmark service: `linkwarden` or `karakeep` | `linkwarden` | No |

### Linkwarden Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `LINKWARDEN_HOST` | URL of your Linkwarden server | `http://localhost:3000` | No |
| `LINKWARDEN_TOKEN` | Linkwarden API token | (empty) | No* |
| `LINKWARDEN_COLLECTION_ID` | Filter bookmarks to specific collection | (all collections) | No |
| `LINKWARDEN_LIMIT` | Number of random bookmarks to display | `10` | No |

### Karakeep Settings

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `KARAKEEP_HOST` | URL of your Karakeep server | `http://localhost:3000` | No |
| `KARAKEEP_TOKEN` | Karakeep API token | (empty) | No* |
| `KARAKEEP_TAG` | Filter bookmarks by tag | (all tags) | No |
| `KARAKEEP_LIMIT` | Number of random bookmarks to display | `10` | No |

\* Required only if using the respective bookmark service integration

### Getting Your API Token

#### Linkwarden

1. Log into your Linkwarden instance
2. Go to Settings → API
3. Generate a new token
4. Copy and add it to your `.env` file

#### Karakeep

1. Log into your Karakeep instance
2. Navigate to Settings or API section
3. Generate a new API token
4. Copy and add it to your `.env` file

## Manual Services

Add custom service links directly from the UI:

1. Click the "+" button in the Services column
2. Enter a name (e.g., "Plex") and URL (e.g., `http://plex:32400`)
3. Services are persisted in `/app/data/services.json`

## Project Structure

```
.
├── server.py           # FastAPI backend application
├── index.html          # Single-page frontend application
├── docker-compose.yml  # Docker Compose configuration
├── Dockerfile          # Container build instructions
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore          # Git ignore rules
└── data/               # Persistent data directory (created at runtime)
    └── services.json   # Manually added services
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serve the main HTML page |
| `GET` | `/api/collections` | Get all collections from configured bookmark service |
| `GET` | `/api/links` | Get random bookmarks (supports `collection_id` for Linkwarden, `tag` for Karakeep) |
| `GET` | `/api/hackernews` | Fetch HN frontpage stories |
| `GET` | `/api/services` | Get all manual services |
| `POST` | `/api/services` | Add a new service |
| `DELETE` | `/api/services/{index}` | Delete a service by index |

### Query Parameters for `/api/links`

- **Linkwarden**: `?collection_id=123` - Filter by collection ID
- **Karakeep**: `?tag=mytag` - Filter by tag

## Security Considerations

- ✅ **No hardcoded credentials**: All sensitive config via environment variables
- ✅ **Generic error messages**: Internal details not exposed to clients
- ✅ **Server-side logging**: Full tracebacks logged server-side only
- ✅ **.gitignore configured**: Prevents accidental commit of `.env` files

### Best Practices

1. Never commit your `.env` file to version control
2. Use strong API tokens for Linkwarden
3. Run behind a reverse proxy (nginx, Traefik) for production use
4. Enable HTTPS for external access

## Development

### Running Locally (without Docker)

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export LINKWARDEN_TOKEN=your_token

# Run the server
python server.py
```

### Building the Docker Image Manually

```bash
docker build -t frontpage .
docker run -p 8080:8080 --env-file .env frontpage
```

## Troubleshooting

### Bookmark Service Connection Issues

- Verify `BOOKMARK_SERVICE` is set correctly (`linkwarden` or `karakeep`)
- Check that the corresponding `*_HOST` URL is accessible from the container
- Ensure the API token (`*_TOKEN`) is valid and has proper permissions
- Review container logs: `docker compose logs frontpage`

### Linkwarden-Specific Issues

- Verify `LINKWARDEN_HOST` is accessible from the container
- Check that `LINKWARDEN_TOKEN` is valid
- Review container logs: `docker compose logs frontpage`

### Karakeep-Specific Issues

- Verify `KARAKEEP_HOST` is accessible from the container
- Check that `KARAKEEP_TOKEN` is valid
- Ensure the tag filter (if used) exists in your Karakeep instance
- Review container logs: `docker compose logs frontpage`

### Data Persistence

Services are stored in `./data/services.json`. Ensure the `data/` directory has proper write permissions.

### Port Conflicts

If port 8080 is in use, modify the port mapping in `docker-compose.yml`:
```yaml
ports:
  - "8081:8080"  # Change host port to 8081
```

## License

MIT License - feel free to use and modify as needed.

## Acknowledgments

- [Linkwarden](https://linkwarden.app/) - Self-hosted bookmark manager
- [Karakeep](https://karakeep.com/) - Self-hosted bookmark and link manager
- [Hacker News](https://news.ycombinator.com/) - Tech news community
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
