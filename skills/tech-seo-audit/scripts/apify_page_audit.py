#!/usr/bin/env python3
"""Run a tightly scoped Apify page-evidence crawl for technical SEO."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from decimal import Decimal, InvalidOperation
from datetime import datetime, timezone


API_ROOT = "https://api.apify.com/v2"
TERMINAL_STATUSES = {"SUCCEEDED", "FAILED", "TIMED-OUT", "ABORTED"}
SENSITIVE_QUERY_NAMES = {
    "access_token", "api_key", "apikey", "auth", "authorization", "code",
    "key", "password", "secret", "session", "session_id", "sig",
    "signature", "token",
}


RAW_PAGE_FUNCTION = r"""async function pageFunction(context) {
  await context.skipLinks();
  const { $, request, response, body, contentType, env } = context;
  const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
  const absolute = (value) => {
    try { return new URL(value, request.loadedUrl || request.url).href; }
    catch (_) { return value || null; }
  };
  const mapElements = (selector, mapper, limit) => $(selector).toArray().slice(0, limit).map((el) => mapper($(el), el));
  const links = mapElements('a[href]', (el) => ({
    href: absolute(el.attr('href')),
    text: clean(el.text()),
    rel: el.attr('rel') || null
  }), 500);
  const images = mapElements('img', (el) => ({
    src: absolute(el.attr('src')),
    alt: el.attr('alt') === undefined ? null : el.attr('alt'),
    width: el.attr('width') || null,
    height: el.attr('height') || null,
    loading: el.attr('loading') || null,
    srcset: el.attr('srcset') || null
  }), 250);
  const headers = {};
  for (const name of ['content-type', 'location', 'x-robots-tag', 'link', 'content-language', 'retry-after', 'last-modified', 'etag', 'cache-control']) {
    if (response && response.headers && response.headers[name] !== undefined) headers[name] = response.headers[name];
  }
  const title = clean($('title').first().text());
  const bodyText = clean($('body').text());
  return {
    sourceMode: 'raw-http',
    fetchedAt: new Date().toISOString(),
    actorRunId: env && env.actorRunId || null,
    requestedUrl: request.url,
    loadedUrl: request.loadedUrl || request.url,
    statusCode: response && response.status || null,
    headers,
    contentType: contentType && contentType.type || null,
    title,
    htmlLang: $('html').attr('lang') || null,
    metaDescription: $('meta[name="description" i]').first().attr('content') || null,
    canonical: absolute($('link[rel="canonical" i]').first().attr('href')),
    robots: mapElements('meta[name="robots" i], meta[name="googlebot" i]', (el) => ({
      name: el.attr('name') || null,
      content: el.attr('content') || null
    }), 20),
    viewport: $('meta[name="viewport" i]').first().attr('content') || null,
    headings: mapElements('h1,h2,h3,h4,h5,h6', (el, node) => ({
      tag: node.name ? node.name.toUpperCase() : null,
      text: clean(el.text())
    }), 250),
    hreflang: mapElements('link[rel="alternate" i][hreflang]', (el) => ({
      hreflang: el.attr('hreflang') || null,
      href: absolute(el.attr('href'))
    }), 100),
    links: { totalExtracted: $('a[href]').length, items: links },
    images: { totalExtracted: $('img').length, items: images },
    jsonLd: mapElements('script[type="application/ld+json" i]', (el) => clean(el.text()).slice(0, 20000), 20),
    bodyTextSnippet: bodyText.slice(0, 12000),
    htmlLength: typeof body === 'string' ? body.length : null,
    challengeIndicators: {
      titleMatch: /just a moment|captcha|access denied|security verification/i.test(title),
      turnstile: $('[name="cf-turnstile-response"]').length > 0,
      bodyMatch: /verify you are human|performing security verification|too many requests/i.test(bodyText.slice(0, 3000))
    }
  };
}"""


RENDERED_PAGE_FUNCTION = r"""async function pageFunction(context) {
  await context.skipLinks();
  const clean = (value) => String(value || '').replace(/\s+/g, ' ').trim();
  const absolute = (value) => {
    try { return new URL(value, window.location.href).href; }
    catch (_) { return value || null; }
  };
  const elements = (selector) => Array.from(document.querySelectorAll(selector));
  const links = elements('a[href]').slice(0, 500).map((el) => ({
    href: el.href || absolute(el.getAttribute('href')),
    text: clean(el.textContent),
    rel: el.getAttribute('rel') || null
  }));
  const images = elements('img').slice(0, 250).map((el) => ({
    src: el.currentSrc || el.src || null,
    alt: el.getAttribute('alt'),
    width: el.getAttribute('width'),
    height: el.getAttribute('height'),
    loading: el.getAttribute('loading'),
    srcset: el.getAttribute('srcset'),
    naturalWidth: el.naturalWidth || null,
    naturalHeight: el.naturalHeight || null
  }));
  const title = clean(document.title);
  const bodyText = clean(document.body && document.body.textContent);
  return {
    sourceMode: 'rendered-browser',
    fetchedAt: new Date().toISOString(),
    requestedUrl: context.request.url,
    loadedUrl: window.location.href,
    title,
    htmlLang: document.documentElement.getAttribute('lang'),
    metaDescription: document.querySelector('meta[name="description" i]')?.getAttribute('content') || null,
    canonical: absolute(document.querySelector('link[rel="canonical" i]')?.getAttribute('href')),
    robots: elements('meta[name="robots" i], meta[name="googlebot" i]').slice(0, 20).map((el) => ({
      name: el.getAttribute('name'),
      content: el.getAttribute('content')
    })),
    viewport: document.querySelector('meta[name="viewport" i]')?.getAttribute('content') || null,
    headings: elements('h1,h2,h3,h4,h5,h6').slice(0, 250).map((el) => ({
      tag: el.tagName,
      text: clean(el.textContent),
      hidden: !(el.offsetWidth || el.offsetHeight || el.getClientRects().length)
    })),
    hreflang: elements('link[rel="alternate" i][hreflang]').slice(0, 100).map((el) => ({
      hreflang: el.getAttribute('hreflang'),
      href: el.href || absolute(el.getAttribute('href'))
    })),
    links: { totalExtracted: elements('a[href]').length, items: links },
    images: { totalExtracted: elements('img').length, items: images },
    jsonLd: elements('script[type="application/ld+json" i]').slice(0, 20).map((el) => clean(el.textContent).slice(0, 20000)),
    bodyTextSnippet: bodyText.slice(0, 12000),
    htmlLength: document.documentElement.outerHTML.length,
    challengeIndicators: {
      titleMatch: /just a moment|captcha|access denied|security verification/i.test(title),
      turnstile: elements('[name="cf-turnstile-response"]').length > 0,
      bodyMatch: /verify you are human|performing security verification|too many requests/i.test(bodyText.slice(0, 3000))
    }
  };
}"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview or execute a controlled Apify technical-SEO crawl."
    )
    parser.add_argument("urls", nargs="+", help="One to ten explicit HTTP(S) URLs")
    parser.add_argument(
        "--mode", choices=("raw", "rendered"), default="raw",
        help="Raw HTTP with Cheerio (default) or browser-rendered DOM",
    )
    parser.add_argument("--execute", action="store_true", help="Actually start the Actor")
    parser.add_argument(
        "--cost-authorized", action="store_true",
        help="Confirm that the user explicitly authorized possible Apify charges",
    )
    parser.add_argument(
        "--max-total-charge-usd",
        help="Required positive per-run cost ceiling when --execute is used",
    )
    parser.add_argument(
        "--actor-build", help="Optional pinned Actor build tag or number",
    )
    parser.add_argument(
        "--poll-timeout-secs", type=int, default=600,
        help="Maximum local wait for a terminal run status (default: 600)",
    )
    return parser.parse_args()


