import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI

from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from agents.models import AdjusterBriefing, IntakeValidation, CoverageAnalysis


load_dotenv()

# function creates and configures an Adjuster Briefing Agent for synthesizing the results of the Intake & Validation Agent and the Coverage & Anomaly Agent. It sets up the necessary services and instructions for the agent to produce a structured briefing for insurance adjusters.
def create_briefing_agent() -> ChatCompletionAgent:

    kernel = Kernel()

    client = AsyncOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        base_url=os.getenv("AZURE_OPENAI_ENDPOINT"),
    )

    kernel.add_service(
        OpenAIChatCompletion(
            ai_model_id=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT"),
            async_client=client,
        )
    )

    return ChatCompletionAgent(
        kernel=kernel,
        name="AdjusterBriefingAgent",
        instructions="""
            You are the Adjuster Briefing Agent in an insurance claims triage system.

            Your responsibility is to synthesize the results produced by:

            1. Intake & Validation Agent
            2. Coverage & Anomaly Agent

            Create a concise, factual briefing for a human insurance adjuster.

            IMPORTANT RULES:

            1. Use only the information provided in the agent results.
            2. Do not invent claim, policy, coverage, amount, date, or document information.
            3. Do not independently perform new coverage analysis.
            4. Do not override the findings of the previous agents.
            5. Clearly identify missing information.
            6. Clearly identify reasons why investigation or human review is required.
            7. If critical information is missing, do not recommend automatic approval.
            8. If the coverage result is "unknown", do not recommend automatic approval.
            9. The recommended_action must be exactly one of:
            - "approve"
            - "reject"
            - "request_more_information"
            - "manual_review"

            Recommended action guidance:

            - Use "approve" only when the supplied results clearly support automatic approval
            and there are no unresolved critical issues.
            - Use "reject" only when the supplied results clearly establish that the claim
            should be rejected.
            - Use "request_more_information" when the primary issue is missing information
            that the claimant can reasonably provide.
            - Use "manual_review" when investigation is required, coverage is unknown,
            or the supplied information requires an adjuster's judgment.

            The briefing must distinguish facts from recommendations.

            Return ONLY valid JSON.

            Do not use markdown.
            Do not use ```json fences.

            Required JSON structure:

            {
            "claim_id": "string",
            "summary": "string",
            "key_findings": [],
            "missing_information": [],
            "investigation_reasons": [],
            "recommended_action": "approve|reject|request_more_information|manual_review",
            "supporting_evidence": [],
            "reasoning": "string"
            }

            Each supporting_evidence item must contain:

            {
            "source": "string",
            "details": {}
            }
            """,
    )

# method creates an adjuster briefing by invoking the Adjuster Briefing Agent. It takes the claim ID, intake validation result, and coverage analysis result as input, and returns a structured briefing for the insurance adjuster.
async def create_briefing(
    claim_id: str,
    intake_result: IntakeValidation,
    coverage_result: CoverageAnalysis,
) -> AdjusterBriefing:

    agent = create_briefing_agent()

    prompt = f"""
        Create an adjuster briefing for insurance claim {claim_id}.

        INTAKE & VALIDATION RESULT:

        {intake_result.model_dump_json(indent=2)}


        COVERAGE & ANOMALY RESULT:

        {coverage_result.model_dump_json(indent=2)}


        Use these results to create the final adjuster briefing.

        Return ONLY valid JSON matching the required structure.
        """

    response_parts = []

    async for response in agent.invoke(messages=prompt):
        if response.content:
            response_parts.append(str(response.content))

    raw_response = "".join(response_parts).strip()

    data = json.loads(raw_response)

    return AdjusterBriefing.model_validate(data)