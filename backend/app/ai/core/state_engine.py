# ai/core/state_engine.py

class StateEngine:

    def next_step(self, current_state, user_message):
        """
        اینجا منطق تعیین مرحله بعد قرار می‌گیرد.
        """

        if current_state == "ask_name":
            return "ask_age"

        if current_state == "ask_age":
            return "completed"

        return "unknown"
