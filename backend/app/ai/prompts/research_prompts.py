class ResearchPrompts:

    @staticmethod
    def get_research_prompt(keyword, language="Persian"):
        return f"""
You are a Senior SEO Strategist and Topic Researcher.
Your job is to deeply analyze the following keyword and provide structured insights for high-quality content planning.

Target Keyword: "{keyword}"

INSTRUCTIONS:
- Think step by step.
- Base your reasoning on real-world SEO and SERP behavior.
- Do NOT add any explanation outside the JSON.
- Make sure the JSON is valid and can be parsed by a standard JSON parser.
- Do NOT include trailing commas.

TASKS:
1) Search Intent:
   - Determine the dominant search intent for this keyword.
   - One of: "Informational", "Transactional", "Navigational", "Commercial Investigation".
2) Target Audience:
   - Describe who is searching for this keyword (job role, level, needs, pain points).
3) Competitor Gap Overview:
   - List up to 5 important sub-topics that top-ranking pages usually cover.
   - Then list 3–5 angle ideas or gaps that are often missing and can be used to stand out.
4) Semantic / LSI Keywords:
   - Provide a list of 10–20 LSI / NLP-related keywords and phrases for "{keyword}".
5) Key Takeaways:
   - List 5–7 crucial insights or points that MUST be included in the final content.
6) Suggested Title:
   - Propose 1 strong SEO title that is attractive and click-worthy.

OUTPUT FORMAT (STRICT JSON ONLY):

{{
  "search_intent": "Informational | Transactional | Navigational | Commercial Investigation",
  "target_audience": "string describing audience profile",
  "competitor_subtopics": [
    "subtopic 1",
    "subtopic 2"
  ],
  "gap_opportunities": [
    "angle or gap 1",
    "angle or gap 2"
  ],
  "key_takeaways": [
    "point 1",
    "point 2"
  ],
  "lsi_keywords": [
    "lsi keyword 1",
    "lsi keyword 2"
  ],
  "suggested_title": "SEO-friendly blog post title"
}}

Language: Respond in {language}.
"""

    @staticmethod
    def get_search_queries_prompt(topic_title, main_keyword, language="Persian", count=5, existing_queries=None):

        existing_queries = existing_queries or []

        return f"""
You are an SEO research assistant that generates realistic Google search queries.

Topic Title:
"{topic_title}"

Main Keyword:
"{main_keyword}"

Language: {language}

Generate {count} realistic Google queries.

Existing queries (do not repeat):
{existing_queries}

Return JSON:

{{
  "queries": [
    "query 1",
    "query 2",
    "query 3"
  ]
}}
"""

    @staticmethod
    def get_merge_research_prompt(research_items, topic_title, main_keyword, language="Persian"):

        return f"""
You are a Senior Research Synthesizer.

TOPIC:
Title: "{topic_title}"
Keyword: "{main_keyword}"

RESEARCH SOURCES:
{research_items}

OUTPUT FORMAT (STRICT JSON):

{{
  "high_level_summary": "2-4 paragraphs",
  "structured_notes": [
    {{
      "heading": "subtopic",
      "summary": "short explanation",
      "key_points": [
        "point 1",
        "point 2"
      ]
    }}
  ],
  "conflicts_or_caveats": [],
  "important_stats": []
}}

Language: Respond in {language}.
"""

    @staticmethod
    def get_fetch_source_data_prompt(query: str) -> str:

        return f"""
Simulate Google search scraping.

Search query:
"{query}"

Return JSON:

{{
  "sources": [
    {{
      "title": "Title",
      "url": "https://example.com",
      "raw_html": "<html> ... </html>"
    }}
  ],
  "summary": {{
    "paragraph": "summary",
    "key_points": [
      "point 1",
      "point 2"
    ]
  }}
}}
"""
