# Frontpage - Landing Page with Linkwarden Integration

A simple landing page dashboard that integrates with Linkwarden for bookmark management, displays Hacker News, and allows manual service links.

## Security Fixes Applied

- **Removed hardcoded credentials**: API tokens and IP addresses are now configured via environment variables
- **Disabled traceback exposure**: Error responses no longer expose stack traces to clients
- **Reduced logging verbosity**: Changed from DEBUG to INFO level for production use
- **Sanitized error messages**: API error responses don't leak internal details

## Configuration

All Linkwarden settings are configurable via environment variables in `docker-compose.yml`:

| Variable | Description | Default |
|----------|-------------|---------|
| `LINKWARDEN_HOST` | Linkwarden server URL | `http://localhost:3000` |
| `LINKWARDEN_TOKEN` | Linkwarden API token (required) | (empty) |
| `LINKWARDEN_COLLECTION_ID` | Filter to specific collection | (all collections) |
| `LINKWARDEN_LIMIT` | Number of random links to display | `10` |

## Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Linkwarden credentials:
   ```bash
   LINKWARDEN_HOST=http://your-linkwarden-host:3000
   LINKWARDEN_TOKEN=your_actual_api_token
   LINKWARDEN_COLLECTION_ID=  # Optional: filter by collection ID
   LINKWARDEN_LIMIT=10
   ```

3. Start the container:
   ```bash
   docker compose up -d
   ```

4. Access the landing page at `http://localhost:8080`

## Files

- `server.py` - FastAPI backend
- `index.html` - Frontend UI
- `docker-compose.yml` - Docker configuration with environment variables
- `.env.example` - Template for environment variables
- `.gitignore` - Prevents committing secrets

## Security Notes

- Never commit `.env` files to version control
- The `.gitignore` file prevents accidental commits of sensitive data
- All error messages sent to clients are generic; detailed logs stay server-side
