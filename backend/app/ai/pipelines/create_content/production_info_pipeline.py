from ai.pipelines.create_content.base_pipeline import BasePipeline


class ProductionInfoPipeline(BasePipeline):

    def run(self, context):

        content_item = context["content_item"]
        data = context["payload"]

        content_item.goal = data.get("goal")
        content_item.platform = data.get("platform", "website")
        content_item.language = data.get("language", "fa")

        content_item.step = "keywords"

        content_item.save()

        return context
