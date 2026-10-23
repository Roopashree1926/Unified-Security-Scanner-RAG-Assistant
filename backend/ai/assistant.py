
import os

from google import genai
from google.genai import types
from dotenv import load_dotenv

from ai.rag import retrieve_context

load_dotenv()

MODEL = "gemini-3.5-flash-lite"


def ask_assistant(question: str):
    if not question or not question.strip():
        return {"answer": "Please enter a question.", "sources": []}

    question = question.strip()
    contexts = []

    try:
        # Retrieve local security knowledge
        contexts = retrieve_context(question, top_k=2)

        context_text = "\n\n".join(
            f"### {item['topic']}\n{item['content'].strip()}"
            for item in contexts
        ) if contexts else "No directly relevant information found."

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "answer": "GEMINI_API_KEY is missing from the backend .env file.",
                "sources": []
            }

        # Limit how long the request waits
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=20000)
        )

        prompt = f"""You are the AI Security Assistant for Unified Security Scanner.
Answer clearly and accurately. Use the retrieved context when relevant.
Give practical defensive cybersecurity guidance.
Keep simple questions concise. Use numbered steps when appropriate.

Retrieved security knowledge:
{context_text}

User question:
{question}
"""

        print(f"Sending one request to Gemini ({MODEL})...")

        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=400
            )
        )

        if response and response.text:
            print("Gemini response received.")
            return {
                "answer": response.text,
                "sources": [item["topic"] for item in contexts]
            }

        return {
            "answer": "Gemini returned an empty response. Please try again.",
            "sources": [item["topic"] for item in contexts]
        }

    except Exception as e:
        print(f"AI Assistant error: {type(e).__name__}: {e}")
        return {
            "answer": (
                "The AI Assistant could not generate a response. "
                "Please check the backend terminal for details."
            ),
            "sources": [item["topic"] for item in contexts]
        }
