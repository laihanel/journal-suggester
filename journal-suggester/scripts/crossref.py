#!/usr/bin/env python3
"""Retrieve public Crossref evidence; no dependencies, credentials, or fit scoring."""

import argparse
from datetime import date, datetime, timezone
from html.parser import HTMLParser
import json
import math
from pathlib import Path
import re
import ssl
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


BASE = "https://api.crossref.org"
LIMITATIONS = [
    "Publisher-deposited metadata may be incomplete; missing abstracts remain null.",
    "Retrieval relevance is not journal fit, acceptance probability, or quality.",
    "Records do not verify current scope, indexing, JIF, APCs, or agreement coverage.",
    "License and update metadata require interpretation; absence is inconclusive.",
]


class PlainText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag.split(":")[-1] in {"p", "br", "div", "title", "sec"}:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        self.handle_starttag(tag, [])

    def handle_data(self, data):
        self.parts.append(data)


def plain(value):
    if value is None:
        return None
    parser = PlainText()
    parser.feed(str(value))
    parser.close()
    return " ".join("".join(parser.parts).split()) or None


def first(values):
    return values[0] if isinstance(values, list) and values else None


def doi_value(value):
    value = re.sub(r"^(?:https?://(?:dx\.)?doi\.org/|doi:\s*)", "", value.strip(), flags=re.I)
    if not re.fullmatch(r"10\.\d{4,9}/\S+", value, flags=re.I):
        raise argparse.ArgumentTypeError("Expected a DOI or a doi.org URL")
    return value


def issn_value(value):
    compact = value.replace("-", "").upper().strip()
    if not re.fullmatch(r"\d{7}[\dX]", compact):
        raise argparse.ArgumentTypeError("Expected an ISSN such as 1476-4687")
    check = 10 if compact[-1] == "X" else int(compact[-1])
    if (sum(int(c) * weight for c, weight in zip(compact[:7], range(8, 1, -1))) + check) % 11:
        raise argparse.ArgumentTypeError("ISSN checksum is invalid")
    return compact[:4] + "-" + compact[4:]


def date_value(value):
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise argparse.ArgumentTypeError("Dates must use YYYY-MM-DD")
    try:
        return date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Invalid calendar date") from exc


def rows_value(value):
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Rows must be an integer") from exc
    if not 1 <= number <= 100:
        raise argparse.ArgumentTypeError("Rows must be between 1 and 100")
    return number


