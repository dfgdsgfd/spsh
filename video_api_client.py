"""
Video Center API Client

A Python client for interacting with the PyVideo 2.3 API.
Supports:
  1. Fetching video center list (get_posts)
  2. Batch disabling videos (batch_disable)
  3. Auto-generating API documentation from the OpenAPI spec
"""

import json
import os
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = os.getenv("VIDEO_API_BASE_URL", "https://v.yuelk.com")
API_KEY = os.getenv("VIDEO_API_KEY", "")

# Public OpenAPI documentation endpoint (no authentication required)
OPENAPI_JSON_URL = os.getenv(
    "VIDEO_API_OPENAPI_URL",
    f"{BASE_URL}/2CBw2VMfDM4l6ZhoXqDrt9u4VCMRlEF1/openapi.json",
)


def _build_headers(accept="application/json", with_api_key=True):
    """Build HTTP request headers.

    Args:
        accept: Accept header value.
        with_api_key: Whether to include the X-API-KEY header.

    Returns:
        Dictionary of HTTP headers.
    """
    headers = {"Accept": accept}
    if with_api_key and API_KEY:
        headers["X-API-KEY"] = API_KEY
    return headers


def get_posts(page=1, per_page=None, search=None, order=None):
    """Get the video center post list.

    Args:
        page: Page number (integer, >= 1). Defaults to 1.
        per_page: Number of items per page (integer, optional).
        search: Search keyword (string, optional).
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
        params["per_page"] = str(int(per_page))
    if search:
        params["search"] = search
    if order:
        params["sort_order"] = order.upper()

    query = urllib.parse.urlencode(params)
    url = f"{BASE_URL}/pyvideo2/api/get_posts?{query}"

    req = urllib.request.Request(url, headers=_build_headers())
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def batch_disable_videos(post_ids):
    """Batch disable videos by their post IDs.

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


def generate_api_docs(output_path="api_docs"):
    """Fetch the OpenAPI specification and generate local API documentation.

    The OpenAPI JSON endpoint is publicly accessible and does **not**
    require authentication.

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
    <script src="https://cdn.jsdelivr.net/npm/redoc@2/bundles/redoc.standalone.js"></script>
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


def main():
    """Command-line interface for the video API client."""
    import argparse

    parser = argparse.ArgumentParser(description="Video Center API Client")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # get_posts command
    gp = subparsers.add_parser("get_posts", help="Get video center list")
    gp.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    gp.add_argument("--per-page", type=int, default=None, help="Items per page")
    gp.add_argument("--search", type=str, default=None, help="Search keyword")
    gp.add_argument("--order", type=str, default=None, choices=["ASC", "DESC", "asc", "desc"],
                     help="Sort order (ASC or DESC)")

    # batch_disable command
    bd = subparsers.add_parser("batch_disable", help="Batch disable videos")
    bd.add_argument("post_ids", type=int, nargs="+", help="Post IDs to disable")

    # generate_docs command
    gd = subparsers.add_parser("generate_docs", help="Auto-generate API documentation")
    gd.add_argument("--output", type=str, default="api_docs",
                     help="Output directory (default: api_docs)")

    args = parser.parse_args()

    if args.command == "get_posts":
        result = get_posts(
            page=args.page,
            per_page=args.per_page,
            search=args.search,
            order=args.order,
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "batch_disable":
        result = batch_disable_videos(args.post_ids)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "generate_docs":
        path = generate_api_docs(output_path=args.output)
        print(f"API documentation generated at: {path}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
