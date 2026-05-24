class SummaryPrompts:

    @staticmethod
    def get_summary_prompt(content, platform="generic", language="Persian"):

        return f"""
Summarize this article.

Platform: {platform}

Content:
{content[:1200]}

Return summary text only.

Language: {language}.
"""
