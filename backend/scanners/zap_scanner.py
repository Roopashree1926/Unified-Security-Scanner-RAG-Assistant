import os
import time
import requests
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

ZAP_API_URL = os.getenv(
    "ZAP_API_URL",
    "http://127.0.0.1:8080"
).rstrip("/")

ZAP_API_KEY = os.getenv("ZAP_API_KEY", "unifiedscanner123")

SESSION = requests.Session()
SESSION.trust_env = False


def zap_request(endpoint, params=None, timeout=30):
    """Send a request to the local ZAP API."""
    params = params or {}

    if ZAP_API_KEY:
        params["apikey"] = ZAP_API_KEY

    response = SESSION.get(
        f"{ZAP_API_URL}{endpoint}",
        params=params,
        timeout=timeout
    )
    response.raise_for_status()
    data = response.json()

    if "code" in data and str(data.get("code", "")).startswith("4"):
        raise RuntimeError(data.get("message", "ZAP API error"))

    return data


def run_zap(target: str):
    """Run ZAP passive scanning and return normalized findings."""
    findings = []
    target = target.strip()

    parsed = urlparse(
        target if "://" in target else f"http://{target}"
    )

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return [{
            "scanner": "ZAP",
            "target": target,
            "title": "Invalid Target",
            "severity": "Info",
            "description": "Enter a valid HTTP or HTTPS URL.",
            "port": None
        }]

    target = parsed.geturl()

    try:
        # Confirm ZAP API is available.
        zap_request("/JSON/core/view/version/")

        # Access the target through ZAP so it enters the site tree.
        zap_request(
            "/JSON/core/action/accessUrl/",
            {"url": target, "followRedirects": "true"}
        )

        # Wait for passive scanning to process the traffic.
        deadline = time.monotonic() + 60

        while time.monotonic() < deadline:
            status = zap_request(
                "/JSON/pscan/view/recordsToScan/"
            )
            remaining = int(status.get("recordsToScan", 0))

            if remaining <= 0:
                break

            time.sleep(2)

        # Retrieve alerts associated with this target.
        alerts = zap_request(
            "/JSON/alert/view/alerts/",
            {"baseurl": target, "start": 0, "count": 500}
        ).get("alerts", [])

        for alert in alerts:
            risk = str(alert.get("risk", "Informational"))
            risk_lower = risk.lower()

            severity = {
                "high": "High",
                "medium": "Medium",
                "low": "Low",
                "informational": "Info"
            }.get(risk_lower, "Info")

            matched_url = alert.get("url", target)
            port = urlparse(matched_url).port

            if port is None:
                port = 443 if urlparse(matched_url).scheme == "https" else 80

            findings.append({
                "scanner": "ZAP",
                "target": target,
                "title": alert.get("alert", "ZAP Alert"),
                "severity": severity,
                "description": alert.get(
                    "description",
                    "ZAP reported a potential security issue."
                ),
                "port": port,
                "evidence": alert.get("evidence", ""),
                "url": matched_url,
                "solution": alert.get("solution", ""),
                "reference": alert.get("reference", "")
            })

        if not findings:
            findings.append({
                "scanner": "ZAP",
                "target": target,
                "title": "No Passive Scan Alerts Found",
                "severity": "Info",
                "description": (
                    "ZAP accessed the target and found no passive-scan "
                    "alerts in the returned results. This does not prove "
                    "the target is free of vulnerabilities."
                ),
                "port": None
            })

    except requests.RequestException as exc:
        findings.append({
            "scanner": "ZAP",
            "target": target,
            "title": "ZAP Connection Error",
            "severity": "Info",
            "description": (
                f"Could not communicate with ZAP at {ZAP_API_URL}: {exc}"
            ),
            "port": None
        })

    except Exception as exc:
        findings.append({
            "scanner": "ZAP",
            "target": target,
            "title": "ZAP Scan Error",
            "severity": "Info",
            "description": str(exc),
            "port": None
        })

    return findings
