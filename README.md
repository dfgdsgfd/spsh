# spsh — Video Center API Client

A Python client for the **PyVideo 2.3** API. All configuration values are **hardcoded** in the
source code — no environment variables needed. Supports fetching the video center list,
batch-disabling videos, toggling video enable/disable, auto-generating API documentation,
and generating an HTML video review page with m3u8 playback support.

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

# Get page 2, 20 items per page, sort descending
python video_api_client.py get_posts --page 2 --per-page 20 --order DESC
```

**Python 代码调用:**

```python
from video_api_client import get_posts

# Get first page with default settings
result = get_posts()

# Get with all parameters
result = get_posts(page=1, per_page=20, order="DESC")
print(result)
```

**curl 调用:**

```bash
curl -H 'accept: application/json' \
     -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \
     'https://v.yuelk.com/pyvideo2/api/get_posts?page=1&per_page=20&sort_order=DESC'
```

Parameters:

| Parameter | Type | Description |
|---|---|---|
| `page` | int | Page number (default: 1) |
| `per_page` | int | Items per page (optional) |
| `order` | str | Sort order: `ASC` or `DESC` (optional) |

### 2. Toggle Video Enable/Disable (切换视频启用/禁用)

Uses the [`video-enable-toggle`](https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/docs#/admin/toggle_video_enable_endpoint_pyvideo2_api_admin_video_enable_toggle_post) endpoint.

**CLI 命令行调用:**

```bash
# Disable a video
python video_api_client.py toggle 100 --disable

# Enable a video
python video_api_client.py toggle 100 --enable
```

**Python 代码调用:**

```python
from video_api_client import toggle_video_enable

# Disable video
result = toggle_video_enable(post_id=100, enable=False)

# Enable video
result = toggle_video_enable(post_id=100, enable=True)
print(result)
```

**curl 调用:**

```bash
# Disable video
curl -X POST \
     -H 'accept: application/json' \
     -H 'Content-Type: application/json' \
     -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \
     -d '{"post_id": 100, "enable": false}' \
     'https://v.yuelk.com/pyvideo2/api/admin/video-enable-toggle'
```

### 3. Batch Disable Videos (批量禁用视频)

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

### 4. Video Review HTML Page (视频审核页面)

Generate a self-contained HTML page for reviewing videos with m3u8 playback support.
The page displays each video with:
- **左边「✅ 通过」按钮** — Approve: skip to next video, **no disable action**
- **右边「❌ 拒绝」按钮** — Reject: call `video-enable-toggle` API to **disable** the video, then move to next

**CLI 命令行调用:**

```bash
python video_api_client.py review --output review.html
# Then open review.html in a browser
```

**Python 代码调用:**

```python
from video_api_client import generate_review_html

html_path = generate_review_html(output_path="review.html")
print(f"Open in browser: {html_path}")
```

Features:
- **m3u8 playback** via HLS.js (also supports mp4 and other formats)
- **通过 (Approve)**: no API call, just skip to next video
- **拒绝 (Reject)**: calls `POST /pyvideo2/api/admin/video-enable-toggle` with `{"post_id": X, "enable": false}`
- Pagination support for browsing through pages of videos
- All config hardcoded (API key, base URL) — just open the HTML file

### 5. Auto-Generate API Documentation (自动生成API文档)

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