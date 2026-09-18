from azure.identity import DefaultAzureCredential

import asyncio

from orchestration.triage_workflow import process_claim
from agents.supervisor_agent import resume_claim


def authenticate():
    credential = DefaultAzureCredential()

    token = credential.get_token(
        "https://management.azure.com/.default"
    )

    print("Azure authentication successful")
    print(f"Token acquired: {token.token[:20]}...")

async def run():

    print("=" * 60)
    print("      INSURANCE CLAIMS TRIAGE ASSISTANT")
    print("=" * 60)

    claim_id = input("\nEnter Claim ID: ").strip()

    if not claim_id:
        print("Claim ID is required.")
        return

    # =========================================================
    # STEP 1: Start Supervisor
    # =========================================================

    print("\n[SUPERVISOR] Starting claim triage...")

    state = await process_claim(claim_id)

    print(
            f"[SUPERVISOR] Current step: "
            f"{state.current_step}"
        )

    if state.status == "failed":
        print("\n" + "=" * 60)
        print("                  WORKFLOW ERROR")
        print("=" * 60)

        if state.error:
            print(f"\nAgent: {state.error.agent}")
            print(f"Error type: {state.error.error_type}")
            print(f"Message: {state.error.message}")
            print(f"Recoverable: {state.error.recoverable}")

        return    

    # =========================================================
    # STEP 2: Display previous memory
    # =========================================================

    if state.previous_memory:

        print("\n[MEMORY] Previous memory found:")

        for memory in state.previous_memory:
            print(
                f"  - {memory['memory_type']}: "
                f"{memory['content']}"
            )

    else:

        print("\n[MEMORY] No previous memory found.")

    # =========================================================
    # STEP 3: Display Intake result
    # =========================================================

    print("\n[INTAKE AGENT]")

    if state.intake:

        print(f"  Valid: {state.intake.valid}")
        print(
            f"  Manual review: "
            f"{state.intake.requires_manual_review}"
        )

        if state.intake.missing_fields:
            print(
                "  Missing fields:",
                ", ".join(state.intake.missing_fields)
            )

        if state.intake.validation_errors:

            print("  Validation errors:")

            for error in state.intake.validation_errors:
                print(f"    - {error}")

    # =========================================================
    # STEP 4: Display Coverage result
    # =========================================================

    print("\n[COVERAGE & ANOMALY AGENT]")

    if state.coverage:

        print(
            f"  Coverage status: "
            f"{state.coverage.coverage_status}"
        )

        print(
            f"  Investigation required: "
            f"{state.coverage.investigation_required}"
        )

        if state.coverage.anomaly_flags:

            print("  Anomaly flags:")

            for flag in state.coverage.anomaly_flags:
                print(f"    - {flag}")

    # =========================================================
    # STEP 5: HITL checkpoint
    # =========================================================

    if state.status == "awaiting_human_review":

        print("\n" + "=" * 60)
        print("              HUMAN REVIEW REQUIRED")
        print("=" * 60)

        print(
            f"\nReason:\n{state.checkpoint_reason}"
        )

        print("\nAvailable actions:")
        print("  1. continue")
        print("  2. reject")

        decision = input(
            "\nEnter human decision: "
        ).strip().lower()

        if decision not in ["continue", "reject"]:

            print(
                "\nInvalid decision. "
                "Workflow remains paused."
            )

            return

        print(
            f"\n[SUPERVISOR] Human decision: "
            f"{decision}"
        )

        state = await resume_claim(
            state,
            human_decision=decision,
        )

    # =========================================================
    # STEP 6: Final result
    # =========================================================

    print("\n" + "=" * 60)
    print("                  FINAL RESULT")
    print("=" * 60)

    print(f"\nStatus: {state.status}")
    print(f"Current step: {state.current_step}")

    if state.briefing:

        print("\n[ADJUSTER BRIEFING]")

        print(
            f"\nSummary:\n"
            f"{state.briefing.summary}"
        )

        print("\nKey findings:")

        for finding in state.briefing.key_findings:
            print(f"  - {finding}")

        print(
            "\nRecommended action: "
            f"{state.briefing.recommended_action}"
        )

        if state.briefing.missing_information:

            print("\nMissing information:")

            for item in state.briefing.missing_information:
                print(f"  - {item}")

    if state.status == "rejected_by_human":

        print(
            "\nThe claim was rejected by the "
            "human reviewer."
        )


if __name__ == "__main__":
    asyncio.run(run())
