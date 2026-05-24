class OutlinePrompts:

    @staticmethod
    def get_outline_prompt(topic_title, main_keyword, merged_research_json,
                           goal=None, platform=None, form_schema_data=None,
                           language="Persian"):

        goal_text = f'- Content goal: "{goal}"' if goal else ""
        platform_text = f'- Target platform: "{platform}"' if platform else ""
        form_text = f'- Additional structured form data: {form_schema_data}' if form_schema_data else ""

        return f"""
You are a Content Architect and SEO Strategist.

TOPIC:
Title: "{topic_title}"
Keyword: "{main_keyword}"

{goal_text}
{platform_text}
{form_text}

RESEARCH:
{merged_research_json}

Return JSON:

{{
  "outline": [
    {{
      "tag": "H1",
      "title": "title",
      "description": "overall coverage"
    }},
    {{
      "tag": "H2",
      "title": "section",
      "description": "purpose",
      "subsections": []
    }}
  ],
  "recommended_length_words": 2200
}}

Language: Respond in {language}.
"""

    @staticmethod
    def get_outline_improvement_prompt(current_outline_json, feedback_text,
                                       topic_title=None, main_keyword=None,
                                       language="Persian"):

        return f"""
Improve this outline based on feedback.

Outline:
{current_outline_json}

Feedback:
{feedback_text}

Return updated outline JSON.

Language: Respond in {language}.
"""
