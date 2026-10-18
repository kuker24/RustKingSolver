#!/usr/bin/env python3
"""Noise-profile engine ("senyap") — request hygiene for the whole pipeline.

Three profiles control delay, jitter, user-agent rotation, logging level,
and verbosity:

  QUIET     delay 2.0s +- 1.0 jitter, fixed UA, no aggressive checks,
            WARNING logs, per-request prints suppressed
  MODERATE  delay 0.5s +- 0.25, rotating UA pool, all checks, INFO (default)
  LOUD      no artificial delay, full parallelism, DEBUG logs

Wraps the requests path; falls back to a urllib-based session shim when
requests is absent (shim keeps the .get/.post call shape engines expect).
"""
import logging
import os
import random
import time
import urllib.error
import urllib.request

try:
    import requests as _requests
    _HAVE_REQUESTS = True
except ImportError:
    _HAVE_REQUESTS = False

# Realistic user-agent pool (10+ entries, modern browser fingerprints).
AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.6 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:132.0) Gecko/20100101 Firefox/132.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 OPR/116.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
]

FIXED_QUIET_AGENT = AGENTS[0]


class Profile:
    """One of QUIET / MODERATE / LOUD. Accepts construction from string."""

    QUIET = "quiet"
    MODERATE = "moderate"
    LOUD = "loud"

    # name -> (delay, jitter, rotate_ua, allows_aggressive, log_level, verbose)
    _TABLE = {
        QUIET:    (2.0, 1.0,  False, False, logging.WARNING, False),
        MODERATE: (0.5, 0.25, True,  True,  logging.INFO,    True),
        LOUD:     (0.0, 0.0,  True,  True,  logging.DEBUG,   True),
    }

    def __init__(self, name: str = MODERATE):
        name = (name or self.MODERATE).strip().lower()
        if name.startswith("--"):
            name = name.lstrip("-")
        if name not in self._TABLE:
            raise ValueError(f"Unknown noise profile: {name!r} (expected quiet|moderate|loud)")
        self.name = name
        (self.delay, self.jitter, self.rotate_ua,
         self.allows_aggressive, self.log_level, self.verbose) = self._TABLE[name]

    @property
    def parallel(self) -> bool:
        return self.name == self.LOUD

    def __repr__(self):
        return f"Profile({self.name}, delay={self.delay}+-{self.jitter})"


DEFAULT = Profile(Profile.MODERATE)


def apply(profile: Profile) -> Profile:
    """Apply profile to process-wide logging and verbosity flag."""
    if not isinstance(profile, Profile):
        profile = Profile(profile)
    logging.getLogger().setLevel(profile.log_level)
    os.environ["AXIOM_VERBOSE"] = "1" if profile.verbose else "0"
    return profile


def sleep_jitter(profile: Profile) -> None:
    """Wait per the profile's delay + jitter before the next request."""
    if profile.delay <= 0:
        return
    wait = max(0.0, profile.delay + random.uniform(-profile.jitter, profile.jitter))
    if wait > 0:
        time.sleep(wait)


def next_ua(profile: Profile) -> str:
    """Return the user-agent for this request (fixed for QUIET, rotating else)."""
    if not profile.rotate_ua:
        return FIXED_QUIET_AGENT
    return random.choice(AGENTS)


def http_session(profile: Profile, proxy: str = None, timeout: int = 10):
    """Build a requests.Session (or urllib shim) configured for the profile."""
    if not isinstance(profile, Profile):
        profile = Profile(profile)
    if _HAVE_REQUESTS:
        session = _requests.Session()
        session.verify = False
        session.headers["User-Agent"] = next_ua(profile)
        if proxy:
            session.proxies = {"http": proxy, "https": proxy}
        return session
    return UrllibSession(proxy=proxy, timeout=timeout)


def throttled(session, url: str, method: str = "GET", profile: Profile = None, **kwargs):
    """Sleep per profile, rotate UA, then send the request.

    Works with a requests.Session or the UrllibSession shim. Extra kwargs
    (headers, data, timeout, verify, allow_redirects) pass through.
    """
    if not isinstance(profile, Profile):
        profile = profile or DEFAULT
        if not isinstance(profile, Profile):
            profile = Profile(profile)
    sleep_jitter(profile)
    headers = dict(kwargs.pop("headers", None) or {})
    headers.setdefault("User-Agent", next_ua(profile))
    kwargs["headers"] = headers
    kwargs.setdefault("timeout", 10)
    if method == "GET":
        return session.get(url, **kwargs)
    return session.post(url, **kwargs)


class UrllibSession:
    """Minimal .get/.post session over urllib for environments without requests."""

    def __init__(self, proxy: str = None, timeout: int = 10):
        self.timeout = timeout
        self.verify = False
        if proxy:
            handler = urllib.request.ProxyHandler({"http": proxy, "https": proxy})
            self._opener = urllib.request.build_opener(handler)
        else:
            self._opener = urllib.request.build_opener()

    def _request(self, url, method="GET", **kwargs):
        req = urllib.request.Request(url, method=method)
        for key, value in (kwargs.get("headers") or {}).items():
            req.add_header(key, value)
        data = kwargs.get("data")
        if data is not None and method != "GET":
            if isinstance(data, str):
                data = data.encode()
            req.data = data
        try:
            resp = self._opener.open(req, timeout=kwargs.get("timeout", self.timeout))
            body = resp.read().decode("utf-8", errors="replace")
            return UrllibResponse(resp.getcode(), body, dict(resp.headers))
        except urllib.error.HTTPError as err:
            try:
                body = err.read().decode("utf-8", errors="replace")
            except Exception:
                body = ""
            return UrllibResponse(err.code, body, dict(err.headers or {}))
        except Exception as err:
            return UrllibResponse(0, str(err), {})

    def get(self, url, **kwargs):
        return self._request(url, method="GET", **kwargs)

    def post(self, url, **kwargs):
        return self._request(url, method="POST", **kwargs)


class UrllibResponse:
    """Response object matching the subset of the requests API engines use."""

    def __init__(self, status_code: int, text: str, headers: dict):
        self.status_code = status_code
        self.text = text
        self.headers = headers
        self.cookies = {}

    def __repr__(self):
        return f"<UrllibResponse {self.status_code} len={len(self.text)}>"
