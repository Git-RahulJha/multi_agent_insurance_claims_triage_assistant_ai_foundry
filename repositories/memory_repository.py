import json
import os


class MemoryRepository:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.path = os.path.join(base_dir, "data", "claim_memory.json")

    def _read(self) -> list[dict]:
        if not os.path.exists(self.path):
            return []

        with open(self.path, encoding="utf-8") as fh:
            return json.load(fh)

    def _write(self, memories: list[dict]) -> None:
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(memories, fh, indent=2)

    def get_memory(self, claim_id: str) -> list[dict]:
        memories = self._read()

        return [
            memory
            for memory in memories
            if memory.get("claim_id") == claim_id
        ]

    def save_memory(self, claim_id: str, memory_type: str, content: str, ) -> dict:
        memories = self._read()

        memory = {
            "claim_id": claim_id,
            "memory_type": memory_type,
            "content": content,
        }

        memories.append(memory)
        self._write(memories)

        return memory