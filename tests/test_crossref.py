"""Offline behavior checks; all publication records here are synthetic fixtures."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import ssl
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlparse


SCRIPT = Path(__file__).resolve().parents[1] / "journal-suggester/scripts/crossref.py"
SPEC = importlib.util.spec_from_file_location("crossref_helper", SCRIPT)
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class CrossrefTests(unittest.TestCase):
    def test_tls_fallback_keeps_certificate_verification_enabled(self):
        context = helper.tls_context()
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    def test_query_is_encoded_and_contact_is_not_returned(self):
        response = io.BytesIO(b'{"status":"ok","message":{"items":[]}}')
        with patch.object(helper, "urlopen", return_value=response) as opened:
            _, public_url = helper.fetch_json("/works", {"query": "soil & water / methane"}, "contact@example.org")
        sent = parse_qs(urlparse(opened.call_args.args[0].full_url).query)
        self.assertEqual(sent["query"], ["soil & water / methane"])
        self.assertEqual(sent["mailto"], ["contact@example.org"])
        self.assertNotIn("mailto", public_url)
        self.assertNotIn("contact@example.org", public_url)

    def test_missing_metadata_is_not_invented(self):
        result = helper.normalize({"DOI": "10.1234/example", "title": ["A study"]})
        self.assertIsNone(result["abstract"])
        self.assertIsNone(result["publication_date_parts"])
        self.assertIsNone(result["crossref_retrieval_score"])
        self.assertEqual(result["issns"], [])

    def test_markup_unicode_and_paragraph_boundaries(self):
        self.assertEqual(helper.plain("<jats:p>α &amp; β</jats:p><jats:p>CO<sub>2</sub></jats:p>"), "α & β CO2")

    def test_duplicates_dates_and_update_evidence(self):
        item = {"DOI": "10.1234/ABC", "published": {"date-parts": [[2025, 3]]},
                "license": [{"URL": "https://example.org/license"}],
                "update-to": [{"type": "correction", "DOI": "10.1234/other"}]}
        result = helper.result_envelope({"message": {"items": [item, {"DOI": "10.1234/abc"}], "total-results": 2}}, "https://example.org", "search")
        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(result["records"][0]["publication_date_parts"], [2025, 3])
        self.assertEqual(result["records"][0]["update_notices"], item["update-to"])
        self.assertEqual(result["records"][0]["licenses"], item["license"])

    def test_request_filters_and_identifier_validation(self):
        parser = helper.make_parser()
        args = parser.parse_args(["journal", "--issn", "14764687", "--from-date", "2024-01-01"])
        path, params = helper.build_request(args)
        self.assertEqual(path, "/journals/1476-4687/works")
        self.assertIn("from-pub-date:2024-01-01", params["filter"])
        self.assertEqual(params["sort"], "published")
        self.assertEqual(helper.doi_value("https://doi.org/10.1234/a(b)"), "10.1234/a(b)")
        for argv in (["journal", "--issn", "1476-4688"],
                     ["search", "--query", "soil", "--rows", "101"],
                     ["search", "--query", "soil", "--from-date", "2025-02-30"],
                     ["doi", "--doi", "10.1234/x", "--timeout", "nan"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                parser.parse_args(argv)

    def test_rate_limit_retry_is_bounded(self):
        error = HTTPError("https://example.org", 429, "limited", {"Retry-After": "0"}, None)
        with patch.object(helper, "urlopen", side_effect=error) as opened, patch.object(helper.time, "sleep") as slept:
            with self.assertRaises(RuntimeError):
                helper.fetch_json("/works", {})
        self.assertEqual(opened.call_count, 3)
        self.assertEqual(slept.call_count, 2)

    def test_long_retry_delay_is_respected_by_stopping(self):
        error = HTTPError("https://example.org", 429, "limited", {"Retry-After": "90"}, None)
        with patch.object(helper, "urlopen", side_effect=error) as opened, patch.object(helper.time, "sleep") as slept:
            with self.assertRaises(RuntimeError):
                helper.fetch_json("/works", {})
        self.assertEqual(opened.call_count, 1)
        slept.assert_not_called()

    def test_network_error_returns_json_without_private_data(self):
        out = io.StringIO()
        with patch.object(helper, "urlopen", side_effect=URLError("contact@example.org")), contextlib.redirect_stdout(out):
            code = helper.main(["search", "--query", "soil", "--mailto", "contact@example.org"])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.getvalue())["status"], "error")
        self.assertNotIn("contact@example.org", out.getvalue())

    def test_no_results_and_malformed_response(self):
        result = helper.result_envelope({"message": {"items": [], "total-results": 0}}, "https://example.org", "search")
        self.assertEqual(result["returned_count"], 0)
        with self.assertRaises(ValueError):
            helper.result_envelope({"message": {"items": "invalid"}}, "https://example.org", "search")

    def test_successful_cli_emits_traceable_records(self):
        payload = {"status": "ok", "message": {"DOI": "10.1234/example", "type": "journal-article"}}
        out = io.StringIO()
        with patch.object(helper, "fetch_json", return_value=(payload, "https://api.crossref.org/works/10.1234%2Fexample")), contextlib.redirect_stdout(out):
            code = helper.main(["doi", "--doi", "10.1234/example"])
        result = json.loads(out.getvalue())
        self.assertEqual(code, 0)
        self.assertEqual(result["records"][0]["doi"], "10.1234/example")
        self.assertTrue(result["retrieved_at"])
        self.assertEqual(result["provider"], "Crossref")

    def test_permanent_http_error_is_not_retried(self):
        error = HTTPError("https://example.org", 404, "not found", {}, None)
        with patch.object(helper, "urlopen", side_effect=error) as opened, patch.object(helper.time, "sleep") as slept:
            with self.assertRaises(RuntimeError):
                helper.fetch_json("/works/10.1234%2Fmissing", {})
        self.assertEqual(opened.call_count, 1)
        slept.assert_not_called()

    def test_invalid_window_stops_before_network(self):
        with patch.object(helper, "urlopen") as opened, contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
            helper.main(["search", "--query", "soil", "--from-date", "2025-01-01", "--until-date", "2024-01-01"])
        opened.assert_not_called()


if __name__ == "__main__":
    unittest.main()
