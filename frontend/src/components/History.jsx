function History({ history, setHistory }) {

    const clearHistory = () => {

        if (
            window.confirm(
                "Are you sure you want to clear scan history?"
            )
        ) {

            setHistory([]);

        }
    };


    return (

        <section className="page-section">

            <div className="page-header">

                <div>

                    <h2>Scan History</h2>

                    <p>
                        Previously completed security scans.
                    </p>

                </div>


                {history.length > 0 && (

                    <button
                        className="danger-button"
                        onClick={clearHistory}
                    >
                        Clear History
                    </button>

                )}

            </div>


            {history.length === 0 ? (

                <div className="empty-state">

                    <h3>No scan history</h3>

                    <p>
                        Run a scanner to create your first
                        history record.
                    </p>

                </div>

            ) : (

                <div className="history-list">

                    {history.map((scan) => (

                        <div
                            className="history-card"
                            key={scan.id}
                        >

                            <div>

                                <h3>
                                    {scan.scanner.toUpperCase()}
                                </h3>

                                <p>
                                    Target:{" "}
                                    <strong>
                                        {scan.target}
                                    </strong>
                                </p>

                                <p>
                                    Date: {scan.date}
                                </p>

                            </div>


                            <div className="history-meta">

                                <span className="success-badge">
                                    {scan.status}
                                </span>

                                <span>
                                    {scan.findings.length} Findings
                                </span>

                            </div>

                        </div>

                    ))}

                </div>

            )}

        </section>
    );
}


export default History;