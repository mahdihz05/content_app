class ImagePipeline:
    def run(self, context: dict) -> dict:
        brain = context['brain']
        prompt = context['payload'].get('prompt', '')
        size = context['payload'].get('size', '1024x1024')

        if not prompt:
            return {"success": False, "message": "پرامپت تصویر خالی است"}

        image_url = brain.generate_image(prompt=prompt, size=size)

        # ذخیره در session memory
        memory = context.get('memory')
        session_id = context.get('session_id')
        if memory and session_id:
            memory.add_message(session_id, 'assistant', image_url)

        return {
            "success": True,
            "image_url": image_url,
            "message_type": "image"
        }
