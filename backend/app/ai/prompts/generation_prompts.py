class GenerationPrompts:

    @staticmethod
    def get_final_generation_prompt(platform,
                                    outline_json,
                                    merged_research_json,
                                    tone="Professional",
                                    language="Persian"):

        if platform and platform.lower() == "instagram":
            return f"""
Create an Instagram post.

Outline:
{outline_json}

Research:
{merged_research_json}

Return JSON:

{{
  "visual_idea": "",
  "caption": "",
  "cta": "",
  "hashtags": []
}}

Language: Respond in {language}.
"""

        return f"""
Write a high quality article.

Outline:
{outline_json}

Research:
{merged_research_json}

Return HTML only.

Language: {language}.
"""

    @staticmethod
    def get_section_generation_prompt(full_outline_json,
                                      merged_research_json,
                                      target_section_id_or_title,
                                      tone="Professional",
                                      language="Persian"):

        return f"""
Write only this section:

Section:
{target_section_id_or_title}

Outline:
{full_outline_json}

Research:
{merged_research_json}

Return Markdown section only.

Language: {language}.
"""
