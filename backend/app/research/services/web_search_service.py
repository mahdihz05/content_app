import requests
from django.conf import settings


class WebSearchService:

    SERP_API_URL = "https://serpapi.com/search"

    def search(self, query: str, max_results: int = 10) -> list:

        api_key = getattr(settings, "SERP_API_KEY", None)

        if not api_key:
            print("⚠️ SERP_API_KEY not set")
            return []

        try:
            response = requests.get(
                self.SERP_API_URL,
                params={
                    "q": query,
                    "api_key": api_key,
                    "num": max_results,
                    "hl": "fa",
                    "gl": "ir",
                },
                timeout=10,
            )

            data = response.json()
            results = []

            for item in data.get("organic_results", []):

                title = item.get("title", "")
                url = item.get("link", "")
                snippet = item.get("snippet", "")

                if not title:
                    continue

                results.append({
                    "title": title,
                    "url": url,
                    "summary": snippet,
                    "raw_text": snippet,
                })

            return results[:max_results]

        except Exception as e:
            print(f"❌ SerpAPI error: {e}")
            return []