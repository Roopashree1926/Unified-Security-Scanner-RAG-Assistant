import { useState } from "react";

function Assistant() {

    const [question, setQuestion] = useState("");
    const [answer, setAnswer] = useState("");
    const [sources, setSources] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const askAssistant = async () => {

        if (!question.trim()) {
            setError("Please enter a question.");
            return;
        }

        setLoading(true);
        setError("");
        setAnswer("");
        setSources([]);

        try {

            const response = await fetch(
                "http://127.0.0.1:8000/assistant/ask",
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        question: question.trim()
                    })
                }
            );

            if (!response.ok) {
                throw new Error("Assistant request failed.");
            }

            const data = await response.json();

            setAnswer(data.answer || "No answer received.");
            setSources(data.sources || []);

        } catch (err) {

            setError(
                err.message ||
                "Unable to connect to RAG Assistant."
            );

        } finally {

            setLoading(false);

        }
    };

    return (
        <section className="assistant">

            <div className="assistant-header">

                <div>
                    <h2>🤖 RAG Security Assistant</h2>

                    <p>
                        Ask security questions and get
                        knowledge-based recommendations.
                    </p>
                </div>

                <div className="assistant-status">
                    ● AI Online
                </div>

            </div>

            <div className="assistant-input">

                <input
                    type="text"
                    placeholder="Ask something like: What is Nuclei?"
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => {
                        if (e.key === "Enter") {
                            askAssistant();
                        }
                    }}
                />

                <button
                    onClick={askAssistant}
                    disabled={loading}
                >
                    {loading ? "Thinking..." : "Ask"}
                </button>

            </div>

            {error && (
                <div className="error-box">
                    {error}
                </div>
            )}

            {answer && (
                <div className="assistant-answer">

                    <h3>AI Response</h3>

                    <div className="answer-content">
                        {answer}
                    </div>

                    {sources.length > 0 && (
                        <div className="sources">

                            <strong>Knowledge Sources:</strong>

                            <div className="source-list">
                                {sources.map((source, index) => (
                                    <span key={index}>
                                        {source}
                                    </span>
                                ))}
                            </div>

                        </div>
                    )}

                </div>
            )}

        </section>
    );
}

export default Assistant;