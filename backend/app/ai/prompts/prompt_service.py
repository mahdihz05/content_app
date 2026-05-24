from .research_prompts import ResearchPrompts
from .outline_prompts import OutlinePrompts
from .generation_prompts import GenerationPrompts
from .seo_prompts import SEOPrompts
from .summary_prompts import SummaryPrompts
from .keyword_prompts import KeywordPrompts
from .interview_prompts import InterviewPrompts


class PromptService:

    research = ResearchPrompts()
    outline = OutlinePrompts()
    generation = GenerationPrompts()
    seo = SEOPrompts()
    summary = SummaryPrompts()
    keywords = KeywordPrompts()
    interview = InterviewPrompts()
