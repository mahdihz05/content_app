class PromptBuilder:
    """
    Base prompt builder class.
    Makes it easy to create expandable and structured prompts.
    """

    def __init__(self, language="Persian"):
        self.language = language

    def wrap(self, content: str) -> str:
        """
        Final wrapper for prompts.
        Useful for adding global rules later (e.g., RAG context injection).
        """
        return f"{content.strip()}\n\nLanguage: Respond in {self.language}."

    def json_only(self, json_schema: str, body: str) -> str:
        """
        Helper: enforce strict JSON output + schema.
        """
        return self.wrap(f"""
{body}

OUTPUT FORMAT (STRICT JSON ONLY):
{json_schema}

Rules:
- No text outside JSON.
- No markdown.
- Must be valid JSON.
""")
