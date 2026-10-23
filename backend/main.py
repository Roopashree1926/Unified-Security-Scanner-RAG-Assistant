
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
from datetime import datetime, timezone
import threading

from scanners.nmap_scanner import run_nmap
from scanners.nuclei_scanner import run_nuclei
from scanners.zap_scanner import run_zap
from scanners.nikto_scanner import run_nikto

from routers.ai import router as ai_router

from database.database import (
    save_scan,
    get_scan_history,
    get_scan_by_job_id,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Unified Security Scanner API",
    description=(
        "Unified GUI and RAG Assistant for "
        "Nmap, Nuclei, OWASP ZAP, Nessus and OpenVAS"
    ),
    version="1.1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# AI ASSISTANT
# ============================================================

app.include_router(ai_router)


# ============================================================
# BACKGROUND SCAN SYSTEM
# ============================================================

executor = ThreadPoolExecutor(max_workers=2)
scan_jobs = {}
scan_lock = threading.Lock()


# ============================================================
# SCAN REQUEST MODEL
# ============================================================

class ScanRequest(BaseModel):
    scanner: str
    target: str


# ============================================================
# SAVE SCAN SAFELY
# ============================================================

def persist_scan(job):
    """Save scan history without crashing the scan worker."""
    try:
        save_scan(job)
    except Exception as exc:
        print("Failed to save scan history:", str(exc))


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "Unified Security Scanner API Running",
        "status": "online",
        "scanners": [
            "Nmap",
            "Nuclei",
            "OWASP ZAP",
            "Nessus",
            "OpenVAS",
        ],
        "assistant": "RAG Assistant",
    }


# ============================================================
# SCANNER EXECUTION
# ============================================================

