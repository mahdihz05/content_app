from ai.pipelines.create_content.core import CreateContentCore
from ai.pipelines.chat_pipeline import ChatPipeline
from ai.pipelines.image_pipeline import ImagePipeline  # اضافه کن


class AIRouter:
    def __init__(self):
        self.pipelines = {
            "content": CreateContentCore(),
            "chat": ChatPipeline(),
            "image": ImagePipeline(),  # اضافه کن
        }

    def resolve(self, task_name):
        return self.pipelines.get(task_name)
