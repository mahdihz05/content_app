import requests


class TelegramAPI:

    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"

    def get_me(self):
        return requests.get(f"{self.base_url}/getMe").json()

    def get_updates(self):
        return requests.get(f"{self.base_url}/getUpdates").json()

    def send_message(self, chat_id, text):
        return requests.post(
            f"{self.base_url}/sendMessage",
            json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        ).json()

    def send_photo(self, chat_id, photo_url, caption=None):
        return requests.post(
            f"{self.base_url}/sendPhoto",
            json={"chat_id": chat_id, "photo": photo_url, "caption": caption or ""}
        ).json()

    def send_video(self, chat_id, video_url, caption=None):
        return requests.post(
            f"{self.base_url}/sendVideo",
            json={"chat_id": chat_id, "video": video_url, "caption": caption or ""}
        ).json()

    def delete_message(self, chat_id, message_id):
        return requests.post(
            f"{self.base_url}/deleteMessage",
            json={"chat_id": chat_id, "message_id": message_id}
        ).json()