from typing import Annotated

from semantic_kernel.functions import kernel_function

from repositories.claim_repository import ClaimRepository


class ClaimTools:

    def __init__(self):
        self.repository = ClaimRepository()

    @kernel_function(
        name="get_claim",
        description="Retrieve the complete insurance claim using the claim ID.",
    )
    def get_claim(
        self,
        claim_id: Annotated[str, "The unique claim ID."]
    ) -> Annotated[str, "The claim record as JSON."]:

        claim = self.repository.claim(claim_id)

        if claim is None:
            return (
                f'{{"found": false, '
                f'"claim_id": "{claim_id}", '
                f'"error": "Claim not found"}}'
            )

        return str(claim)