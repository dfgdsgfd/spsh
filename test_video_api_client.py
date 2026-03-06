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

    def test_headers_with_api_key(self):
        headers = video_api_client._build_headers()
        self.assertEqual(headers["Accept"], "application/json")
        self.assertEqual(
            headers["X-API-KEY"],
            "ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56",
        )

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

    def test_invalid_per_page_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.get_posts(per_page=0)
        with self.assertRaises(ValueError):
            video_api_client.get_posts(per_page=-5)
        with self.assertRaises(ValueError):
            video_api_client.get_posts(per_page="not_int")

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

        result = video_api_client.get_posts(page=2, per_page=10, order="desc")
        self.assertEqual(result, {"total": 5})

        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertIn("page=2", req.full_url)
        self.assertIn("per_page=10", req.full_url)
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
        mock_gp.assert_called_once_with(page=2, per_page=None, order=None)

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

    @patch("video_api_client.generate_review_html", return_value="/tmp/review.html")
    def test_main_review(self, mock_rv):
        with patch("sys.argv", ["prog", "review", "--output", "/tmp/review.html"]):
            video_api_client.main()
        mock_rv.assert_called_once_with(output_path="/tmp/review.html")

    @patch("video_api_client.toggle_video_enable", return_value={"success": True})
    def test_main_toggle_disable(self, mock_tg):
        with patch("sys.argv", ["prog", "toggle", "100", "--disable"]):
            video_api_client.main()
        mock_tg.assert_called_once_with(post_id=100, enable=False)

    @patch("video_api_client.toggle_video_enable", return_value={"success": True})
    def test_main_toggle_enable(self, mock_tg):
        with patch("sys.argv", ["prog", "toggle", "100", "--enable"]):
            video_api_client.main()
        mock_tg.assert_called_once_with(post_id=100, enable=True)


class TestToggleVideoEnable(unittest.TestCase):
    """Tests for toggle_video_enable function."""

    def test_invalid_post_id_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.toggle_video_enable(post_id=0, enable=True)
        with self.assertRaises(ValueError):
            video_api_client.toggle_video_enable(post_id=-1, enable=False)
        with self.assertRaises(ValueError):
            video_api_client.toggle_video_enable(post_id="abc", enable=True)

    def test_invalid_enable_raises(self):
        with self.assertRaises(ValueError):
            video_api_client.toggle_video_enable(post_id=1, enable="yes")
        with self.assertRaises(ValueError):
            video_api_client.toggle_video_enable(post_id=1, enable=1)

    @patch("video_api_client.urllib.request.urlopen")
    def test_toggle_disable_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = video_api_client.toggle_video_enable(post_id=100, enable=False)
        self.assertEqual(result, {"success": True})

        call_args = mock_urlopen.call_args
        req = call_args[0][0]
        self.assertEqual(req.method, "POST")
        self.assertIn("video-enable-toggle", req.full_url)
        self.assertEqual(req.get_header("Content-type"), "application/json")

        body = json.loads(req.data.decode("utf-8"))
        self.assertEqual(body["post_id"], 100)
        self.assertFalse(body["enable"])

    @patch("video_api_client.urllib.request.urlopen")
    def test_toggle_enable_sends_correct_request(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({"success": True}).encode("utf-8")
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_resp

        result = video_api_client.toggle_video_enable(post_id=200, enable=True)
        self.assertEqual(result, {"success": True})

        body = json.loads(mock_urlopen.call_args[0][0].data.decode("utf-8"))
        self.assertEqual(body["post_id"], 200)
        self.assertTrue(body["enable"])


class TestGenerateReviewHtml(unittest.TestCase):
    """Tests for generate_review_html function."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_generates_html_file(self):
        output = os.path.join(self.test_dir, "review.html")
        result = video_api_client.generate_review_html(output_path=output)
        self.assertEqual(result, output)
        self.assertTrue(os.path.isfile(output))

    def test_html_contains_hls_js(self):
        output = os.path.join(self.test_dir, "review.html")
        video_api_client.generate_review_html(output_path=output)
        with open(output, encoding="utf-8") as f:
            html = f.read()
        self.assertIn("hls.js", html.lower())

    def test_html_contains_hardcoded_config(self):
        output = os.path.join(self.test_dir, "review.html")
        video_api_client.generate_review_html(output_path=output)
        with open(output, encoding="utf-8") as f:
            html = f.read()
        self.assertIn("https://v.yuelk.com", html)
        self.assertIn("ef13c2bdf8cd8550ed4c37c323a558c9985d6d928d39a3b53bed864460221d56", html)

    def test_html_contains_approve_reject_buttons(self):
        output = os.path.join(self.test_dir, "review.html")
        video_api_client.generate_review_html(output_path=output)
        with open(output, encoding="utf-8") as f:
            html = f.read()
        self.assertIn("通过", html)
        self.assertIn("拒绝", html)
        self.assertIn("btn-approve", html)
        self.assertIn("btn-reject", html)

    def test_html_uses_video_enable_toggle_endpoint(self):
        output = os.path.join(self.test_dir, "review.html")
        video_api_client.generate_review_html(output_path=output)
        with open(output, encoding="utf-8") as f:
            html = f.read()
        self.assertIn("video-enable-toggle", html)

    def test_html_supports_m3u8(self):
        output = os.path.join(self.test_dir, "review.html")
        video_api_client.generate_review_html(output_path=output)
        with open(output, encoding="utf-8") as f:
            html = f.read()
        self.assertIn(".m3u8", html)
        self.assertIn("Hls.isSupported", html)

    def test_creates_parent_dirs(self):
        output = os.path.join(self.test_dir, "sub", "dir", "review.html")
        result = video_api_client.generate_review_html(output_path=output)
        self.assertTrue(os.path.isfile(result))


if __name__ == "__main__":
    unittest.main()
