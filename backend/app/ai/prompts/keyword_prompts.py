class KeywordPrompts:

    @staticmethod
    def get_keyword_generation_prompt(form_data, language="Persian"):

        return f"""
Generate SEO keyword set.

Input data:
{form_data}

Return JSON:

{{
  "primary_keyword": "",
  "secondary_keywords": [],
  "long_tail_keywords": [],
  "question_keywords": [],
  "lsi_keywords": []
}}

Language: Respond in {language}.
"""
