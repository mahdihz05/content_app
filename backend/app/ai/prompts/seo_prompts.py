class SEOPrompts:

    @staticmethod
    def get_seo_metadata_prompt(content, language="Persian"):

        return f"""
Generate SEO metadata.

Content:
{content[:2000]}

Return JSON:

{{
  "meta_title": "",
  "meta_description": "",
  "slug": "",
  "tags": []
}}

Language: Respond in {language}.
"""
