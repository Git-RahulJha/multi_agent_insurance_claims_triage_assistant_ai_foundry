import pytest

from orchestration.triage_workflow import process_claim


@pytest.mark.asyncio
async def test_process_claim():

    claim_id = "C-2034"

    result = await process_claim(claim_id)

    print("\n===== WORKFLOW STATUS =====")
    print(result.status)

    print("\n===== CURRENT STEP =====")
    print(result.current_step)

    print("\n===== PREVIOUS MEMORY =====")
    print(result.previous_memory)

    print("\n===== CHECKPOINT =====")
    print("Required:", result.checkpoint_required)
    print("Reason:", result.checkpoint_reason)

    print("\n===== INTAKE =====")

    if result.intake:
        print(result.intake.model_dump_json(indent=2))

    print("\n===== COVERAGE =====")

    if result.coverage:
        print(result.coverage.model_dump_json(indent=2))

    print("\n===== BRIEFING =====")

    if result.briefing:
        print(result.briefing.model_dump_json(indent=2))

    assert result.claim_id == claim_id
    assert result.intake is not None
    assert result.coverage is not None