import time


class BulkSender:

    def __init__(self, platform):

        self.platform = platform

    def start(
            self,
            users,
            text,
            delay=5
    ):

        print("=" * 50)
        print("START BULK SENDER")
        print("=" * 50)

        for user in users:

            try:

                print(f"SEND TO -> {user}")

                self.platform.send_message(
                    user,
                    text
                )

                print(f"SUCCESS -> {user}")

            except Exception as e:

                print(f"ERROR -> {user}")
                print(str(e))

            print(f"WAIT {delay} SEC")

            time.sleep(delay)

        print("BULK FINISHED")