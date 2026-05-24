from ai.pipelines.create_content.base_pipeline import BasePipeline


class ChatPipeline(BasePipeline):
    def run(self, context):

        brain = context["brain"]

        user_input = context["payload"].get("message")
        memory = context["session_memory"] or []

        # ساخت prompt با حافظه
        dialog = ""
        for msg in memory:
            dialog += f"{msg['role']}: {msg['content']}\n"

        dialog += f"user: {user_input}\nassistant:"

        system_prompt = """
        You are an intelligent AI assistant. 
        Respond clearly, politely and helpfully.
        """

        response = brain.llm(
            system_prompt=system_prompt,
            user_prompt=dialog,
            model="gpt-4.1-mini"
        )

        # ذخیره درMemoryManager
        if context["session_id"]:
            context["memory"].add_message(context["session_id"], "assistant", response)

        return {"reply": response}