def execute_scan(job_id: str, scanner: str, target: str):
    try:
        with scan_lock:
            scan_jobs[job_id]["status"] = "running"
            scan_jobs[job_id]["started_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
            running_job = scan_jobs[job_id].copy()

        persist_scan(running_job)

        print("\n================================")
        print("BACKGROUND SCAN STARTED")
        print("Job ID :", job_id)
        print("Scanner:", scanner)
        print("Target :", target)
        print("================================")

        # NMAP
        if scanner == "nmap":
            findings = run_nmap(target)

        # NUCLEI
        elif scanner == "nuclei":
            findings = run_nuclei(target)

        # OWASP ZAP
        elif scanner == "zap":
            findings = run_zap(target)

        # NIKTO
        elif scanner == "nikto":
            findings = run_nikto(target)

        elif scanner == "nessus":
            findings = [{
                "scanner": "Nessus",
                "target": target,
                "title": "Nessus Not Configured",
                "severity": "Info",
                "description": (
                    "A Nessus server connection has not "
                    "been configured. Live integration "
                    "requires a Nessus server and API credentials."
                ),
                "port": None,
            }]

        # OPENVAS
        elif scanner == "openvas":
            findings = [{
                "scanner": "OpenVAS",
                "target": target,
                "title": "OpenVAS Not Configured",
                "severity": "Info",
                "description": (
                    "An OpenVAS/Greenbone server connection "
                    "has not been configured. Live integration "
                    "requires a Greenbone/OpenVAS server."
                ),
                "port": None,
            }]

        else:
            raise ValueError(f"Unsupported scanner: {scanner}")

        if not isinstance(findings, list):
            raise ValueError(
                "Scanner returned an unexpected results format."
            )

        with scan_lock:
            scan_jobs[job_id]["status"] = "completed"
            scan_jobs[job_id]["findings"] = findings
            scan_jobs[job_id]["finished_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
            completed_job = scan_jobs[job_id].copy()

        persist_scan(completed_job)

        print("\n================================")
        print("BACKGROUND SCAN COMPLETED")
        print("Job ID :", job_id)
        print("Findings:", len(findings))
        print("================================")

    except Exception as exc:
        print("\n================================")
        print("BACKGROUND SCAN FAILED")
        print("Job ID :", job_id)
        print("Error  :", str(exc))
        print("================================")

        with scan_lock:
            if job_id in scan_jobs:
                scan_jobs[job_id]["status"] = "failed"
                scan_jobs[job_id]["error"] = str(exc)
                scan_jobs[job_id]["finished_at"] = (
                    datetime.now(timezone.utc).isoformat()
                )
                failed_job = scan_jobs[job_id].copy()
            else:
                failed_job = None

        if failed_job:
            persist_scan(failed_job)


# ============================================================
# START BACKGROUND SCAN
# ============================================================

@app.post("/scan/start")
def start_scan(request: ScanRequest):
    scanner = request.scanner.lower().strip()
    target = request.target.strip()

    if not scanner:
        raise HTTPException(
            status_code=400,
            detail="Scanner is required.",
        )

    if not target:
        raise HTTPException(
            status_code=400,
            detail="Target is required.",
        )

    supported_scanners = [
        "nmap",
        "nuclei",
        "zap",
        "nikto",
    ]

    if scanner not in supported_scanners:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported scanner: {scanner}",
        )

    job_id = str(uuid4())

    job = {
        "job_id": job_id,
        "scanner": scanner,
        "target": target,
        "status": "queued",
        "findings": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    with scan_lock:
        scan_jobs[job_id] = job

    persist_scan(job.copy())

    try:
        executor.submit(
            execute_scan,
            job_id,
            scanner,
            target,
        )
    except Exception as exc:
        with scan_lock:
            scan_jobs[job_id]["status"] = "failed"
            scan_jobs[job_id]["error"] = str(exc)
            scan_jobs[job_id]["finished_at"] = (
                datetime.now(timezone.utc).isoformat()
            )
            failed_job = scan_jobs[job_id].copy()

        persist_scan(failed_job)

        raise HTTPException(
            status_code=500,
            detail="Could not schedule scan.",
        ) from exc

    return {
        "job_id": job_id,
        "scanner": scanner,
        "target": target,
        "status": "queued",
        "message": "Scan started successfully.",
    }


# ============================================================
# GET SCAN STATUS
# ============================================================

@app.get("/scan/status/{job_id}")
def get_scan_status(job_id: str):
    with scan_lock:
        job = scan_jobs.get(job_id)

        if job is not None:
            return job.copy()

    # Allow lookup after a backend restart.
    saved_job = get_scan_by_job_id(job_id)

    if saved_job is None:
        raise HTTPException(
            status_code=404,
            detail="Scan job not found.",
        )

    return saved_job


# ============================================================
# SCAN HISTORY
# ============================================================

@app.get("/history")
def get_history(limit: int = 100):
    if limit < 1 or limit > 500:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 500.",
        )

    history = get_scan_history(limit)

    return {
        "count": len(history),
        "history": history,
    }


@app.get("/history/{job_id}")
def get_history_item(job_id: str):
    record = get_scan_by_job_id(job_id)

    if record is None:
        raise HTTPException(
            status_code=404,
            detail="Scan history record not found.",
        )

    return record


# ============================================================
# OLD SYNCHRONOUS ENDPOINT
# Preserved for compatibility.
# ============================================================

@app.post("/scan")
def scan(request: ScanRequest):
    scanner = request.scanner.lower().strip()
    target = request.target.strip()

    if not scanner:
        raise HTTPException(
            status_code=400,
            detail="Scanner is required.",
        )

    if not target:
        raise HTTPException(
            status_code=400,
            detail="Target is required.",
        )

    if scanner == "nmap":
        return run_nmap(target)

    elif scanner == "nuclei":
        return run_nuclei(target)

    elif scanner == "zap":
        return run_zap(target)

    elif scanner == "nessus":
        return [{
            "scanner": "Nessus",
            "target": target,
            "title": "Nessus Not Configured",
            "severity": "Info",
            "description": (
                "Nessus server and API credentials "
                "are required for live scanning."
            ),
            "port": None,
        }]

    elif scanner == "openvas":
        return [{
            "scanner": "OpenVAS",
            "target": target,
            "title": "OpenVAS Not Configured",
            "severity": "Info",
            "description": (
                "OpenVAS/Greenbone server configuration "
                "is required for live scanning."
            ),
            "port": None,
        }]

    raise HTTPException(
        status_code=400,
        detail=f"Unsupported scanner: {scanner}",
    )


