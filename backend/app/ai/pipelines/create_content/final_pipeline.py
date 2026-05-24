from ai.pipelines.create_content.base_pipeline import BasePipeline
from ai.services.ai_service import AIService


class FinalPipeline(BasePipeline):

    def __init__(self):
        self.ai = AIService()

    def run(self, context):

        content_item = context["content_item"]

        form = content_item.content_form

        article = self.ai.generate_article(
            keyword=content_item.main_keyword,
            research=content_item.information.get("research"),
            form_data=form.data
        )

        content_item.description = article
        content_item.status = "completed"

        content_item.save()

        context["result"] = article

        return context
