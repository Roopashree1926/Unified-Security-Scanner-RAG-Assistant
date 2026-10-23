function Navbar({
    activePage,
    setActivePage
}) {

    return (

        <nav className="navbar">

            <div className="nav-content">

                <div
                    className="logo"
                    onClick={() => setActivePage("scanner")}
                    style={{ cursor: "pointer" }}
                >
                    Unified Scanner
                </div>


                <div className="nav-links">

                    <button
                        className={
                            activePage === "scanner"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("scanner")
                        }
                    >
                        Scanner
                    </button>


                    <button
                        className={
                            activePage === "history"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("history")
                        }
                    >
                        History
                    </button>


                    <button
                        className={
                            activePage === "reports"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("reports")
                        }
                    >
                        Reports
                    </button>


                    <button
                        className={
                            activePage === "assistant"
                                ? "nav-button active"
                                : "nav-button"
                        }
                        onClick={() =>
                            setActivePage("assistant")
                        }
                    >
                        AI Assistant
                    </button>


                    <div className="nav-status">

                        <span className="status-dot"></span>

                        System Ready

                    </div>

                </div>

            </div>

        </nav>
    );
}


export default Navbar;