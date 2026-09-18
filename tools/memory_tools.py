from semantic_kernel.functions import kernel_function

from repositories.memory_repository import MemoryRepository


class MemoryTools:

    def __init__(self):
        self.repository = MemoryRepository()

    @kernel_function(
        name="get_claim_memory",
        description="Retrieve previously stored memory for a claim."
    )
    def get_claim_memory(self, claim_id: str) -> str:
        memories = self.repository.get_memory(claim_id)

        if not memories:
            return "No previous memory found for this claim."

        return "\n".join(
            f"{memory['memory_type']}: {memory['content']}"
            for memory in memories
        )

    @kernel_function(
        name="save_claim_memory",
        description="Persist important information about a claim for future interactions."
    )
    def save_claim_memory(
        self,
        claim_id: str,
        memory_type: str,
        content: str,
    ) -> str:

        memory = self.repository.save_memory(
            claim_id=claim_id,
            memory_type=memory_type,
            content=content,
        )

        return (
            f"Memory saved for claim {claim_id}: "
            f"{memory['memory_type']} - {memory['content']}"
        )