from ai.pipelines.create_content.base_pipeline import BasePipeline


class KeywordsPipeline(BasePipeline):

    def run(self, context):

        content_item = context["content_item"]
        data = context["payload"]

        content_item.main_keyword = data.get("main_keyword")
        content_item.additional_keywords = data.get("additional_keywords", [])

        content_item.step = "research"
        content_item.status = "researching"

        content_item.save()

        return context
