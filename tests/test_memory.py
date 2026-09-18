import pytest
from tools.memory_tools import MemoryTools


def test_memory():
    tools = MemoryTools()

    saved = tools.save_claim_memory(
        claim_id="C-2034",
        memory_type="adjuster_note",
        content="Loss date and amount are missing. Manual review required.",
    )

    print("\n===== SAVED MEMORY =====")
    print(saved)

    memory = tools.get_claim_memory("C-2034")

    print("\n===== RETRIEVED MEMORY =====")
    print(memory)

    #assert "C-2034" in memory
    #assert "Manual review required" in memory


test_memory()