def normalize_urls(values: list[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        parsed = urllib.parse.urlsplit(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError(f"Invalid HTTP(S) URL: {value}")
        query_names = {name.lower() for name, _ in urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)}
        sensitive = sorted(query_names & SENSITIVE_QUERY_NAMES)
        if sensitive:
            raise ValueError(
                "Refusing to send a URL with potentially sensitive query parameter(s) "
                f"to Apify: {', '.join(sensitive)}"
            )
        normalized = urllib.parse.urlunsplit(parsed)
        if normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    if not 1 <= len(result) <= 10:
        raise ValueError("Provide between 1 and 10 unique URLs")
    return result


def parse_cost(value: str | None) -> Decimal | None:
    if value is None:
        return None
    try:
        cost = Decimal(value)
    except InvalidOperation as exc:
        raise ValueError("--max-total-charge-usd must be a number") from exc
    if not cost.is_finite() or cost <= 0:
        raise ValueError("--max-total-charge-usd must be positive")
    return cost


def actor_config(mode: str, urls: list[str]) -> tuple[str, dict]:
    common = {
        "startUrls": [{"url": url} for url in urls],
        "keepUrlFragments": True,
        "respectRobotsTxtFile": True,
        "linkSelector": "",
        "globs": [],
        "pseudoUrls": [],
        "excludes": [],
        "proxyConfiguration": {"useApifyProxy": True},
        "proxyRotation": "UNTIL_FAILURE",
        "maxRequestRetries": 0,
        "maxPagesPerCrawl": len(urls),
        "maxResultsPerCrawl": len(urls),
        "maxConcurrency": 1,
        "pageLoadTimeoutSecs": 60,
        "pageFunctionTimeoutSecs": 30,
        "debugLog": False,
    }
    if mode == "raw":
        return "apify~cheerio-scraper", {**common, "pageFunction": RAW_PAGE_FUNCTION}
    return "apify~web-scraper", {
        **common,
        "pageFunction": RENDERED_PAGE_FUNCTION,
        "runMode": "PRODUCTION",
        "injectJQuery": False,
        "useChrome": False,
        "headless": True,
        "ignoreSslErrors": False,
        "ignoreCorsAndCsp": False,
        "downloadMedia": False,
        "downloadCss": True,
        "closeCookieModals": False,
        "maxScrollHeightPixels": 0,
        "browserLog": False,
        "waitUntil": ["domcontentloaded", "networkidle2"],
    }


def request_json(
    method: str,
    url: str,
    token: str,
    payload: dict | None = None,
    timeout: int = 75,
):
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "User-Agent": "tech-seo-audit-apify-helper/1.0",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read(4000).decode("utf-8", errors="replace")
        raise RuntimeError(f"Apify API HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Apify API connection failed: {exc.reason}") from exc


def compact_run(run: dict) -> dict:
    keys = (
        "id", "actId", "actorTaskId", "buildId", "buildNumber",
        "defaultDatasetId", "startedAt", "finishedAt", "status",
        "statusMessage", "exitCode", "options", "stats", "pricingInfo",
        "chargedEventCounts", "usage", "usageTotalUsd",
    )
    return {key: run.get(key) for key in keys if key in run}


def sha256_json(value: dict) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def execute(actor_id: str, payload: dict, token: str, cost: Decimal, args: argparse.Namespace) -> dict:
    query = {
        "waitForFinish": 60,
        "timeout": min(600, max(60, len(args.urls) * 60)),
        "maxItems": len(args.urls),
        "maxTotalChargeUsd": format(cost, "f"),
    }
    if args.actor_build:
        query["build"] = args.actor_build
    run_url = f"{API_ROOT}/actors/{actor_id}/runs?{urllib.parse.urlencode(query)}"
    started = request_json("POST", run_url, token, payload)
    run = started.get("data", started)
    run_id = run.get("id")
    if not run_id:
        raise RuntimeError("Apify response did not include a run ID")

    deadline = time.monotonic() + args.poll_timeout_secs
    while run.get("status") not in TERMINAL_STATUSES and time.monotonic() < deadline:
        poll_url = f"{API_ROOT}/actor-runs/{urllib.parse.quote(run_id)}?waitForFinish=60"
        polled = request_json("GET", poll_url, token)
        run = polled.get("data", polled)

    if run.get("status") not in TERMINAL_STATUSES:
        return {
            "apifyRun": compact_run(run),
            "items": [],
            "error": "Local polling deadline reached; the Actor may still be running. Do not start a duplicate run automatically.",
        }

    dataset_id = run.get("defaultDatasetId")
    items = []
    if dataset_id:
        item_query = urllib.parse.urlencode({"format": "json", "clean": "false", "limit": len(args.urls)})
        item_url = f"{API_ROOT}/datasets/{urllib.parse.quote(dataset_id)}/items?{item_query}"
        items = request_json("GET", item_url, token)

    return {"apifyRun": compact_run(run), "items": items}


def main() -> int:
    args = parse_args()
    try:
        urls = normalize_urls(args.urls)
        cost = parse_cost(args.max_total_charge_usd)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    actor_id, payload = actor_config(args.mode, urls)
    args.urls = urls
    plan = {
        "execute": args.execute,
        "mode": args.mode,
        "actorId": actor_id,
        "urlCount": len(urls),
        "urls": urls,
        "costAuthorized": args.cost_authorized,
        "maxTotalChargeUsd": None if cost is None else format(cost, "f"),
        "tokenSource": "APIFY_API_TOKEN environment variable",
        "inputSha256": sha256_json(payload),
        "pageFunctionSha256": hashlib.sha256(payload["pageFunction"].encode("utf-8")).hexdigest(),
        "input": payload,
    }
    if not args.execute:
        print(json.dumps(plan, ensure_ascii=False, indent=2))
        return 0

    if not args.cost_authorized:
        print("error: --cost-authorized is required for --execute", file=sys.stderr)
        return 2
    if cost is None:
        print("error: --max-total-charge-usd is required for --execute", file=sys.stderr)
        return 2
    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        print("error: APIFY_API_TOKEN is not configured", file=sys.stderr)
        return 2
    if args.poll_timeout_secs < 1:
        print("error: --poll-timeout-secs must be positive", file=sys.stderr)
        return 2

    try:
        result = execute(actor_id, payload, token, cost, args)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    output = {
        "collection": {
            "mode": args.mode,
            "actorId": actor_id,
            "actorBuild": args.actor_build or "default",
            "requestedUrls": urls,
            "maxTotalChargeUsd": format(cost, "f"),
            "inputSha256": sha256_json(payload),
            "pageFunctionSha256": hashlib.sha256(payload["pageFunction"].encode("utf-8")).hexdigest(),
            "retrievedAt": datetime.now(timezone.utc).isoformat(),
            "datasetItemCount": len(result.get("items", [])),
        },
        **result,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
