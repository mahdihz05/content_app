# ai/core/memory_manager.py

class MemoryManager:

    _memory_store = {}

    def get_memory(self, session_id):
        return self._memory_store.get(session_id, [])

    def add_message(self, session_id, role, content):
        self._memory_store.setdefault(session_id, []).append({
            "role": role,
            "content": content
        })
