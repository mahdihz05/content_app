# ai/services/ai_task_service.py

from ai.core.ai_manager import AIManager
from ai.prompts.research_prompts import ResearchPrompts


class AITaskService:

    async def generate_research(self, topic, user):
        system, user_prompt = ResearchPrompts.get_research_prompt(topic)

        ai = AIManager()

        result = await ai.brain.llm(
            system_prompt=system,
            user_prompt=user_prompt,
        )

        return result
