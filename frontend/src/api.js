const API_URL = "http://127.0.0.1:8000";


export async function startScan(scanner, target) {

    const response = await fetch(
        `${API_URL}/scan/start`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                scanner,
                target
            })
        }
    );

    if (!response.ok) {

        const error = await response
            .json()
            .catch(() => ({}));

        throw new Error(
            error.detail || "Unable to start scan."
        );
    }

    return await response.json();
}


export async function getScanStatus(jobId) {

    const response = await fetch(
        `${API_URL}/scan/status/${jobId}`
    );

    if (!response.ok) {

        const error = await response
            .json()
            .catch(() => ({}));

        throw new Error(
            error.detail || "Unable to get scan status."
        );
    }

    return await response.json();
}


// Keep the old function for compatibility
export async function runScan(scanner, target) {

    const response = await fetch(
        `${API_URL}/scan`,
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                scanner,
                target
            })
        }
    );

    if (!response.ok) {

        const error = await response
            .json()
            .catch(() => ({}));

        throw new Error(
            error.detail || "Scan failed."
        );
    }

    return await response.json();
}