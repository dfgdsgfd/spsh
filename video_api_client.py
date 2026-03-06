"""
Video Center API Client

A Python client for interacting with the PyVideo 2.3 API.
Supports:
  1. Fetching video center list (get_posts)
  2. Batch disabling videos (batch_disable)
  3. Toggle video enable/disable (toggle)
  4. Auto-generating API documentation from the OpenAPI spec
  5. Generating HTML video review page with m3u8 playback (review)

调用方式 (How to Call):

  1. 获取视频列表 (Get video list):
     python video_api_client.py get_posts --page 1 --per-page 20 --order DESC

  2. 批量禁用视频 (Batch disable videos):
     python video_api_client.py batch_disable 100 200 300

  3. 切换视频启用/禁用 (Toggle video enable/disable):
     python video_api_client.py toggle 100 --disable
     python video_api_client.py toggle 100 --enable

  4. 自动生成API文档 (Auto-generate API docs):
     python video_api_client.py generate_docs --output api_docs

  5. 生成视频审核HTML页面 (Generate video review HTML page):
     python video_api_client.py review --output review.html
     然后在浏览器中打开 review.html 即可使用

  作为库调用 (Use as a library):
     from video_api_client import get_posts, batch_disable_videos, toggle_video_enable
     from video_api_client import generate_api_docs, generate_review_html

     posts = get_posts(page=1, per_page=20, order="DESC")
     result = batch_disable_videos([100, 200, 300])
     result = toggle_video_enable(post_id=100, enable=False)
     generate_api_docs(output_path="api_docs")
     generate_review_html(output_path="review.html")
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error

# ============================================================
# 硬编码配置 (Hardcoded Configuration)
# ============================================================
BASE_URL = "https://v.yuelk.com"
API_KEY = "ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56"

# Public OpenAPI documentation endpoint (no authentication required)
OPENAPI_JSON_URL = "https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/openapi.json"


def _build_headers(accept="application/json", with_api_key=True):
    """Build HTTP request headers.

    Args:
        accept: Accept header value.
        with_api_key: Whether to include the X-API-KEY header.

    Returns:
        Dictionary of HTTP headers.
    """
    headers = {"Accept": accept}
    if with_api_key:
        headers["X-API-KEY"] = API_KEY
    return headers


def get_posts(page=1, per_page=None, order=None):
    """Get the video center post list.

    调用方式 (How to call):
        # 命令行 (CLI):
        python video_api_client.py get_posts --page 1 --per-page 20 --order DESC

        # Python 代码调用 (Python code):
        from video_api_client import get_posts
        result = get_posts(page=1, per_page=20, order="DESC")

        # curl 调用 (curl):
        curl -H 'accept: application/json' \\
             -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \\
             'https://v.yuelk.com/pyvideo2/api/get_posts?page=1&per_page=20&sort_order=DESC'

    Args:
        page: Page number (integer, >= 1). Defaults to 1.
        per_page: Number of items per page (integer, optional).
        order: Sort order, either ``"ASC"`` or ``"DESC"`` (optional).

    Returns:
        Parsed JSON response from the API as a dictionary.

    Raises:
        ValueError: If *page* is less than 1 or *order* is invalid.
        urllib.error.URLError: On network errors.
        urllib.error.HTTPError: On HTTP error responses.
    """
    if page < 1:
        raise ValueError("page must be >= 1")
    if order is not None and order.upper() not in ("ASC", "DESC"):
        raise ValueError("order must be 'ASC' or 'DESC'")

    params = {"page": str(page)}
    if per_page is not None:
        if not isinstance(per_page, int) or per_page < 1:
            raise ValueError("per_page must be a positive integer")
        params["per_page"] = str(per_page)
    if order:
        params["sort_order"] = order.upper()

    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/pyvideo2/api/get_posts?{query}"

    req = urllib.request.Request(url, headers=_build_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def batch_disable_videos(post_ids):
    """Batch disable videos by their post IDs.

    调用方式 (How to call):
        # 命令行 (CLI):
        python video_api_client.py batch_disable 100 200 300

        # Python 代码调用 (Python code):
        from video_api_client import batch_disable_videos
        result = batch_disable_videos([100, 200, 300])

        # curl 调用 (curl):
        curl -X POST \\
             -H 'accept: application/json' \\
             -H 'Content-Type: application/json' \\
             -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \\
             -d '{"post_ids": [100, 200, 300]}' \\
             'https://v.yuelk.com/pyvideo2/api/admin/moderation/batch-disable'

    Sends a POST request to the admin moderation batch-disable endpoint.

    Args:
        post_ids: A list of integer post IDs to disable.

    Returns:
        Parsed JSON response from the API as a dictionary.

    Raises:
        ValueError: If *post_ids* is empty or contains non-integers.
        urllib.error.URLError: On network errors.
        urllib.error.HTTPError: On HTTP error responses.
    """
    if not post_ids:
        raise ValueError("post_ids must not be empty")
    if not all(isinstance(pid, int) for pid in post_ids):
        raise ValueError("All post_ids must be integers")

    url = f"{BASE_URL}/pyvideo2/api/admin/moderation/batch-disable"
    body = json.dumps({"post_ids": post_ids}).encode("utf-8")

    headers = _build_headers()
    headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def toggle_video_enable(post_id, enable):
    """Toggle a video's enable status by post_id.

    调用方式 (How to call):
        # 命令行 (CLI) — 禁用视频:
        python video_api_client.py toggle 100 --disable

        # 命令行 (CLI) — 启用视频:
        python video_api_client.py toggle 100 --enable

        # Python 代码调用 (Python code):
        from video_api_client import toggle_video_enable
        result = toggle_video_enable(post_id=100, enable=False)   # 禁用
        result = toggle_video_enable(post_id=100, enable=True)    # 启用

        # curl 调用 (curl) — 禁用视频:
        curl -X POST \\
             -H 'accept: application/json' \\
             -H 'Content-Type: application/json' \\
             -H 'X-API-KEY: ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56' \\
             -d '{"post_id": 100, "enable": false}' \\
             'https://v.yuelk.com/pyvideo2/api/admin/video-enable-toggle'

    API文档参考:
        https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/docs#/admin/toggle_video_enable_endpoint_pyvideo2_api_admin_video_enable_toggle_post

    Args:
        post_id: The video's post ID (integer, required).
        enable: True to enable the video, False to disable (boolean, required).

    Returns:
        Parsed JSON response from the API as a dictionary.

    Raises:
        ValueError: If *post_id* is not a positive integer.
        urllib.error.URLError: On network errors.
        urllib.error.HTTPError: On HTTP error responses.
    """
    if not isinstance(post_id, int) or post_id < 1:
        raise ValueError("post_id must be a positive integer")
    if not isinstance(enable, bool):
        raise ValueError("enable must be a boolean")

    url = f"{BASE_URL}/pyvideo2/api/admin/video-enable-toggle"
    body = json.dumps({"post_id": post_id, "enable": enable}).encode("utf-8")

    headers = _build_headers()
    headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def generate_api_docs(output_path="api_docs"):
    """Fetch the OpenAPI specification and generate local API documentation.

    调用方式 (How to call):
        # 命令行 (CLI):
        python video_api_client.py generate_docs --output api_docs

        # Python 代码调用 (Python code):
        from video_api_client import generate_api_docs
        html_path = generate_api_docs(output_path="api_docs")

    The OpenAPI JSON endpoint is publicly accessible and does **not**
    require authentication.
    API文档地址: https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/redoc

    Args:
        output_path: Directory where documentation files will be written.

    Returns:
        Path to the generated ``index.html`` file.
    """
    os.makedirs(output_path, exist_ok=True)

    # Fetch the OpenAPI spec (no auth required)
    req = urllib.request.Request(OPENAPI_JSON_URL, headers=_build_headers(with_api_key=False))
    with urllib.request.urlopen(req) as resp:
        spec = json.loads(resp.read().decode("utf-8"))

    # Save the raw OpenAPI JSON
    spec_path = os.path.join(output_path, "openapi.json")
    with open(spec_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)

    # Generate a self-contained HTML documentation page using ReDoc
    title = spec.get("info", {}).get("title", "API Documentation")
    version = spec.get("info", {}).get("version", "")
    description = spec.get("info", {}).get("description", "")

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>{title} {version}</title>
    <meta name="description" content="{description}" />
    <link href="https://fonts.googleapis.com/css?family=Montserrat:300,400,700|Roboto:300,400,700" rel="stylesheet" />
    <style>
        body {{ margin: 0; padding: 0; }}
    </style>
</head>
<body>
    <redoc spec-url="openapi.json"></redoc>
    <script src="https://cdn.jsdelivr.net/npm/redoc@2.4.0/bundles/redoc.standalone.js"
            integrity="sha256-FCWbfEOaKHMF75vN7Fzj1cPP5/wIBBMKe70xqiLNpHk="
            crossorigin="anonymous"></script>
</body>
</html>
"""

    html_path = os.path.join(output_path, "index.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # Generate a Markdown summary of all endpoints
    md_lines = [f"# {title} {version}\n", f"{description}\n"]

    for path, methods in spec.get("paths", {}).items():
        for method, detail in methods.items():
            if method in ("get", "post", "put", "delete", "patch", "head", "options"):
                summary = detail.get("summary", "")
                desc = detail.get("description", "").split("\n")[0]
                md_lines.append(f"## `{method.upper()}` {path}\n")
                if summary:
                    md_lines.append(f"**{summary}**\n")
                if desc:
                    md_lines.append(f"{desc}\n")

                params = detail.get("parameters", [])
                if params:
                    md_lines.append("| Parameter | In | Type | Required |")
                    md_lines.append("|---|---|---|---|")
                    for p in params:
                        pname = p.get("name", "")
                        pin = p.get("in", "")
                        ptype = p.get("schema", {}).get("type", "")
                        preq = "Yes" if p.get("required") else "No"
                        md_lines.append(f"| {pname} | {pin} | {ptype} | {preq} |")
                    md_lines.append("")

                md_lines.append("")

    md_path = os.path.join(output_path, "api_reference.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    return html_path


def generate_review_html(output_path="review.html"):
    """Generate a self-contained HTML video review page.

    调用方式 (How to call):
        # 命令行 (CLI):
        python video_api_client.py review --output review.html

        # Python 代码调用 (Python code):
        from video_api_client import generate_review_html
        html_path = generate_review_html(output_path="review.html")

        # 然后在浏览器中打开 review.html 即可使用

    The generated HTML page:
      - Fetches the video list from the API (hardcoded BASE_URL and API_KEY)
      - Supports m3u8 video playback via HLS.js
      - Displays each video with two buttons:
        - 左边「通过」(Approve): skip to next video, no disable action
        - 右边「拒绝」(Reject): call video-enable-toggle API to disable, then next video

    API文档参考:
        https://v.yuelk.com/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/docs#/admin/toggle_video_enable_endpoint_pyvideo2_api_admin_video_enable_toggle_post

    Args:
        output_path: File path for the generated HTML file.

    Returns:
        Path to the generated HTML file.
    """
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>视频审核 Video Review</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@1.5.7"></script>
<style>
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
       background: #1a1a2e; color: #eee; min-height: 100vh; }}
#app {{ max-width: 900px; margin: 0 auto; padding: 20px; }}
h1 {{ text-align: center; margin-bottom: 10px; font-size: 1.5em; }}
#status {{ text-align: center; color: #aaa; margin-bottom: 20px; font-size: 0.9em; }}
#player-container {{ position: relative; width: 100%; background: #000; border-radius: 8px;
                     overflow: hidden; margin-bottom: 20px; }}
