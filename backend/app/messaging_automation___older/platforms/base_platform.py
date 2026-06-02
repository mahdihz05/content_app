class BasePlatform:

    def connect(self):
        raise NotImplementedError

    def send_message(
        self,
        recipient,
        message,
        attachment=None
    ):
        raise NotImplementedError

    def listen_for_new_messages(self):
        raise NotImplementedError

    def reply_to_message(
        self,
        message
    ):
        raise NotImplementedError