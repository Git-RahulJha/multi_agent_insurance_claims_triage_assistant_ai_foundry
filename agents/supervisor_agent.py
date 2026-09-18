from dataclasses import dataclass, field
from typing import Literal

from agents.intake_agent import validate_claim
from agents.coverage_agent import analyze_claim
from agents.briefing_agent import create_briefing

from agents.models import (
    IntakeValidation,
    CoverageAnalysis,
    AdjusterBriefing,
)

from repositories.memory_repository import MemoryRepository


@dataclass
class SupervisorState:
    claim_id: str

    current_step: str = "started"

    # Long-term memory loaded at the beginning
    previous_memory: list[dict] = field(default_factory=list)

    # Agent results
    intake: IntakeValidation | None = None
    coverage: CoverageAnalysis | None = None
    briefing: AdjusterBriefing | None = None

    # HITL
    checkpoint_required: bool = False
    checkpoint_reason: str | None = None

    # Workflow status
    status: Literal[
        "completed",
        "awaiting_human_review",
        "rejected_by_human",
        "failed",
    ] = "completed"


async def supervise_claim(claim_id: str) -> SupervisorState:
    """
    Start claim triage from the beginning.
    """

    state = SupervisorState(
        claim_id=claim_id,
        current_step="load_memory",
    )

    memory_repository = MemoryRepository()

    # =========================================================
    # STEP 1: Load persistent memory
    # =========================================================

    state.previous_memory = memory_repository.get_memory(
        claim_id
    )

    # =========================================================
    # STEP 2: Intake Agent
    # =========================================================

    state.current_step = "intake"

    try:
        state.intake = await validate_claim(
            claim_id
        )
    except Exception as exc:
        state.status = "failed"
        state.current_step = "intake_failed"
        state.checkpoint_reason = (
            f"Intake agent failed: {str(exc)}"
        )
        return state

    # =========================================================
    # STEP 3: Coverage & Anomaly Agent
    # =========================================================

    state.current_step = "coverage"

    try:
        state.coverage = await analyze_claim(
            claim_id
        )
    except Exception as exc:
        state.status = "failed"
        state.current_step = "coverage_failed"
        state.checkpoint_reason = (
            f"Coverage agent failed: {str(exc)}"
        )
        return state

    # =========================================================
    # STEP 4: HITL CHECKPOINT
    # =========================================================

    if (
        state.intake.requires_manual_review
        or state.coverage.investigation_required
    ):
        state.checkpoint_required = True
        state.status = "awaiting_human_review"
        state.current_step = "human_review_checkpoint"

        reasons = []

        if state.intake.requires_manual_review:
            reasons.append(
                "Intake validation requires manual review."
            )

        if state.coverage.investigation_required:
            reasons.append(
                "Coverage/anomaly analysis requires investigation."
            )

        state.checkpoint_reason = " ".join(reasons)

        return state

    # =========================================================
    # No HITL required → continue automatically
    # =========================================================

    return await _complete_after_review(state)


async def resume_claim(
    state: SupervisorState,
    human_decision: Literal[
        "continue",
        "reject",
    ],
) -> SupervisorState:
    """
    Resume a paused claim workflow after human review.
    """

    if state.status != "awaiting_human_review":
        raise ValueError(
            "Claim is not waiting for human review."
        )

    if human_decision == "reject":

        state.status = "rejected_by_human"
        state.current_step = "human_rejected"
        state.checkpoint_required = False
        state.checkpoint_reason = (
            "Human reviewer rejected the claim during checkpoint."
        )

        return state

    if human_decision == "continue":

        state.current_step = "human_review_completed"
        state.checkpoint_required = False
        state.checkpoint_reason = None

        return await _complete_after_review(state)

    raise ValueError(
        f"Unsupported human decision: {human_decision}"
    )


async def _complete_after_review(
    state: SupervisorState,
) -> SupervisorState:
    """
    Continue the workflow after the checkpoint
    or complete automatically when no checkpoint is required.
    """

    # =========================================================
    # STEP 5: Adjuster Briefing Agent
    # =========================================================

    state.current_step = "briefing"

    try:
        state.briefing = await create_briefing(
            claim_id=state.claim_id,
            intake_result=state.intake,
            coverage_result=state.coverage,
        )

    except Exception as exc:
        state.status = "failed"
        state.current_step = "briefing_failed"
        state.checkpoint_reason = (
            f"Briefing agent failed: {str(exc)}"
        )
        return state

    # =========================================================
    # STEP 6: Persist memory
    # =========================================================

    memory_repository = MemoryRepository()

    memory_repository.save_memory(
        claim_id=state.claim_id,
        memory_type="adjuster_briefing",
        content=state.briefing.summary,
    )

    # =========================================================
    # STEP 7: Complete
    # =========================================================

    state.current_step = "completed"
    state.status = "completed"

    return state