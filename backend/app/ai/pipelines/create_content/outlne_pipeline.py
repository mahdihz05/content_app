from .basic_info_pipeline import BasicInfoPipeline


class OutlinePipeline(BasicInfoPipeline):

    def run(self, context):

        content_item = self.get_content(context)

        topic = content_item.main_keyword
        keywords = content_item.additional_keywords

        outline = self.ai.generate_outline(
            topic=topic,
            keywords=keywords
        )

        information = content_item.information or {}
        information["outline"] = outline

        self.update_content(
            content_item,
            information=information,
            step="outline_done",
            status="outline_done"
        )

        return context
