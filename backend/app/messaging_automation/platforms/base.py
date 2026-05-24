class BasePlatform:

    def login(self):
        raise NotImplementedError

    def send_message(self, user, text):
        raise NotImplementedError

    def get_unread_messages(self):
        raise NotImplementedError

    def reply_to_message(self, message, text):
        raise NotImplementedError