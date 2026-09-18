import json
from pathlib import Path

class PolicyRepository:

    def __init__(self):
        data_path = (
            Path(__file__).parent.parent
            / "data"
            / "policy_coverage.json"
        )

        with open(data_path, encoding="utf-8") as file:
            self.policies = json.load(file)

    def get_policy(self, policy_number: str):
        for policy in self.policies:
            if policy["policy_number"] == policy_number:
                return policy

        return None