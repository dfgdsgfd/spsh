"""Tests for video_api_client module."""

import json
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock
from io import BytesIO
from urllib.error import HTTPError

import video_api_client


class TestBuildHeaders(unittest.TestCase):
    """Tests for _build_headers helper."""

    @patch.object(video_api_client, "API_KEY", "test-key-123")
    def test_headers_with_api_key(self):
        headers = video_api_client._build_headers()
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(headers["X-API-KEY"], "test-key-123")

    @patch.object(video_api_client, "API_KEY", "")
    def test_headers_without_api_key_when_empty(self):
        headers = video_api_client._build_headers()
        self.assertNotIn("X-API-KEY", headers)

    @patch.object(video_api_client, "API_KEY", "some-key")
    def test_headers_skip_api_key_when_flag_false(self):
        headers = video_api_client._build_headers(with_api_key=False)
        self.assertNotIn("X-API-KEY", headers)

    def test_custom_accept(self):
        headers = video_api_client._build_headers(accept="text/html", with_api_key=False)
        self.assertEqual(headers["Accept"], "text/html")


class TestGetPosts(unittest.TestCase):
    """Tests for get_posts function."""

    def test_page_must_be_positive(self):
        with self.assertRaises(ValueError):
            video_api_client.get_posts(page=0)
        with self.assertRaises(ValueError):
            video_api_client.get_posts(page=-1)

    def test_invalid_order_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.get_posts(order="INVALID")

    @patch("video_api_client.urllib.request.urlopen")
    def test_get_posts_default_params(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"posts": []}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = video_api_client.get_posts()
        self.assertEqual(result, {"posts": []})

        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertIn("page=1", req.full_url)

    @patch("video_api_client.urllib.request.urlopen")
    def test_get_posts_with_all_params(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"total": 5}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = video_api_client.get_posts(page=2, per_page=10, search="test", order="desc")
        self.assertEqual(result, {"total": 5})

        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertIn("page=2", req.full_url)
        self.assertIn("per_page=10", req.full_url)
        self.assertIn("search=test", req.full_url)
        self.assertIn("sort_order=DESC", req.full_url)

    def test_order_case_insensitive(self):
        # Should not raise for lowercase
        with patch("video_api_client.urllib.request.urlopen") as mock_urlopen:
            mock_resp = MagicMock()
            mock_resp.read.return_value = b'{"ok": true}'
            mock_resp.__enter__ = lambda s: s
            mock_resp.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_resp

            video_api_client.get_posts(order="asc")
            req = mock_urlopen.call_args[0][0]
            self.assertIn("sort_order=ASC", req.full_url)


class TestBatchDisableVideos(unittest.TestCase):
    """Tests for batch_disable_videos function."""

    def test_empty_post_ids_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.batch_disable_videos([])

    def test_non_integer_post_ids_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.batch_disable_videos(["not_an_int"])

    def test_mixed_types_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.batch_disable_videos([1, "two", 3])

    @patch("video_api_client.urllib.request.urlopen")
    def test_batch_disable_sends_post_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = video_api_client.batch_disable_videos([100, 200, 300])
        self.assertEqual(result, {"success": True})

        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertEqual(req.method, "POST")
        self.assertIn("batch-disable", req.full_url)
        self.assertEqual(req.get_header("Content-type"), "application/json")

        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["post_ids"], [100, 200, 300])


class TestGenerateApiDocs(unittest.TestCase):
    """Tests for generate_api_docs function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    @patch("video_api_client.urllib.request.urlopen")
    def test_generates_html_and_markdown(self, mock_urlopen):
        spec = {
            "openapi": "3.1.0",
            "info": {"title": "Test API", "version": "1.0.0", "description": "Test"},
            "paths": {
                "/test": {
                    "get": {
                        "summary": "Test Endpoint",
                        "description": "A test endpoint",
                        "parameters": [
                            {
                                "name": "q",
                                "in": "query",
                                "schema": {"type": "string"},
                                "required": False,
                            }
                        ],
                    }
                }
            },
        }
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(spec).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        output = os.path.join(self.test_dir, "docs")
        result = video_api_client.generate_api_docs(output_path=output)

        self.assertTrue(os.path.isfile(result))
        self.assertTrue(os.path.isfile(os.path.join(output, "openapi.json")))
        self.assertTrue(os.path.isfile(os.path.join(output, "api_reference.md")))
        self.assertTrue(os.path.isfile(os.path.join(output, "index.html")))

        # Check HTML contains ReDoc
        with open(os.path.join(output, "index.html"), encoding="utf-8") as f:
            html = f.read()
        self.assertIn("redoc", html.lower())
        self.assertIn("Test API", html)

        # Check Markdown contains endpoint info
        with open(os.path.join(output, "api_reference.md"), encoding="utf-8") as f:
            md = f.read()
        self.assertIn("GET", md)
        self.assertIn("/test", md)
        self.assertIn("Test Endpoint", md)

    @patch("video_api_client.urllib.request.urlopen")
    def test_no_auth_header_for_docs(self, mock_urlopen):
        spec = {"openapi": "3.1.0", "info": {"title": "T", "version": "1"}, "paths": {}}
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(spec).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        output = os.path.join(self.test_dir, "docs2")
        video_api_client.generate_api_docs(output_path=output)

        req = mock_urlopen.call_args[0][0]
        self.assertNotIn("X-API-KEY", dict(req.headers))


class TestMain(unittest.TestCase):
    """Tests for main() CLI entrypoint."""

    @patch("video_api_client.get_posts", return_value={"posts": []})
    def test_main_get_posts(self, mock_gp):
        with patch("sys.argv", ["prog", "get_posts", "--page", "2"]):
            video_api_client.main()
        mock_gp.assert_called_once_with(page=2, per_page=None, search=None, order=None)

    @patch("video_api_client.batch_disable_videos", return_value={"success": True})
    def test_main_batch_disable(self, mock_bd):
        with patch("sys.argv", ["prog", "batch_disable", "1", "2", "3"]):
            video_api_client.main()
        mock_bd.assert_called_once_with([1, 2, 3])

    @patch("video_api_client.generate_api_docs", return_value="/tmp/docs/index.html")
    def test_main_generate_docs(self, mock_gd):
        with patch("sys.argv", ["prog", "generate_docs", "--output", "/tmp/docs"]):
            video_api_client.main()
        mock_gd.assert_called_once_with(output_path="/tmp/docs")


if __name__ == "__main__":
    unittest.main()
