from .basic_info_pipeline import BasicInfoPipeline
from .production_info_pipeline import ProductionInfoPipeline
from .keyword_pipline import KeywordsPipeline
from .research_pipeline import ResearchPipeline
from .knowledge_pipeline import KnowledgePipeline
from .approval_pipeline import ApprovalPipeline
from .final_pipeline import FinalPipeline


class CreateContentCore:
    """Pipeline مرکزی که توالی مراحل تولید محتوا را مدیریت می‌کند."""

    def run(self, context):

        content_item = context["content_item"]

        step = content_item.step
        pipeline_result = None

        if step == "basic_info":
            pipeline_result = BasicInfoPipeline().run(context)
            next_step = "production_info"
            reply = "حالا اطلاعات فنی تولید را وارد کن."

        elif step == "production_info":
            pipeline_result = ProductionInfoPipeline().run(context)
            next_step = "keywords"
            reply = "حالا کلمات کلیدی را وارد کن."

        elif step == "keywords":
            pipeline_result = KeywordsPipeline().run(context)
            next_step = "research"
            reply = "دارم تحقیق کلیدواژه‌ها را انجام می‌دهم..."

        elif step == "research":
            pipeline_result = ResearchPipeline().run(context)
            next_step = "knowledge"
            reply = "اطلاعات فرم را کامل کن تا ساخت محتوا آغاز شود."

        elif step == "knowledge":
            pipeline_result = KnowledgePipeline().run(context)
            next_step = "approval"
            reply = "الان بررسی نهایی انجام می‌شود."

        elif step == "approval":
            pipeline_result = ApprovalPipeline().run(context)
            next_step = "completed"
            reply = "در حال تولید متن نهایی..."

        elif step == "completed":
            pipeline_result = FinalPipeline().run(context)
            reply = "✅ محتوا آماده شد!"

        else:
            reply = "مرحله‌ی نامشخص. لطفاً دوباره شروع کنید."

        # بروزرسانی مرحله
        if "content_item" in context and next_step:
            content_item.step = next_step
            content_item.save(update_fields=["step"])

        response = {
            "reply": reply,
            "step_index": self._get_step_index(step),
            "step_type": "form" if next_step else "output",
        }

        # مرکب از context pipeline
        if isinstance(pipeline_result, dict):
            response.update(pipeline_result)

        return response

    def _get_step_index(self, step):
        order = [
            "basic_info",
            "production_info",
            "keywords",
            "research",
            "knowledge",
            "approval",
            "completed",
        ]
        return order.index(step) + 1 if step in order else 0
