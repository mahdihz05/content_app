class AutoReplyService:

    def __init__(self, platform, ai_service):
        self.platform = platform
        self.ai_service = ai_service

    def start(self):

        while True:

            messages = self.platform.listen_for_new_messages()

            for message in messages:

                ai_response = self.ai_service.generate_reply(
                    message.text
                )

                self.platform.reply_to_message(
                    ai_response
                )