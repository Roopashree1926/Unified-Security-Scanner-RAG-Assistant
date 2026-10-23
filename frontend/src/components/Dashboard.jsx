import FindingCard from "./FindingCard";

function Dashboard({ results, scanner, target }) {

    return (
        <section className="dashboard">

            <div className="dashboard-header">

                <div>

                    <h2>Scan Results</h2>

                    {scanner && (
                        <p>
                            Scanner:{" "}
                            <strong>
                                {scanner.toUpperCase()}
                            </strong>
                        </p>
                    )}

                    {target && (
                        <p>
                            Target:{" "}
                            <strong>{target}</strong>
                        </p>
                    )}

                </div>

                {results.length > 0 && (
                    <div className="result-count">
                        {results.length} Findings
                    </div>
                )}

            </div>

            {results.length === 0 ? (

                <div className="empty-state">

                    <div className="empty-icon">
                        🛡️
                    </div>

                    <h3>No scan results</h3>

                    <p>
                        Select a scanner, enter a target
                        and click Scan.
                    </p>

                </div>

            ) : (

                <div className="findings">

                    {results.map((finding, index) => (

                        <FindingCard
                            key={index}
                            finding={finding}
                        />

                    ))}

                </div>

            )}

        </section>
    );
}

export default Dashboard;