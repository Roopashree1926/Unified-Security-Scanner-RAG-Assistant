from scanners.nmap_scanner import run_nmap
from scanners.nuclei_scanner import run_nuclei
from scanners.zap_scanner import run_zap
from scanners.nikto_scanner import run_nikto


def run_scan(scanner: str, target: str):
    scanner = scanner.strip().lower()

    if scanner == "nmap":
        return run_nmap(target)
    elif scanner == "nuclei":
        return run_nuclei(target)
    elif scanner in ("zap", "owasp zap"):
        return run_zap(target)
    elif scanner == "nikto":
        return run_nikto(target)

    raise ValueError(f"Unsupported scanner: {scanner}")
