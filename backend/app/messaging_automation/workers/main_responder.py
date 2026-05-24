from messaging_automation.platforms.bale import BalePlatform
from messaging_automation.ai.ai_service import AIService
from messaging_automation.workers.ai_responder import AIResponder


platform = BalePlatform(
    profile_path="profiles/bale_1"
)

platform.login()

ai_service = AIService()

responder = AIResponder(
    platform,
    ai_service
)

responder.start()