video {{ width: 100%; display: block; max-height: 70vh; }}
#video-info {{ padding: 10px 0; }}
#video-info h2 {{ font-size: 1.1em; margin-bottom: 5px; }}
#video-info p {{ color: #aaa; font-size: 0.85em; }}
#buttons {{ display: flex; gap: 20px; margin-top: 20px; }}
#buttons button {{ flex: 1; padding: 16px; font-size: 1.2em; font-weight: bold;
                   border: none; border-radius: 8px; cursor: pointer; transition: all 0.2s; }}
#btn-approve {{ background: #27ae60; color: #fff; }}
#btn-approve:hover {{ background: #2ecc71; }}
#btn-approve:disabled {{ background: #555; color: #888; cursor: not-allowed; }}
#btn-reject {{ background: #c0392b; color: #fff; }}
#btn-reject:hover {{ background: #e74c3c; }}
#btn-reject:disabled {{ background: #555; color: #888; cursor: not-allowed; }}
#message {{ text-align: center; margin-top: 15px; padding: 10px; border-radius: 6px;
            font-size: 0.9em; min-height: 40px; }}
.msg-ok {{ background: rgba(39,174,96,0.2); color: #2ecc71; }}
.msg-err {{ background: rgba(192,57,43,0.2); color: #e74c3c; }}
.msg-info {{ background: rgba(52,152,219,0.15); color: #5dade2; }}
#loading {{ text-align: center; padding: 60px 0; color: #aaa; }}
#done {{ text-align: center; padding: 60px 0; }}
#done h2 {{ color: #2ecc71; margin-bottom: 10px; }}
#pagination {{ display: flex; justify-content: center; gap: 10px; margin-top: 15px; }}
#pagination button {{ padding: 8px 18px; border: 1px solid #444; background: #2a2a3e;
                      color: #eee; border-radius: 6px; cursor: pointer; }}
#pagination button:disabled {{ color: #555; cursor: not-allowed; }}
#pagination button:hover:not(:disabled) {{ background: #3a3a5e; }}
</style>
</head>
<body>
<div id="app">
  <h1>📹 视频审核系统</h1>
  <div id="status">正在加载视频列表...</div>
  <div id="loading">⏳ Loading...</div>
  <div id="review-area" style="display:none;">
    <div id="player-container">
      <video id="video-player" controls playsinline></video>
    </div>
    <div id="video-info">
      <h2 id="video-title"></h2>
      <p id="video-meta"></p>
    </div>
    <div id="buttons">
      <button id="btn-approve" onclick="approve()">✅ 通过</button>
      <button id="btn-reject" onclick="reject()">❌ 拒绝</button>
    </div>
    <div id="message"></div>
    <div id="pagination">
      <button id="btn-prev-page" onclick="prevPage()">⬅ 上一页</button>
      <span id="page-info" style="line-height:36px;color:#aaa;"></span>
      <button id="btn-next-page" onclick="nextPage()">下一页 ➡</button>
    </div>
  </div>
  <div id="done" style="display:none;">
    <h2>🎉 本页审核完毕</h2>
    <p>所有视频已审核完成，可翻页继续。</p>
  </div>
</div>

<script>
// ============================================================
// 硬编码配置 (Hardcoded Configuration)
// ============================================================
const BASE_URL = "{BASE_URL}";
const API_KEY  = "{API_KEY}";

let videos = [];
let currentIndex = 0;
let currentPage = 1;
let totalPages = 1;
let hls = null;
let busy = false;

async function fetchVideos(page) {{
  const url = BASE_URL + "/pyvideo2/api/get_posts?page=" + page;
  const resp = await fetch(url, {{
    headers: {{ "Accept": "application/json", "X-API-KEY": API_KEY }}
  }});
  if (!resp.ok) throw new Error("HTTP " + resp.status);
  return await resp.json();
}}

async function disableVideo(postId) {{
  const url = BASE_URL + "/pyvideo2/api/admin/video-enable-toggle";
  const resp = await fetch(url, {{
    method: "POST",
    headers: {{
      "Accept": "application/json",
      "Content-Type": "application/json",
      "X-API-KEY": API_KEY
    }},
    body: JSON.stringify({{ post_id: postId, enable: false }})
  }});
  if (!resp.ok) throw new Error("HTTP " + resp.status);
  return await resp.json();
}}

function showMessage(text, type) {{
  const el = document.getElementById("message");
  el.textContent = text;
  el.className = type === "ok" ? "msg-ok" : type === "err" ? "msg-err" : "msg-info";
  if (type !== "err") setTimeout(() => {{ el.textContent = ""; el.className = ""; }}, 3000);
}}

function playVideo(url) {{
  const video = document.getElementById("video-player");
  if (hls) {{ hls.destroy(); hls = null; }}

  if (url && url.includes(".m3u8")) {{
    if (Hls.isSupported()) {{
      hls = new Hls();
      hls.loadSource(url);
      hls.attachMedia(video);
      hls.on(Hls.Events.MANIFEST_PARSED, () => video.play().catch(() => {{}}));
    }} else if (video.canPlayType("application/vnd.apple.mpegurl")) {{
      video.src = url;
      video.addEventListener("loadedmetadata", () => video.play().catch(() => {{}}), {{ once: true }});
    }}
  }} else if (url) {{
    video.src = url;
    video.play().catch(() => {{}});
  }}
}}

function getVideoUrl(post) {{
  // Try common field names for the video URL
  return post.video_url || post.url || post.video || post.media_url
      || post.file_url || post.stream_url || post.hls_url || "";
}}

function getVideoTitle(post) {{
  return post.title || post.name || ("Video #" + (post.id || post.post_id || ""));
}}

function getVideoId(post) {{
  return post.id || post.post_id || post.ID || 0;
}}

function showCurrentVideo() {{
  if (currentIndex >= videos.length) {{
    document.getElementById("review-area").style.display = "none";
    document.getElementById("done").style.display = "block";
    updateStatus();
    return;
  }}
  document.getElementById("review-area").style.display = "block";
  document.getElementById("done").style.display = "none";

  const post = videos[currentIndex];
  const videoUrl = getVideoUrl(post);
  const title = getVideoTitle(post);
  const postId = getVideoId(post);

  document.getElementById("video-title").textContent = title;
  document.getElementById("video-meta").textContent =
    "ID: " + postId + " | " + (currentIndex + 1) + " / " + videos.length;

  playVideo(videoUrl);
  updateStatus();
  setBusy(false);
}}

function updateStatus() {{
  const remain = Math.max(0, videos.length - currentIndex);
  document.getElementById("status").textContent =
    "第 " + currentPage + " 页 | 剩余 " + remain + " 个视频待审核";
  document.getElementById("page-info").textContent = "第 " + currentPage + " 页";
}}

function setBusy(val) {{
  busy = val;
  document.getElementById("btn-approve").disabled = val;
  document.getElementById("btn-reject").disabled = val;
}}

function approve() {{
  if (busy) return;
  showMessage("✅ 已通过，跳到下一个", "ok");
  currentIndex++;
  showCurrentVideo();
}}

async function reject() {{
  if (busy) return;
  const post = videos[currentIndex];
  const postId = getVideoId(post);
  if (!postId) {{
    showMessage("⚠ 无法获取视频 ID", "err");
    return;
  }}
  setBusy(true);
  showMessage("⏳ 正在禁用视频 " + postId + " ...", "info");
  try {{
    await disableVideo(postId);
    showMessage("❌ 视频 " + postId + " 已禁用", "ok");
    currentIndex++;
    setTimeout(showCurrentVideo, 800);
  }} catch (e) {{
    showMessage("禁用失败: " + e.message, "err");
    setBusy(false);
  }}
}}

async function loadPage(page) {{
  document.getElementById("loading").style.display = "block";
  document.getElementById("review-area").style.display = "none";
  document.getElementById("done").style.display = "none";
  try {{
    const data = await fetchVideos(page);
    videos = data.posts || data.data || data.results || data.items || [];
    if (Array.isArray(data) && !videos.length) videos = data;
    totalPages = data.total_pages || data.pages || Math.ceil((data.total || videos.length) / 20) || 1;
    currentPage = page;
    currentIndex = 0;
    document.getElementById("loading").style.display = "none";
    if (videos.length === 0) {{
      document.getElementById("status").textContent = "此页没有视频";
      document.getElementById("done").style.display = "block";
      document.getElementById("done").querySelector("h2").textContent = "📭 暂无视频";
      document.getElementById("done").querySelector("p").textContent = "当前页没有可审核的视频。";
    }} else {{
      showCurrentVideo();
    }}
    document.getElementById("btn-prev-page").disabled = (currentPage <= 1);
    document.getElementById("btn-next-page").disabled = (currentPage >= totalPages);
  }} catch (e) {{
    document.getElementById("loading").style.display = "none";
    document.getElementById("status").textContent = "加载失败: " + e.message;
  }}
}}

function prevPage() {{ if (currentPage > 1) loadPage(currentPage - 1); }}
function nextPage() {{ if (currentPage < totalPages) loadPage(currentPage + 1); }}

// Start
loadPage(1);
</script>
</body>
</html>
"""

    # Ensure parent directory exists
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    return output_path


def main():
    """Command-line interface for the video API client."""
    import argparse

    parser = argparse.ArgumentParser(description="Video Center API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # get_posts command
    gp = subparsers.add_parser("get_posts", help="Get video center list")
    gp.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    gp.add_argument("--per-page", type=int, default=None, help="Items per page")
    gp.add_argument("--order", type=str, default=None, choices=["ASC", "DESC", "asc", "desc"],
                     help="Sort order (ASC or DESC)")

    # batch_disable command
    bd = subparsers.add_parser("batch_disable", help="Batch disable videos")
    bd.add_argument("post_ids", type=int, nargs="+", help="Post IDs to disable")

    # generate_docs command
    gd = subparsers.add_parser("generate_docs", help="Auto-generate API documentation")
    gd.add_argument("--output", type=str, default="api_docs",
                     help="Output directory (default: api_docs)")

    # review command
    rv = subparsers.add_parser("review", help="Generate HTML video review page")
    rv.add_argument("--output", type=str, default="review.html",
                     help="Output HTML file (default: review.html)")

    # toggle command
    tg = subparsers.add_parser("toggle", help="Toggle video enable/disable")
    tg.add_argument("post_id", type=int, help="Post ID to toggle")
    tg_group = tg.add_mutually_exclusive_group(required=True)
    tg_group.add_argument("--enable", action="store_true", help="Enable the video")
    tg_group.add_argument("--disable", action="store_true", help="Disable the video")

    args = parser.parse_args()

    if args.command == "get_posts":
        result = get_posts(
            page=args.page,
            per_page=args.per_page,
            order=args.order,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "batch_disable":
        result = batch_disable_videos(args.post_ids)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "generate_docs":
        path = generate_api_docs(output_path=args.output)
        print(f"API documentation generated at: {path}")

    elif args.command == "review":
        path = generate_review_html(output_path=args.output)
        print(f"Video review page generated at: {path}")
        print("Open this file in a browser to start reviewing videos.")

    elif args.command == "toggle":
        enable = args.enable  # True if --enable, False if --disable
        result = toggle_video_enable(post_id=args.post_id, enable=enable)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
