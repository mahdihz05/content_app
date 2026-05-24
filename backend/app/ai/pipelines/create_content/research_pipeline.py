from research.models import ResearchSource
from ai.services.prompt_service import PromptService
from ai.services.ai_service import AIService
from content.models import ContentItem
import json


class ResearchPipeline:

    def __init__(self):
        self.ai_service = AIService()

    def run(self, content_item: ContentItem):
        """
        Full automated research pipeline
        """

        # مرحله 1: Generate Queries
        queries = self._generate_queries(content_item)

        created_sources = []

        # مرحله 2: Fetch Data
        for query in queries:
            source = ResearchSource.objects.create(
                content_item=content_item,
                title=query,
                source_type="ai",
                is_selected=True
            )

            data = self._fetch_source_data(query)

            source.summary = data.get("summary", "")
            source.raw_text = data.get("raw_text", "")

            if hasattr(source, "sources_json"):
                source.sources_json = data.get("sources", [])

            source.save()

            created_sources.append(source)

        # مرحله 3: Finalize
        self._finalize_research(content_item)

        return created_sources

    def _generate_queries(self, content_item):
        prompt = PromptService.get_search_queries_prompt(
            topic_title=content_item.title,
            main_keyword=content_item.main_keyword or content_item.title,
            language="Persian",
            count=5,
            existing_queries=[]
        )

        response = self.ai_service.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You generate search queries."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format="json"
        )

        data = json.loads(response)

        return data.get("queries", [])

    def _fetch_source_data(self, query):
        prompt = PromptService.get_fetch_source_data_prompt(query=query)

        response = self.ai_service.chat(
            messages=[
                {
                    "role": "system",
                    "content": "You simulate web research."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            response_format="json",
            temperature=0.3
        )

        data = json.loads(response)

        return {
            "summary": data.get("summary", {}).get("paragraph", ""),
            "sources": data.get("sources", []),
            "raw_text": "\n\n".join([
                s.get("raw_html", "")
                for s in data.get("sources", [])
                if isinstance(s, dict)
            ])
        }

    def _finalize_research(self, content_item):
        sources = content_item.research_sources.filter(is_selected=True)

        final_list = []

        for src in sources:
            final_list.append({
                "title": src.title,
                "summary": src.summary,
                "raw_text": src.raw_text
            })

        content_item.information = {
            "research": final_list
        }

        content_item.status = "research_done"
        content_item.save()