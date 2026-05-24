from content.models import ContentItem
from ai.pipelines.create_content.base_pipeline import BasePipeline


class CampaignPipeline(BasePipeline):

    def run(self, context):

        campaign_id = context["payload"]["campaign_id"]

        content = ContentItem.objects.create(
            campaign_id=campaign_id,
            step="basic_info",
            status="idle"
        )

        context["content_item"] = content

        return context
