import { startScan, getScanStatus } from "../api";

function wait(ms) {
    return new Promise(resolve => {
        setTimeout(resolve, ms);
    });
}

function ScannerForm({
    scanner,
    setScanner,
    target,
    setTarget,
    setResults,
    loading,
    setLoading,
    setError,
    onScanComplete,
}) {
    const handleScan = async () => {
        if (!scanner) {
            setError("Please select a scanner.");
            return;
        }

        if (!target.trim()) {
            setError("Please enter a target.");
            return;
        }

        setError("");
        setResults([]);
        setLoading(true);

        try {
            let scanTarget = target.trim();

            // Nmap accepts a hostname or IP address.
            if (scanner === "nmap") {
                scanTarget = scanTarget
                    .replace(/^https?:\/\//, "")
                    .replace(/\/$/, "");
            }

            // Start the background scan.
            const job = await startScan(scanner, scanTarget);

            console.log("Scan started:", job.job_id);

            // Poll until the scan completes or fails.
            let finished = false;

            while (!finished) {
                await wait(2000);

                const status = await getScanStatus(job.job_id);

                console.log("Scan status:", status.status);

                if (status.status === "completed") {
                    const findings = Array.isArray(status.findings)
                        ? status.findings
                        : [];

                    setResults(findings);

                    if (onScanComplete) {
                        onScanComplete(
                            scanner,
                            scanTarget,
                            findings
                        );
                    }

                    finished = true;
                } else if (status.status === "failed") {
                    throw new Error(
                        status.error || "Scanner failed."
                    );
                }
            }
        } catch (error) {
            console.error("Scan error:", error);

            setError(error.message || "Scan failed.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <section className="scanner-form">
            <select
                value={scanner}
                onChange={e => setScanner(e.target.value)}
                disabled={loading}
            >
                <option value="">Select Scanner</option>
                <option value="nmap">Nmap</option>
                <option value="nuclei">Nuclei</option>
                <option value="zap">OWASP ZAP</option>
                <option value="nikto">Nikto</option>
            </select>

            <input
                type="text"
                placeholder="Enter target (example: scanme.nmap.org)"
                value={target}
                onChange={e => setTarget(e.target.value)}
                disabled={loading}
            />

            <button
                onClick={handleScan}
                disabled={loading}
            >
                {loading ? "Scanning..." : "Scan"}
            </button>
        </section>
    );
}

export default ScannerForm;

