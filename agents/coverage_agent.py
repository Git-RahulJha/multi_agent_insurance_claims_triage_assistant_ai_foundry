import os
import asyncio
import json

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.agents import ChatCompletionAgent
from openai import AsyncOpenAI

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from tools.claim_tools import ClaimTools
from tools.policy_tools import PolicyTools
from tools.knowledge_tools import KnowledgeTools
from agents.models import CoverageAnalysis

load_dotenv()

# create_coverage_agent function creates and configures a Coverage and Anomaly Agent for analyzing insurance claims. It sets up the necessary services, plugins, and instructions for the agent to perform its tasks effectively.
def create_coverage_agent():
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

    kernel.add_plugin(ClaimTools(), plugin_name="ClaimTools")
    kernel.add_plugin(PolicyTools(), plugin_name="PolicyTools")
    kernel.add_plugin(KnowledgeTools(), plugin_name="KnowledgeTools")

    

    instructions = """
        You are the Coverage and Anomaly Agent for an insurance
        claims triage system.

        Your responsibility is to analyze insurance claims against
        their authoritative policy information and applicable
        underwriting knowledge.

        You MUST:

        1. Retrieve the claim using get_claim when a claim ID is provided.
        2. Retrieve the authoritative policy using get_policy.
        3. Use search_insurance_knowledge to retrieve relevant
        underwriting, coverage, and fraud rules.
        4. Do NOT invent policy facts.
        5. Do NOT hardcode underwriting rules.
        6. Use retrieved knowledge as evidence for anomaly detection.
        7. Check:
        - claim type coverage
        - loss date against policy period
        - claim amount against coverage limit
        - early-policy claim rules
        - near-limit claim rules
        - delayed reporting rules
        - other relevant retrieved fraud indicators
        8. Return a structured coverage analysis.
        9. If information is missing or contradictory, mark the
        relevant status as unknown and explain why.
        10. Do not automatically approve a claim merely because
            it appears covered.

        The final analysis must distinguish:
        - authoritative policy facts
        - retrieved underwriting rules
        - your reasoning
        """

    agent = ChatCompletionAgent(
        kernel=kernel,
        name="CoverageAnomalyAgent",
        instructions=instructions,
    )

    return agent

# analyze_claim function is an asynchronous function that uses the Coverage and Anomaly Agent to analyze a specific insurance claim based on its claim ID. It constructs a prompt with detailed instructions for the agent, invokes the agent to process the claim, and validates the final response against the CoverageAnalysis model.
async def analyze_claim(claim_id: str) -> CoverageAnalysis:
    agent = create_coverage_agent()

    prompt = f"""
        You are the Coverage and Anomaly Agent for an insurance
        claims triage system.

        Analyze the insurance claim with claim ID: {claim_id}.

        You MUST use get_claim with exactly this claim ID: {claim_id}.

        Your responsibility is to analyze insurance claims against
        their authoritative policy information and applicable
        underwriting knowledge.

        You MUST:

        1. Retrieve the claim using get_claim.
        2. Retrieve the authoritative policy using get_policy.
        3. Use search_insurance_knowledge to retrieve relevant
        underwriting, coverage, and fraud rules.
        4. Do NOT invent policy facts.
        5. Do NOT hardcode underwriting rules.
        6. Use retrieved knowledge as evidence for anomaly detection.
        7. Check:
        - claim type coverage
        - loss date against policy period
        - claim amount against coverage limit
        - early-policy claim rules
        - near-limit claim rules
        - delayed reporting rules
        - other relevant retrieved fraud indicators
        8. Return a structured coverage analysis.
        9. If information is missing or contradictory, use null
        for the affected boolean field.
        10. Do not automatically approve a claim merely because
            it appears covered.

        For these boolean fields:

        - claim_type_covered
        - within_policy_period
        - amount_within_limit

        use ONLY:

        - true
        - false
        - null

        Rules:

        - true = condition was evaluated and passed
        - false = condition was evaluated and failed
        - null = condition cannot be evaluated because required
        information is missing or unavailable

        NEVER return "unknown", "N/A", "not available", or another
        string for these boolean fields.

        For coverage_status use ONLY:

        - "covered"
        - "not_covered"
        - "unknown"

        IMPORTANT EVIDENCE FORMAT:

        The "evidence" field MUST be an array of JSON objects.

        Every evidence object MUST have exactly these fields:

        {{
            "source": "string",
            "details": "string | object | array"
        }}

        For example:

        {{
            "source": "authoritative_policy",
            "details": {{
                "policy_number": "POL-4410",
                "coverage_limit": 40000
            }}
        }}

        Do NOT return evidence as plain strings.

        Incorrect:

        "evidence": [
            "Policy POL-4410 covers fire"
        ]

        Correct:

        "evidence": [
            {{
                "source": "authoritative_policy",
                "details": "Policy POL-4410 covers fire"
            }}
        ]

        The evidence must be based only on information actually
        retrieved from tools or the knowledge base.

        The final response must contain ONLY valid JSON.
        Do not include markdown.
        Do not include ``` characters.
        Do not include explanatory text before or after the JSON.

        The final JSON must contain exactly:

        {{
            "claim_id": "string",
            "policy_number": "string",
            "coverage_status": "covered | not_covered | unknown",
            "claim_type_covered": true,
            "within_policy_period": true,
            "amount_within_limit": true,
            "anomaly_flags": [],
            "investigation_required": false,
            "evidence": [],
            "reasoning": "string"
        }}
        """

    response_parts = []

    async for response in agent.invoke(messages=prompt):
        if response.content:
            response_parts.append(str(response.content))

    raw_response = "".join(response_parts).strip()
    data = json.loads(raw_response)

    return CoverageAnalysis.model_validate(data)
