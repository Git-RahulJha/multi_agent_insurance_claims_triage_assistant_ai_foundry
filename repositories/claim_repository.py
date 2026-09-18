import json
from pathlib import Path


class ClaimRepository:

    def __init__(self):
        data_path = (
            Path(__file__).parent.parent
            / "data"
            / "claims.json"
        )

        with open(data_path, encoding="utf-8") as file:
            self.claims = json.load(file)

    def claim(self, claim_id: str):
        for claim in self.claims:
            if claim["claim_id"] == claim_id:
                return claim

        return None