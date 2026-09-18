import pytest

from agents.intake_agent import validate_claim
from agents.coverage_agent import analyze_claim
from agents.briefing_agent import create_briefing


@pytest.mark.asyncio
async def test_briefing_agent():

    claim_id = "C-2034"

    # Run Agent 1
    intake_result = await validate_claim(
        claim_id
    )

    # Run Agent 2
    coverage_result = await analyze_claim(
        claim_id
    )

    # Run Agent 3
    briefing = await create_briefing(
        claim_id=claim_id,
        intake_result=intake_result,
        coverage_result=coverage_result,
    )

    print("\n===== ADJUSTER BRIEFING =====")

    print(
        briefing.model_dump_json(
            indent=2
        )
    )

    assert briefing.claim_id == claim_id

    assert briefing.summary

    assert briefing.recommended_action in [
        "approve",
        "reject",
        "request_more_information",
        "manual_review",
    ]