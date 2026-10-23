# Unified Security Scanner

## Project Overview
Unified Security Scanner is a web-based cybersecurity application that integrates four security scanning tools and an AI-powered security assistant.

## Main Features
- Nmap: Network discovery and port scanning.
- Nuclei: Template-based vulnerability detection.
- OWASP ZAP: Web application security scanning.
- Nikto: Web server security testing.
- RAG AI Security Assistant powered by Gemini.
- Scan history and PDF report generation.

## Technology Stack
- Frontend: React and Vite
- Backend: Python and FastAPI
- AI: Google Gemini
- Knowledge retrieval: Retrieval-Augmented Generation (RAG)

## Project Structure
- backend/: API, scanner integrations, and AI assistant.
- frontend/: User interface and application pages.

## Requirements
- Python and the backend virtual environment
- Node.js and npm
- Nmap, Nuclei, Nikto, and OWASP ZAP installed and configured
- Gemini API key configured in the backend environment

## Running the Backend
Open PowerShell:

    cd C:\Users\roopa\OneDrive\Desktop\unifiedscanner\backend
    ..\backend\venv\Scripts\python.exe -m uvicorn main:app --reload --host 127.0.0.1 --port 8000

Backend API documentation:
http://127.0.0.1:8000/docs

## Running the Frontend
Open a second PowerShell terminal:

    cd C:\Users\roopa\OneDrive\Desktop\unifiedscanner\frontend
    npm run dev

Frontend:
http://localhost:5173

## OWASP ZAP
Start OWASP ZAP separately using its configured API on 127.0.0.1:8080 before running ZAP scans.

## Security Notice
Only scan systems that you own or have explicit permission to test. Keep API keys and credentials private. Do not include secrets in source control.

## Limitations
Scanner results may contain false positives or miss vulnerabilities. Review findings manually before treating them as confirmed security issues. AI-generated explanations should also be verified.
