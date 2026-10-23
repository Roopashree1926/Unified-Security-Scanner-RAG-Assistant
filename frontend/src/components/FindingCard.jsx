function FindingCard({ finding }) {

    const severity =
        finding.severity?.toLowerCase() || "info";

    return (
        <div className={`finding-card ${severity}`}>

            <div className="finding-top">

                <h3>
                    {finding.title || "Security Finding"}
                </h3>

                <span className={`severity ${severity}`}>
                    {finding.severity || "Info"}
                </span>

            </div>

            <div className="finding-details">

                <p>
                    <strong>Scanner:</strong>{" "}
                    {finding.scanner}
                </p>

                <p>
                    <strong>Target:</strong>{" "}
                    {finding.target}
                </p>

                <p>
                    <strong>Port:</strong>{" "}
                    {finding.port ?? "-"}
                </p>

                <p>
                    <strong>Description:</strong>{" "}
                    {finding.description || "No description available."}
                </p>

            </div>

        </div>
    );
}

export default FindingCard;