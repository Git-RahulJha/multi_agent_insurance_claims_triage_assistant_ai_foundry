import pytest

from agents.supervisor_agent import (
    supervise_claim,
    resume_claim,
)


@pytest.mark.asyncio
async def test_hitl_resume():

    claim_id = "C-2034"

    # ---------------------------------------------------------
    # Start workflow
    # ---------------------------------------------------------

    state = await supervise_claim(claim_id)

    print("\n===== INITIAL STATE =====")
    print("Status:", state.status)
    print("Step:", state.current_step)
    print("Checkpoint:", state.checkpoint_required)
    print("Reason:", state.checkpoint_reason)

    assert state.status == "awaiting_human_review"
    assert state.checkpoint_required is True

    # ---------------------------------------------------------
    # Human approves continuation
    # ---------------------------------------------------------

    state = await resume_claim(
        state,
        human_decision="continue",
    )

    print("\n===== AFTER HUMAN REVIEW =====")
    print("Status:", state.status)
    print("Step:", state.current_step)

    if state.briefing:
        print("\n===== BRIEFING =====")
        print(
            state.briefing.model_dump_json(
                indent=2
            )
        )

    assert state.status == "completed"
    assert state.current_step == "completed"
    assert state.briefing is not None

@pytest.mark.asyncio
async def test_hitl_rejection():

    claim_id = "C-2034"

    state = await supervise_claim(claim_id)

    assert state.status == "awaiting_human_review"

    state = await resume_claim(
        state,
        human_decision="reject",
    )

    print("\n===== HUMAN REJECTION =====")
    print("Status:", state.status)
    print("Step:", state.current_step)
    print("Reason:", state.checkpoint_reason)

    assert state.status == "rejected_by_human"
    assert state.current_step == "human_rejected"
    assert state.briefing is None