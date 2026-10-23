# Simple local RAG knowledge base for Unified Security Scanner

KNOWLEDGE_BASE = [
    {
        "topic": "Nmap",
        "content": """
        Nmap is a network discovery and security auditing tool.
        It can identify open ports, running services, service versions
        and basic host information. Nmap is mainly useful for network
        reconnaissance and port/service discovery.
        """
    },
    {
        "topic": "Nuclei",
        "content": """
        Nuclei is a fast vulnerability scanner that uses templates
        to identify known security issues, exposed technologies,
        misconfigurations and vulnerabilities in web applications
        and other targets.
        """
    },
    {
        "topic": "OWASP ZAP",
        "content": """
        OWASP ZAP is a web application security testing tool.
        It can identify potential web security issues, including
        missing security headers and other alerts. In this project,
        ZAP is configured for passive scanning of target URLs.
        Findings should be validated; no alerts do not prove that
        an application is free of vulnerabilities.
        """
    },
    {
        "topic": "Nikto",
        "content": """
        Nikto is a web server scanner that checks for potentially
        dangerous files, outdated server software, and server
        configuration issues. It can also report missing recommended
        HTTP security headers. Findings should be reviewed and validated.
        """
    },
    {
        "topic": "Missing Security Headers",
        "content": """
        Missing HTTP security headers can weaken web application security.
        Important headers include Content-Security-Policy,
        X-Content-Type-Options, X-Frame-Options, Referrer-Policy,
        Permissions-Policy and Strict-Transport-Security.
        """
    },
    {
        "topic": "Outdated Software",
        "content": """
        Outdated software may contain publicly known vulnerabilities.
        Recommended remediation is to upgrade the affected software
        to a supported and secure version and verify that the vulnerable
        version is no longer exposed.
        """
    },
    {
        "topic": "Cookie Security",
        "content": """
        Cookies containing session information should use appropriate
        security attributes such as Secure, HttpOnly and SameSite.
        These attributes help reduce the risk of session theft and
        cross-site attacks.
        """
    },
    {
        "topic": "High Severity",
        "content": """
        High severity findings should normally receive priority because
        they may represent significant security exposure. Analysts should
        validate the finding, determine affected assets and apply the
        recommended remediation as soon as practical.
        """
    }
]


def retrieve_context(question: str, top_k: int = 3):
    """Retrieve relevant knowledge-base entries using keyword matching."""

    question_words = set(
        question.lower()
        .replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
        .split()
    )

    scored = []

    for item in KNOWLEDGE_BASE:
        text = (item["topic"] + " " + item["content"]).lower()
        score = sum(1 for word in question_words if word in text)

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    return [item for score, item in scored[:top_k]]


def rag_answer(question: str):
    """Retrieve relevant security knowledge and create an answer."""

    contexts = retrieve_context(question)

    if not contexts:
        return {
            "answer": (
                "I could not find a relevant security topic in the "
                "current knowledge base. Try asking about Nmap, Nuclei, "
                "OWASP ZAP, Nikto, security headers, outdated software, "
                "cookies or severity."
            ),
            "sources": []
        }

    answer_parts = []

    for item in contexts:
        answer_parts.append(
            f"**{item['topic']}**\n{item['content'].strip()}"
        )

    answer = (
        "Based on the retrieved security knowledge:\n\n"
        + "\n\n".join(answer_parts)
    )

    return {
        "answer": answer,
        "sources": [item["topic"] for item in contexts]
    }
