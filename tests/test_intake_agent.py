#import pytest

import asyncio
from agents.intake_agent import validate_claim


#@pytest.mark.asyncio
async def main():

    result = await validate_claim("C-2034")

    print(result.model_dump_json(indent=2))

    #assert result.claim_id == "C-2034"

if __name__ == "__main__":
    asyncio.run(main())