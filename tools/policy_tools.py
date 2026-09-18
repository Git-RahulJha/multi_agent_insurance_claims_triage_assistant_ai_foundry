from typing import Annotated

from semantic_kernel.functions import kernel_function

from repositories.policy_repository import PolicyRepository


class PolicyTools:

    def __init__(self):
        self.repository = PolicyRepository()

    @kernel_function(
        name="get_policy",
        description="Retrieve the authoritative policy coverage record.",
    )
    def get_policy(
        self,
        policy_number: Annotated[str, "The policy number."]
    ) -> Annotated[str, "The policy record as JSON."]:

        policy = self.repository.get_policy(policy_number)

        if policy is None:
            return (
                f'{{"found": false, '
                f'"policy_number": "{policy_number}", '
                f'"error": "Policy not found"}}'
            )

        return str(policy)