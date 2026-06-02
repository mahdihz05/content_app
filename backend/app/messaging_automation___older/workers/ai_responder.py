import time


class AIResponder:

    def __init__(self, platform, ai_service):

        self.platform = platform
        self.ai_service = ai_service

    def start(self):

        print("=" * 50)
        print("START AI RESPONDER")
        print("=" * 50)

        while True:

            try:

                messages = self.platform.get_unread_messages()

                for msg in messages:

                    print("NEW MESSAGE:", msg)

                    answer = self.ai_service.generate_reply(
                        msg["text"]
                    )

                    self.platform.reply_to_message(
                        msg,
                        answer
                    )

                    print("REPLY SENT")

            except Exception as e:

                print("RESPONDER ERROR")
                print(str(e))

            time.sleep(5)