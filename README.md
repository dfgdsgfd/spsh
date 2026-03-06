# spsh — Video Center API Client

A Python client for the **PyVideo 2.3** API. All configuration values are **hardcoded** in the
source code — no environment variables needed. Supports fetching the video center list,
batch-disabling videos, and auto-generating API documentation from the public OpenAPI specification.

## Requirements

- Python 3.7+
- No third-party dependencies (uses only the standard library)

## Hardcoded Configuration

All values are hardcoded in `video_api_client.py`:

| Constant | Value |
|---|---|
| `BASE_URL` | `https://v.yuelk.com` |
| `API_KEY` | `ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56` |
| `OPENAPI_JSON_URL` | `https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/openapi.json` |

## Usage

### 1. Get Video Center List (获取视频中心列表)

**CLI 命令行调用:**

```bash
# Get page 1 (default)
python video_api_client.py get_posts

# Get page 2, 20 items per page, search for a keyword, sort descending
python video_api_client.py get_posts --page 2 --per-page 20 --search "关键词" --order DESC
```

**Python 代码调用:**

```python
from video_api_client import get_posts

# Get first page with default settings
result = get_posts()

# Get with all parameters
result = get_posts(page=1, per_page=20, search="关键词", order="DESC")
print(result)
```

**curl 调用:**

```bash
curl -H 'accept: application/json' \
     -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \
     'https://v.yuelk.com/pyvideo2/api/get_posts?page=1&per_page=20&search=关键词&sort_order=DESC'
```

Parameters:

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Items per page (optional) |
| `search` | str | Search keyword, can be empty (optional) |
| `order` | str | Sort order: `ASC` or `DESC` (optional) |

### 2. Batch Disable Videos (批量禁用视频)

**CLI 命令行调用:**

```bash
python video_api_client.py batch_disable 100 200 300
```

**Python 代码调用:**

```python
from video_api_client import batch_disable_videos

result = batch_disable_videos([100, 200, 300])
print(result)
```

**curl 调用:**

```bash
curl -X POST \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \
     -d '{"post_ids": [100, 200, 300]}' \
     'https://v.yuelk.com/pyvideo2/api/admin/moderation/batch-disable'
```

### 3. Auto-Generate API Documentation (自动生成API文档)

API documentation is publicly accessible **without authentication**.

Online API docs: https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/redoc

**CLI 命令行调用:**

```bash
python video_api_client.py generate_docs --output api_docs
```

**Python 代码调用:**

```python
from video_api_client import generate_api_docs

html_path = generate_api_docs(output_path="api_docs")
print(f"Documentation generated at: {html_path}")
```

This fetches the public OpenAPI spec and generates:

- `api_docs/openapi.json` — raw OpenAPI specification
- `api_docs/index.html` — interactive ReDoc documentation page
- `api_docs/api_reference.md` — Markdown API reference

## Running Tests

```bash
python -m pytest test_video_api_client.py -v
```

Or with the built-in test runner:

```bash
python -m unittest test_video_api_client -v
```