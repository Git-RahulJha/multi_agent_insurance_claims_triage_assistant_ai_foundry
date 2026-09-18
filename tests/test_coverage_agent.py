import asyncio
import json

from agents.coverage_agent import analyze_claim


CLAIM_ID = "C-2034"


async def main():
    try:
        result = await analyze_claim("C-2031")
        
        print(result.model_dump_json(indent=2))
    except json.JSONDecodeError as exc:
        print("\nERROR: Final response is not valid JSON.")
        print(f"{type(exc).__name__}: {exc}")
        return



if __name__ == "__main__":
    asyncio.run(main())