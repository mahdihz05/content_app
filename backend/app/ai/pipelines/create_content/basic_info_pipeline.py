from ai.pipelines.create_content.base_pipeline import BasePipeline


class BasicInfoPipeline(BasePipeline):

    def run(self, context):
        print('---++++++++++++++++++++++++++++----')
        print(context)
        print('---++++++++++++++++++++++++++++----')
        content_item = context["content_item"]
        data = context["payload"]

        content_item.title = data.get("title")
        content_item.description = data.get("description", "")
        content_item.step = "production_info"

        content_item.save()

        return context
