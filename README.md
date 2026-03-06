# spsh — Video Center API Client

A Python client for the **PyVideo 2.3** API. Supports fetching the video center
list, batch-disabling videos, and auto-generating API documentation from the
public OpenAPI specification.

## Requirements

- Python 3.7+
- No third-party dependencies (uses only the standard library)

## Configuration

Set the following environment variables before running:

| Variable | Description | Default |
|---|---|---|
| `VIDEO_API_KEY` | Your API key (`X-API-KEY` header) | *(empty – required for API calls)* |
| `VIDEO_API_BASE_URL` | Base URL of the API server | `https://v.yuelk.com` |
| `VIDEO_API_OPENAPI_URL` | URL for the OpenAPI JSON spec | `{BASE_URL}/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/openapi.json` |

Example:

```bash
export VIDEO_API_KEY="your_api_key_here"
```

## Usage

### 1. Get Video Center List

```bash
python video_api_client.py get_posts --page 1 --per-page 20 --search "keyword" --order DESC
```

Parameters:

| Parameter | Type | Description |
|---|---|---|
| `--page` | int | Page number (default: 1) |
| `--per-page` | int | Items per page (optional) |
| `--search` | str | Search keyword (optional) |
| `--order` | str | Sort order: `ASC` or `DESC` (optional) |

### 2. Batch Disable Videos

```bash
python video_api_client.py batch_disable 100 200 300
```

Provide one or more integer post IDs as arguments.

### 3. Auto-Generate API Documentation

```bash
python video_api_client.py generate_docs --output api_docs
```

This fetches the public OpenAPI spec (no authentication required) and generates:

- `api_docs/openapi.json` — raw OpenAPI specification
- `api_docs/index.html` — interactive ReDoc documentation page
- `api_docs/api_reference.md` — Markdown API reference

### Using as a Library

```python
import video_api_client

# Get video list
posts = video_api_client.get_posts(page=1, per_page=20, search="test", order="DESC")

# Batch disable videos
result = video_api_client.batch_disable_videos([100, 200, 300])

# Generate local API docs
video_api_client.generate_api_docs(output_path="api_docs")
```

## Running Tests

```bash
python -m pytest test_video_api_client.py -v
```

Or with the built-in test runner:

```bash
python -m unittest test_video_api_client -v
```