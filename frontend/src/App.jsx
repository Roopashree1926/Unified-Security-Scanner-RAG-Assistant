import { useEffect, useState } from "react";

import ScannerForm from "./components/ScannerForm";
import Dashboard from "./components/Dashboard";
import Assistant from "./components/Assistant";
import Navbar from "./components/Navbar";
import History from "./components/History";
import Reports from "./components/Reports";

import "./App.css";


function App() {

    const [results, setResults] = useState([]);
    const [scanner, setScanner] = useState("");
    const [target, setTarget] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const [activePage, setActivePage] = useState("scanner");

    const [history, setHistory] = useState(() => {

        try {

            const saved =
                localStorage.getItem("unifiedScannerHistory");

            return saved
                ? JSON.parse(saved)
                : [];

        } catch {

            return [];
        }
    });


    useEffect(() => {

        localStorage.setItem(
            "unifiedScannerHistory",
            JSON.stringify(history)
        );

    }, [history]);


    const saveScanToHistory = (
        completedScanner,
        completedTarget,
        findings
    ) => {

        const scan = {

            id: Date.now(),

            scanner: completedScanner,

            target: completedTarget,

            findings: Array.isArray(findings)
                ? findings
                : [],

            status: "Completed",

            date: new Date().toLocaleString()

        };


        setHistory(previous => [
            scan,
            ...previous
        ]);
    };


    return (
        <div className="app">

            <Navbar
                activePage={activePage}
                setActivePage={setActivePage}
            />


            <main className="container">

                {activePage === "scanner" && (
                    <>

                        <section className="hero">

                            <h1>
                                Unified Security Scanner
                            </h1>

                            <p>
                                Unified vulnerability scanning using Nmap, Nuclei, OWASP ZAP and Nikto
                            </p>

                        </section>


                        <ScannerForm

                            scanner={scanner}
                            setScanner={setScanner}

                            target={target}
                            setTarget={setTarget}

                            setResults={setResults}

                            loading={loading}
                            setLoading={setLoading}

                            setError={setError}

                            onScanComplete={
                                saveScanToHistory
                            }

                        />


                        {error && (
                            <div className="error-box">
                                {error}
                            </div>
                        )}


                        <Dashboard
                            results={results}
                            scanner={scanner}
                            target={target}
                        />

                    </>
                )}


                {activePage === "history" && (

                    <History
                        history={history}
                        setHistory={setHistory}
                    />

                )}


                {activePage === "reports" && (

                    <Reports
                        history={history}
                    />

                )}


                {activePage === "assistant" && (

                    <Assistant />

                )}

            </main>

        </div>
    );
}


export default App;