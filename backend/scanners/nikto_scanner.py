
import os
import re
import shutil
import subprocess
from urllib.parse import urlparse


NIKTO_SCRIPT = r"C:\Tools\nikto\program\nikto.pl"
PERL_PATH = shutil.which("perl") or "perl"


def run_nikto(target: str):
    """Run Nikto and return findings in the project's common format."""

    target = target.strip()
    parsed = urlparse(
        target if "://" in target else f"http://{target}"
    )

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        return [{
            "scanner": "Nikto",
            "target": target,
            "title": "Invalid Target",
            "severity": "Info",
            "description": "Enter a valid hostname or HTTP/HTTPS URL.",
            "port": None
        }]

    host = parsed.hostname
    port = parsed.port or (443 if parsed.scheme == "https" else 80)

    if not os.path.isfile(NIKTO_SCRIPT):
        return [{
            "scanner": "Nikto",
            "target": target,
            "title": "Nikto Installation Not Found",
            "severity": "Info",
            "description": f"Nikto script not found at {NIKTO_SCRIPT}",
            "port": port
        }]

    command = [
        PERL_PATH,
        NIKTO_SCRIPT,
        "-host", host,
        "-port", str(port),
        "-nointeractive",
        "-timeout", "10",
        "-maxtime", "60s"
    ]

    if parsed.scheme == "https":
        command.append("-ssl")
    else:
        command.append("-nossl")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=75,
            errors="replace",
            cwd=os.path.dirname(NIKTO_SCRIPT)
        )

        output = (result.stdout or "") + "\n" + (result.stderr or "")
        findings = []

        for line in output.splitlines():
            line = line.strip()

            if not line.startswith("+"):
                continue

            message = line[1:].strip()

            if not message or message.startswith((
                "Target IP:",
                "Target Hostname:",
                "Target Port:",
                "Platform:",
                "Start Time:",
                "End Time:",
                "Server:",
                "Scan terminated:",
                "1 host(s) tested",
                "No CGI Directories found"
            )):
                continue

            if "ERROR:" in message.upper() and "MAXIMUM EXECUTION TIME" in message.upper():
                continue

            if "Allowed HTTP Methods:" in message:
                title = "HTTP Methods"
                severity = "Info"
            elif "missing:" in message.lower():
                title = message.split(":", 1)[-1].strip()
                severity = "Low"
            elif re.search(r"\b(OSVDB|CVE-\d{4}-\d+|vulnerab|exploit)\b",
                           message, re.IGNORECASE):
                title = message
                severity = "Medium"
            else:
                title = message
                severity = "Info"

            findings.append({
                "scanner": "Nikto",
                "target": target,
                "title": title,
                "severity": severity,
                "description": message,
                "port": port
            })

        if result.returncode != 0 and not findings:
            detail = output.strip() or "Nikto exited without diagnostic output."
            return [{
                "scanner": "Nikto",
                "target": target,
                "title": "Nikto Scan Failed",
                "severity": "Info",
                "description": detail[-3000:],
                "port": port
            }]

        if not findings:
            findings.append({
                "scanner": "Nikto",
                "target": target,
                "title": "No Findings Returned",
                "severity": "Info",
                "description": (
                    "Nikto returned no reportable findings. Check the scan "
                    "output and duration; this does not prove the target "
                    "is free of vulnerabilities."
                ),
                "port": port
            })

        return findings

    except subprocess.TimeoutExpired:
        return [{
            "scanner": "Nikto",
            "target": target,
            "title": "Nikto Scan Timed Out",
            "severity": "Info",
            "description": "Nikto did not finish within the 75-second limit.",
            "port": port
        }]

    except Exception as exc:
        return [{
            "scanner": "Nikto",
            "target": target,
            "title": "Nikto Scan Error",
            "severity": "Info",
            "description": str(exc),
            "port": port
        }]
