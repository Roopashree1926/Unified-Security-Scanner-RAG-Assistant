import subprocess


def run_nmap(target: str):

    findings = []

    try:

        command = [
            "nmap",
            "-sV",
            target
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:

            return [{
                "scanner": "Nmap",
                "target": target,
                "title": "Nmap Error",
                "severity": "High",
                "description": result.stderr.strip() or "Nmap scan failed.",
                "port": None
            }]

        output = result.stdout

        for line in output.splitlines():

            if "/tcp" not in line:
                continue

            parts = line.split()

            if len(parts) < 3:
                continue

            try:
                port = int(parts[0].split("/")[0])
            except ValueError:
                port = None

            state = parts[1]
            service = parts[2]

            version = ""

            if len(parts) > 3:
                version = " ".join(parts[3:])

            findings.append({
                "scanner": "Nmap",
                "target": target,
                "title": f"{service} Service Detected",
                "severity": "Info",
                "description": (
                    f"State: {state}. "
                    f"Service: {service}. "
                    f"Version: {version or 'Unknown'}."
                ),
                "port": port,
                "evidence": line.strip()
            })

        if not findings:

            findings.append({
                "scanner": "Nmap",
                "target": target,
                "title": "No Open TCP Ports Detected",
                "severity": "Info",
                "description": (
                    "Nmap completed successfully but did not "
                    "identify open TCP ports."
                ),
                "port": None
            })

    except FileNotFoundError:

        findings.append({
            "scanner": "Nmap",
            "target": target,
            "title": "Nmap Not Installed",
            "severity": "High",
            "description": (
                "Nmap executable was not found. "
                "Install Nmap and make sure it is available "
                "in the system PATH."
            ),
            "port": None
        })

    except subprocess.TimeoutExpired:

        findings.append({
            "scanner": "Nmap",
            "target": target,
            "title": "Nmap Scan Timeout",
            "severity": "High",
            "description": (
                "The Nmap scan exceeded the maximum "
                "execution time of 300 seconds."
            ),
            "port": None
        })

    except Exception as e:

        findings.append({
            "scanner": "Nmap",
            "target": target,
            "title": "Nmap Error",
            "severity": "High",
            "description": str(e),
            "port": None
        })

    return findings