def timeout_value(value):
    try:
        number = float(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("Timeout must be a number") from exc
    if not math.isfinite(number) or not 0 < number <= 60:
        raise argparse.ArgumentTypeError("Timeout must be greater than 0 and at most 60 seconds")
    return number


def build_request(args):
    if args.command == "doi":
        return "/works/" + quote(args.doi, safe=""), {}
    filters = ["type:journal-article"]
    for field in ("from", "until"):
        value = getattr(args, field + "_date")
        if value:
            filters.append(field + "-pub-date:" + value)
    params = {"rows": args.rows, "filter": ",".join(filters)}
    if args.command == "search":
        params["query"] = args.query.strip()
        params["sort"] = "relevance"
        path = "/works"
    else:
        params.update(sort="published", order="desc")
        path = "/journals/" + quote(args.issn, safe="") + "/works"
    return path, params


def tls_context():
    context = ssl.create_default_context()
    # Some framework Python installations omit a CA bundle. Use the OS bundle
    # only when no roots were loaded; never disable certificate verification.
    if not context.get_ca_certs():
        for bundle in ("/etc/ssl/cert.pem", "/etc/pki/tls/certs/ca-bundle.crt"):
            if Path(bundle).is_file():
                context.load_verify_locations(cafile=bundle)
                break
    return context


def fetch_json(path, params, mailto=None, timeout=25):
    public_url = BASE + path + ("?" + urlencode(params) if params else "")
    sent_params = dict(params)
    if mailto:
        sent_params["mailto"] = mailto
    url = BASE + path + ("?" + urlencode(sent_params) if sent_params else "")
    request = Request(url, headers={
        "User-Agent": "journal-suggester/1.0 (public scholarly metadata research)",
        "Accept": "application/json",
    })
    context = tls_context()
    for attempt in range(3):
        try:
            with urlopen(request, timeout=timeout, context=context) as response:
                payload = json.load(response)
            if not isinstance(payload, dict) or payload.get("status") != "ok":
                raise ValueError("Crossref returned an unexpected response envelope")
            return payload, public_url
        except HTTPError as exc:
            code = exc.code
            retry_after = exc.headers.get("Retry-After") if exc.headers else None
            exc.close()
            if code not in {429, 502, 503, 504} or attempt == 2:
                raise RuntimeError("Crossref HTTP " + str(code)) from None
            delay = 2 ** attempt
            if retry_after:
                try:
                    delay = float(retry_after)
                except ValueError:
                    raise RuntimeError("Crossref requested a deferred retry; try again later") from None
                if not math.isfinite(delay) or not 0 <= delay <= 10:
                    raise RuntimeError("Crossref requested a longer retry delay; try again later")
            time.sleep(delay)
        except URLError as exc:
            if isinstance(exc.reason, ssl.SSLCertVerificationError):
                raise RuntimeError("Crossref TLS certificate verification failed; configure trusted certificates for this Python installation") from None
            raise RuntimeError("Crossref network request failed; check connectivity and access permissions") from None
        except (TimeoutError, OSError):
            raise RuntimeError("Crossref connection failed or timed out") from None
    raise RuntimeError("Crossref request did not complete")


def normalize(item):
    doi = item.get("DOI")
    published = item.get("published") or item.get("published-online") or item.get("published-print") or {}
    return {
        "doi": doi,
        "doi_url": "https://doi.org/" + quote(doi, safe="/") if doi else None,
        "title": plain(first(item.get("title"))),
        "journal_title": plain(first(item.get("container-title"))),
        "issns": item.get("ISSN", []),
        "publisher": item.get("publisher"),
        "work_type": item.get("type"),
        "publication_date_parts": first(published.get("date-parts")),
        "abstract": plain(item.get("abstract")),
        "crossref_retrieval_score": item.get("score"),
        "crossref_cited_by_count": item.get("is-referenced-by-count"),
        "reference_dois": [r["DOI"] for r in item.get("reference", []) if r.get("DOI")],
        "licenses": item.get("license", []),
        "update_notices": item.get("update-to", []),
        "relations": item.get("relation", {}),
    }


def result_envelope(payload, url, command):
    message = payload.get("message")
    if not isinstance(message, dict):
        raise ValueError("Crossref response is missing its metadata object")
    items = [message] if command == "doi" else message.get("items")
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise ValueError("Crossref response contains invalid work records")
    records, seen = [], set()
    for item in items:
        doi = item.get("DOI")
        key = doi.lower() if doi else None
        if key and key in seen:
            continue
        if key:
            seen.add(key)
        records.append(normalize(item))
    return {
        "status": "ok", "provider": "Crossref", "schema_version": 1,
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "request_url": url,
        "total_results": 1 if command == "doi" else message.get("total-results"),
        "returned_count": len(records),
        "limitations": LIMITATIONS,
        "records": records,
    }


def make_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("search", "journal", "doi"):
        sub = commands.add_parser(name)
        sub.add_argument("--mailto", help="Optional authorized contact sent to Crossref")
        sub.add_argument("--timeout", type=timeout_value, default=25)
        if name == "doi":
            sub.add_argument("--doi", required=True, type=doi_value)
            continue
        if name == "search":
            sub.add_argument("--query", required=True, help="Generic topical search terms")
        else:
            sub.add_argument("--issn", required=True, type=issn_value)
        sub.add_argument("--from-date", type=date_value)
        sub.add_argument("--until-date", type=date_value)
        sub.add_argument("--rows", type=rows_value, default=20)
    return parser


def main(argv=None):
    parser = make_parser()
    args = parser.parse_args(argv)
    if args.command == "search" and not args.query.strip():
        parser.error("Search query cannot be empty")
    if args.command != "doi" and args.from_date and args.until_date and args.from_date > args.until_date:
        parser.error("--from-date cannot be later than --until-date")
    try:
        path, params = build_request(args)
        payload, url = fetch_json(path, params, args.mailto, args.timeout)
        result = result_envelope(payload, url, args.command)
    except RuntimeError as exc:
        # These messages are locally defined; no remote response bodies or URLs.
        print(json.dumps({"status": "error", "provider": "Crossref", "error": str(exc)}))
        return 1
    except (ValueError, TypeError, KeyError, AttributeError):
        # Do not echo URLs, query contents, contact details, or server response bodies.
        print(json.dumps({"status": "error", "provider": "Crossref",
                          "error": "Retrieval failed or response was invalid; check network access, identifiers, and API availability."}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
