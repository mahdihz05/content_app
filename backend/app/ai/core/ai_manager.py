from ai.core.brain import AIBrain
from ai.core.context_manager import ContextManager
from ai.core.memory_manager import MemoryManager
from ai.core.router import AIRouter


class AIManager:
    def __init__(self):
        self.brain = AIBrain()
        self.context_manager = ContextManager()
        self.memory_manager = MemoryManager()
        self.router = AIRouter()

    def run_task(self, user, task_name, payload=None, session_id=None):
        payload = payload or {}

        # Context‌ها
        user_context = self.context_manager.get_user_context(user)
        session_memory = (
            self.memory_manager.get_memory(session_id)
            if session_id else None
        )

        # Pipeline
        pipeline = self.router.resolve(task_name)
        if not pipeline:
            raise ValueError(f"No pipeline found for task: {task_name}")

        # ساخت context
        context = {
            "user": user,
            "task_name": task_name,
            "payload": payload,
            "user_context": user_context,
            "session_memory": session_memory,
            "session_id": session_id,
            "brain": self.brain,
            "memory": self.memory_manager,
        }

        if "content_item" in payload:
            context["content_item"] = payload["content_item"]

        # اجرای pipeline
        return pipeline.run(context)
