from agents.supervisor_agent import (
    SupervisorState,
    supervise_claim,
)


async def process_claim(claim_id: str) -> SupervisorState:
    """
    Entry point for claim triage.

    The Supervisor controls the complete workflow.
    """
    return await supervise_claim(claim_id)