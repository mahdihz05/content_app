from ai.pipelines.create_content.base_pipeline import BasePipeline


class ApprovalPipeline(BasePipeline):

    def run(self, context):

        content_item = context["content_item"]

        content_item.step = "completed"
        content_item.status = "generating"

        content_item.save()

        return context
