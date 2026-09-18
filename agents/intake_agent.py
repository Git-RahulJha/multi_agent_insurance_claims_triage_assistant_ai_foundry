import json
import os
from dotenv import load_dotenv

from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from agents.models import IntakeValidation
from tools.claim_tools import ClaimTools
from tools.policy_tools import PolicyTools

load_dotenv()

# function creates and configures an Intake and Validation Agent for insurance claims. It sets up the necessary services, plugins, and instructions for the agent to perform its tasks effectively.
def create_intake_agent() -> ChatCompletionAgent:

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

    kernel.add_plugin(
        ClaimTools(),
        plugin_name="claim_tools"
    )

    kernel.add_plugin(
        PolicyTools(),
        plugin_name="policy_tools"
    )

    return ChatCompletionAgent(
        kernel=kernel,
        name="IntakeValidationAgent",
        instructions="""
            You are the Intake & Validation Agent for an insurance claims triage system.

            Your responsibility is to validate the structural and basic business completeness
            of an insurance claim before downstream coverage analysis.

            For the supplied claim_id:

            1. Retrieve the claim using the claim tool.
            2. Retrieve the associated policy using the policy tool.
            3. Check whether the claim exists.
            4. Check whether the referenced policy exists.
            5. Check required claim information:
            - claim_id
            - policy_number
            - claim_type
            - loss_date
            - report_date
            - amount
            6. Check whether supporting documents are present.
            7. Identify obvious data inconsistencies.
            8. Do NOT determine whether the claim is covered.
            9. Do NOT invent missing values.
            10. Do NOT apply coverage or fraud rules that belong to the Coverage Agent.

            If information is missing, report it explicitly.

            Return ONLY valid JSON matching this structure:

            {
            "claim_id": "...",
            "valid": true,
            "missing_fields": [],
            "validation_errors": [],
            "warnings": [],
            "requires_manual_review": false,
            "evidence": [],
            "reasoning": "..."
            }

            Rules:

            - valid = false when critical claim/policy information is missing or invalid.
            - missing_fields contains fields that are absent or unusable.
            - validation_errors contains actual structural/data errors.
            - warnings contains non-blocking concerns.
            - requires_manual_review = true when the claim cannot safely proceed because
            critical information is missing or the policy cannot be found.
            - evidence must contain objects with "source" and "details".
            - Do not return markdown.
            - Do not return ```json fences.
            """
    )

#function validates an insurance claim by invoking the Intake and Validation Agent. It retrieves the claim and policy information, checks for required fields, and returns a structured validation result.
async def validate_claim(claim_id: str) -> IntakeValidation:
    agent = create_intake_agent()

    prompt = f"""
    Validate insurance claim {claim_id}.

    Return only the JSON structure specified in your instructions.
    """

    response_parts = []

    async for response in agent.invoke(messages=prompt):
        if response.content:
            response_parts.append(str(response.content))

    raw_response = "".join(response_parts).strip()

    data = json.loads(raw_response)

    return IntakeValidation.model_validate(data)