import logging
from dataclasses import dataclass, field
from typing import Literal

from agents.intake_agent import validate_claim
from agents.coverage_agent import analyze_claim
from agents.briefing_agent import create_briefing

from agents.models import AgentError, IntakeValidation, CoverageAnalysis, AdjusterBriefing
from repositories.memory_repository import MemoryRepository


# =============================================================
# Logging
# =============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("claims.supervisor")

# =============================================================
# Constants
# =============================================================

AGENT_TIMEOUT_SECONDS = 60

# =============================================================
# Workflow State
# =============================================================

@dataclass
class SupervisorState:
    claim_id: str

    current_step: str = "started"

    # Long-term memory
    previous_memory: list[dict] = field(default_factory=list)

    # Agent results
    intake: IntakeValidation | None = None
    coverage: CoverageAnalysis | None = None
    briefing: AdjusterBriefing | None = None

    # HITL
    checkpoint_required: bool = False
    checkpoint_reason: str | None = None

    # Error
    error: AgentError | None = None

    # Workflow status
    status: Literal[
        "completed",
        "awaiting_human_review",
        "rejected_by_human",
        "failed",
    ] = "completed"


# =============================================================
# Supervisor
# =============================================================

async def supervise_claim(claim_id: str) -> SupervisorState:

    state = SupervisorState(
        claim_id=claim_id,
        current_step="load_memory",
    )

    logger.info("Starting claim triage | claim_id=%s",claim_id)

    memory_repository = MemoryRepository()

    # =========================================================
    # STEP 1: Load Memory
    # =========================================================

    logger.info("Loading persistent memory | claim_id=%s", claim_id )

    try:
        state.previous_memory = (memory_repository.get_memory(claim_id))

    except Exception as exc:

        return _fail(
            state,
            agent="memory_repository",
            error_type="memory_load_error",
            message=str(exc),
        )

    # =========================================================
    # STEP 2: Intake Agent
    # =========================================================

    state.current_step = "intake"

    logger.info(
        "Executing Intake Agent | claim_id=%s",
        claim_id,
    )

    try:

        state.intake = await _run_with_timeout(
            validate_claim(claim_id)
        )

    except TimeoutError as exc:

        return _fail(
            state,
            agent="intake_agent",
            error_type="timeout",
            message=str(exc),
            recoverable=True,
        )

    except Exception as exc:

        return _fail(
            state,
            agent="intake_agent",
            error_type="execution_error",
            message=str(exc),
        )

    # =========================================================
    # STEP 3: Coverage Agent
    # =========================================================

    state.current_step = "coverage"

    logger.info(
        "Executing Coverage Agent | claim_id=%s",
        claim_id,
    )

    try:

        state.coverage = await _run_with_timeout(
            analyze_claim(claim_id)
        )

    except TimeoutError as exc:

        return _fail(
            state,
            agent="coverage_agent",
            error_type="timeout",
            message=str(exc),
            recoverable=True,
        )

    except Exception as exc:

        return _fail(
            state,
            agent="coverage_agent",
            error_type="execution_error",
            message=str(exc),
        )

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

        logger.warning(
            "HITL checkpoint reached | claim_id=%s | reason=%s",
            claim_id,
            state.checkpoint_reason,
        )

        return state

    # =========================================================
    # No HITL → Continue
    # =========================================================

    return await _complete_after_review(state)


# =============================================================
# Resume after HITL
# =============================================================

async def resume_claim(
    state: SupervisorState,
    human_decision: Literal[
        "continue",
        "reject",
    ],
) -> SupervisorState:

    if state.status != "awaiting_human_review":

        raise ValueError(
            "Claim is not waiting for human review."
        )

    logger.info(
        "Human decision received | claim_id=%s | decision=%s",
        state.claim_id,
        human_decision,
    )

    if human_decision == "reject":

        state.status = "rejected_by_human"
        state.current_step = "human_rejected"
        state.checkpoint_required = False
        state.checkpoint_reason = (
            "Human reviewer rejected the claim "
            "during checkpoint."
        )

        logger.info(
            "Claim rejected by human | claim_id=%s",
            state.claim_id,
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


# =============================================================
# Complete workflow
# =============================================================

async def _complete_after_review(
    state: SupervisorState,
) -> SupervisorState:

    # =========================================================
    # STEP 5: Briefing Agent
    # =========================================================

    state.current_step = "briefing"

    logger.info(
        "Executing Briefing Agent | claim_id=%s",
        state.claim_id,
    )

    try:

        state.briefing = await _run_with_timeout(
            create_briefing(
                claim_id=state.claim_id,
                intake_result=state.intake,
                coverage_result=state.coverage,
            )
        )

    except TimeoutError as exc:

        return _fail(
            state,
            agent="briefing_agent",
            error_type="timeout",
            message=str(exc),
            recoverable=True,
        )

    except Exception as exc:

        return _fail(
            state,
            agent="briefing_agent",
            error_type="execution_error",
            message=str(exc),
        )

    # =========================================================
    # STEP 6: Persist Memory
    # =========================================================

    logger.info(
        "Saving persistent memory | claim_id=%s",
        state.claim_id,
    )

    try:

        memory_repository = MemoryRepository()

        memory_repository.save_memory(
            claim_id=state.claim_id,
            memory_type="adjuster_briefing",
            content=state.briefing.summary,
        )

    except Exception as exc:

        return _fail(
            state,
            agent="memory_repository",
            error_type="memory_save_error",
            message=str(exc),
        )

    # =========================================================
    # STEP 7: Complete
    # =========================================================

    state.current_step = "completed"
    state.status = "completed"

    logger.info(
        "Claim triage completed | claim_id=%s",
        state.claim_id,
    )

    return state


# =============================================================
# Timeout helper
# =============================================================

async def _run_with_timeout(coroutine):

    import asyncio

    try:

        return await asyncio.wait_for(
            coroutine,
            timeout=AGENT_TIMEOUT_SECONDS,
        )

    except asyncio.TimeoutError:

        raise TimeoutError(
            f"Agent execution exceeded "
            f"{AGENT_TIMEOUT_SECONDS} seconds."
        )


# =============================================================
# Error helper
# =============================================================

def _fail(
    state: SupervisorState,
    agent: str,
    error_type: str,
    message: str,
    recoverable: bool = False,
) -> SupervisorState:

    state.status = "failed"
    state.current_step = f"{agent}_failed"

    state.error = AgentError(
        agent=agent,
        error_type=error_type,
        message=message,
        recoverable=recoverable,
    )

    logger.error(
        "Workflow failed | claim_id=%s | agent=%s | "
        "error_type=%s | message=%s",
        state.claim_id,
        agent,
        error_type,
        message,
    )

    return state