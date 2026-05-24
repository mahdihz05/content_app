from ai.pipelines.create_content.base_pipeline import BasePipeline
from content.models import ContentForm


class KnowledgePipeline(BasePipeline):

    def run(self, context):

        content_item = context["content_item"]
        form_data = context["payload"]

        form, created = ContentForm.objects.get_or_create(
            content_item=content_item
        )

        form.data = form_data
        form.save()

        content_item.step = "approval"
        content_item.save()

        return context
