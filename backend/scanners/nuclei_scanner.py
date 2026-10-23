
import subprocess
import json
import shutil
from urllib.parse import urlparse


def run_nuclei(target: str):
    findings = []
    target = target.strip()

    if not target:
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "Invalid Target",
            "severity": "Info",
            "description": "Please provide a valid target.",
            "port": None,
        }]

    # Check whether Nuclei is installed and accessible.
    nuclei_path = shutil.which("nuclei")

    if not nuclei_path:
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "Nuclei Not Installed",
            "severity": "Info",
            "description": (
                "Nuclei was not found in PATH. "
                "Install ProjectDiscovery Nuclei and verify "
                "it works by running: nuclei -version"
            ),
            "port": None,
        }]

    # Normalize a hostname into an HTTP URL.
    if "://" not in target:
        target = "https://" + target

    parsed_target = urlparse(target)

    if parsed_target.scheme not in ("http", "https") or not parsed_target.hostname:
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "Invalid Target",
            "severity": "Info",
            "description": (
                "Provide a valid HTTP/HTTPS URL or hostname."
            ),
            "port": None,
        }]

    command = [
        nuclei_path,
        "-u", target,
        "-jsonl",
        "-silent",
        "-duc",
        "-ni",
        "-pt", "http",
        "-s", "info,low,medium,high,critical",
        "-timeout", "10",
        "-retries", "1",
        "-rl", "10",
        "-c", "5",
    ]

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300,
            errors="replace",
        )

        # Parse JSON Lines output from Nuclei.
        for line in result.stdout.splitlines():
            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            info = data.get("info") or {}

            title = (
                info.get("name")
                or data.get("template-id")
                or "Nuclei Finding"
            )

            severity = str(
                info.get("severity", "info")
            ).capitalize()

            description = (
                info.get("description")
                or "Nuclei detected a potential security issue."
            )

            matched_at = (
                data.get("matched-at")
                or data.get("host")
                or target
            )

            port = None

            try:
                parsed = urlparse(matched_at)

                if parsed.port:
                    port = parsed.port
                elif parsed.scheme == "https":
                    port = 443
                elif parsed.scheme == "http":
                    port = 80
            except (ValueError, TypeError):
                pass

            findings.append({
                "scanner": "Nuclei",
                "target": target,
                "title": title,
                "severity": severity,
                "description": description,
                "port": port,
                "evidence": matched_at,
                "template_id": data.get("template-id"),
            })

        # Do not report a successful empty scan if the process failed.
        if result.returncode != 0 and not findings:
            error_message = (
                result.stderr.strip()
                or result.stdout.strip()
                or f"Nuclei exited with code {result.returncode}."
            )

            return [{
                "scanner": "Nuclei",
                "target": target,
                "title": "Nuclei Execution Error",
                "severity": "Info",
                "description": error_message[:2000],
                "port": None,
            }]

        if findings:
            return findings

        # A zero exit code and no findings indicates an empty result.
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "No Vulnerabilities Detected",
            "severity": "Info",
            "description": (
                "Nuclei completed without reporting matching "
                "HTTP template findings. This does not prove "
                "that the target is free of vulnerabilities."
            ),
            "port": None,
        }]

    except subprocess.TimeoutExpired:
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "Nuclei Scan Timeout",
            "severity": "Info",
            "description": (
                "Nuclei exceeded the 300-second execution limit. "
                "Check target reachability, template availability, "
                "network connectivity, and the backend terminal."
            ),
            "port": None,
        }]

    except Exception as exc:
        return [{
            "scanner": "Nuclei",
            "target": target,
            "title": "Nuclei Error",
            "severity": "Info",
            "description": str(exc),
            "port": None,
        }]
