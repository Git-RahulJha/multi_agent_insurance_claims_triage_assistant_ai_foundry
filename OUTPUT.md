#To view end-to-end result, check all the way down to this document.

Intake agent output:

claim C-2034

{
  "claim_id": "C-2034",
  "valid": false,
  "missing_fields": [
    "loss_date",
    "amount",
    "supporting_documents"
  ],
  "validation_errors": [
    "loss_date is empty/unset",
    "amount is zero or not provided (required positive numeric value)",
    "report_date (2026-08-20) is after policy expiration_date (2026-01-01) — possible policy lapse or date entry error"
  ],
  "warnings": [
    "Claim description explicitly states loss date and claim amount are missing",
    "No documents attached to the claim record"
  ],
  "requires_manual_review": true,
  "evidence": [
    {
      "source": "claim_record",
      "details": "claim_id=C-2034, policy_number=POL-4410, claim_type=fire, loss_date='', report_date=2026-08-20, amount=0, description='Fire damage reported, but loss date and claim amount are missing.', documents=[]"
    },
    {
      "source": "policy_record",
      "details": "policy_number=POL-4410, policy_type=homeowners, effective_date=2024-01-01, expiration_date=2026-01-01, coverage_limit=40000, covered_claim_types=['water_damage','fire','theft']"
    }
  ],
  "reasoning": "The claim and referenced policy were found. Critical claim fields (loss_date and amount) are missing/unusable and supporting documents are absent, which prevents safe automated processing. Additionally, the claim's report_date is after the policy expiration_date, indicating a date inconsistency that requires clarification. Because of the missing critical information and the date inconsistency, the claim is not valid for automated intake and requires manual review. No coverage determination was made."
}


Coverage agent output:

claim C-2031

{
  "claim_id": "C-2031",
  "policy_number": "POL-5521",
  "coverage_status": "covered",
  "claim_type_covered": true,
  "within_policy_period": true,
  "amount_within_limit": true,
  "anomaly_flags": [],
  "investigation_required": false,
  "evidence": [
    {
      "source": "authoritative_policy",
      "details": {
        "policy_number": "POL-5521",
        "policy_type": "homeowners",
        "coverage_limit": 50000,
        "effective_date": "2025-01-01",
        "expiration_date": "2026-12-31",
        "covered_claim_types": [
          "water_damage",
          "fire",
          "theft"
        ]
      }
    },
    {
      "source": "authoritative_claim",
      "details": {
        "claim_id": "C-2031",
        "claim_type": "water_damage",
        "loss_date": "2026-08-15",
        "report_date": "2026-08-16",
        "amount": 8500,
        "description": "Pipe burst caused water damage.",
        "documents": [
          "repair_estimate.pdf",
          "damage_photos.zip"
        ]
      }
    },
    {
      "source": "underwriting_rules.md",
      "details": {
        "early_policy_claims": "Claims filed within 7 days of the policy inception date should be flagged for additional review.",
        "near_policy_limit": "Claims whose requested amount is within 2% of the applicable policy coverage limit should be flagged for investigator review.",
        "excessive_claim_amount": "A claim amount greater than the applicable policy coverage limit cannot be automatically approved.",
        "policy_period_requirement": "The loss date must fall within the policy period."
      }
    },
    {
      "source": "coverage_guidelines.md",
      "details": {
        "property_claims": "Homeowners policies may cover property damage caused by covered events such as water damage when the event is within the policy coverage period and applicable coverage exists.",
        "coverage_limit_note": "The requested claim amount must not exceed theapplicable policy coverage limit for automatic approval.",
        "water_damage_note": "Water damage claims should be checked against the property's applicable water damage coverage."
      }
    }
  ],
  "reasoning": "Authoritative policy POL-5521 explicitly lists water_damage asa covered claim type and shows an active policy period from 2025-01-01 to 2026-12-31. The claim loss date (2026-08-15) falls within that period and the reported amount ($8,500) is below the policy coverage limit ($50,000). Retrieved underwriting rules flag claims within 7 days of inception and claims within 2% of the coverage limit for additional review; neither condition applies here (loss date is well after inception and amount is far below the 2% threshold). Reporting occurred one day after loss, consistent with prompt reporting. No evidence from the authoritative records or retrieved rules indicates the claim is excluded or requires investigation, so coverage_status is assessed as covered. Investigation is not required based on the available facts and retrieved underwriting/fraud indicators."
}

claim-2033

| Check         | Result         | Reason                             |
| ------------- | -------------- | ---------------------------------- |
| Claim type    | ✅ Covered      | `theft` is in policy               |
| Policy period | ✅ Valid        | 2026-08-30 is between policy dates |
| Amount        | ✅ Within limit | ₹25,000 = ₹25,000 limit            |
| Early claim   | ⚠️ Flag        | 3 days after inception             |
| Near limit    | ⚠️ Flag        | Amount is within 2% of limit       |
| Investigation | ⚠️ Required    | Multiple anomaly indicators        |


Raw response:
{
    "claim_id": "C-2033",
    "policy_number": "POL-9981",
    "coverage_status": "covered",
    "claim_type_covered": true,
    "within_policy_period": true,
    "amount_within_limit": true,
    "anomaly_flags": [
        "early_policy_claim",
        "near_limit_amount",
        "missing_supporting_documents",
        "delayed_reporting_uncertain"
    ],
    "investigation_required": true,
    "evidence": [
        "Authoritative policy: policy_number POL-9981, policy_type homeowners,coverage_limit 25000, effective_date 2026-08-27, expiration_date 2027-08-27, covered_claim_types ['water_damage','fire','theft'].",
        "Authoritative claim: claim_id C-2033, claim_type theft, loss_date 2026-08-30, report_date 2026-09-02, amount 25000, description 'Jewelry theft'.",
        "Underwriting rule (underwriting_rules.md): 'Claims filed within 7 days of the policy inception date should be flagged for additional review.'",
        "Underwriting rule (underwriting_rules.md): 'Claims whose requested amount is within 2% of the applicable policy coverage limit should be flagged forinvestigator review.'",
        "Fraud indicator (fraud_indicator_patterns.md): 'A significant delay between the loss date and claim report' (delayed reporting is a fraud indicator).",
        "Coverage guideline (coverage_guidelines.md): 'Theft claims ... may require additional documentation such as a police report or inventory of stolen property.'"
    ],
    "reasoning": "Authoritative policy facts show this is a homeowners policy (POL-9981) that includes 'theft' in covered_claim_types, the loss date (2026-08-30) falls between the effective (2026-08-27) and expiration (2027-08-27) dates, and the claimed amount (25000) equals the policy coverage_limit (25000). Therefore, on the facts available the claim is within the policy period, the claim type is covered, and the amount does not exceed the limit (coverage_status: covered). Retrieved underwriting rules and fraud indicators identify multiple anomalies requiring investigation: the loss occurred 3 days after policy inception which matches the 'within 7 days' early-claim rule (flag: early_policy_claim); the claim amount equals the policy limit and is within the 'within 2%' near-limit rule (flag: near_limit_amount); theft claims typically require supporting documentation such as a police report, which is not present in the claim record (flag: missing_supporting_documents). There is a 3-day gap between loss and report; knowledge indicates delayed reporting can be an indicator but the retrievedsources do not provide a firm numeric threshold for 'significant delay', so the significance of the 3-day delay is uncertain (flag: delayed_reporting_uncertain). Given these anomaly indicators and missing supporting documentation, an investigator review is required. This analysis identifies coverage applicability but does not constitute claim approval."
}

Validated CoverageAnalysis:
{
  "claim_id": "C-2033",
  "policy_number": "POL-9981",
  "coverage_status": "covered",
  "claim_type_covered": true,
  "within_policy_period": true,
  "amount_within_limit": true,
  "anomaly_flags": [
    "early_policy_claim",
    "near_limit_amount",
    "missing_supporting_documents",
    "delayed_reporting_uncertain"
  ],
  "investigation_required": true,
  "evidence": [
    "Authoritative policy: policy_number POL-9981, policy_type homeowners, coverage_limit 25000, effective_date 2026-08-27, expiration_date 2027-08-27, covered_claim_types ['water_damage','fire','theft'].",
    "Authoritative claim: claim_id C-2033, claim_type theft, loss_date 2026-08-30, report_date 2026-09-02, amount 25000, description 'Jewelry theft'.",
    "Underwriting rule (underwriting_rules.md): 'Claims filed within 7 days ofthe policy inception date should be flagged for additional review.'",
    "Underwriting rule (underwriting_rules.md): 'Claims whose requested amountis within 2% of the applicable policy coverage limit should be flagged for investigator review.'",
    "Fraud indicator (fraud_indicator_patterns.md): 'A significant delay between the loss date and claim report' (delayed reporting is a fraud indicator).",
    "Coverage guideline (coverage_guidelines.md): 'Theft claims ... may require additional documentation such as a police report or inventory of stolen property.'"
  ],
  "reasoning": "Authoritative policy facts show this is a homeowners policy (POL-9981) that includes 'theft' in covered_claim_types, the loss date (2026-08-30) falls between the effective (2026-08-27) and expiration (2027-08-27) dates, and the claimed amount (25000) equals the policy coverage_limit (25000). Therefore, on the facts available the claim is within the policy period, the claim type is covered, and the amount does not exceed the limit (coverage_status: covered). Retrieved underwriting rules and fraud indicators identify multiple anomalies requiring investigation: the loss occurred 3 days after policy inception which matches the 'within 7 days' early-claim rule (flag: early_policy_claim); the claim amount equals the policy limit and is within the 'within 2%' near-limitrule (flag: near_limit_amount); theft claims typically require supporting documentation such as a police report, which is not present in the claim record (flag: missing_supporting_documents). There is a 3-day gap between loss and report; knowledge indicates delayed reporting can be an indicator but the retrieved sources do not provide a firm numeric threshold for 'significant delay', so the significance of the 3-day delay is uncertain (flag: delayed_reporting_uncertain). Given these anomaly indicators and missing supporting documentation, an investigator review is required. This analysis identifies coverage applicability but does not constitute claim approval."
}

Claim c-2034

{
  "claim_id": "C-2034",
  "policy_number": "POL-4410",
  "coverage_status": "unknown",
  "claim_type_covered": true,
  "within_policy_period": null,
  "amount_within_limit": null,
  "anomaly_flags": [
    "missing_loss_date",
    "missing_claim_amount",
    "claim_reported_after_policy_expiration",
    "no_supporting_documents",
    "missing_critical_information"
  ],
  "investigation_required": true,
  "evidence": [
    {
      "source": "authoritative_policy",
      "details": {
        "policy_number": "POL-4410",
        "policy_type": "homeowners",
        "coverage_limit": 40000,
        "effective_date": "2024-01-01",
        "expiration_date": "2026-01-01",
        "covered_claim_types": [
          "water_damage",
          "fire",
          "theft"
        ]
      }
    },
    {
      "source": "claim",
      "details": {
        "claim_id": "C-2034",
        "claim_type": "fire",
        "loss_date": "",
        "report_date": "2026-08-20",
        "amount": 0,
        "description": "Fire damage reported, but loss date and claim amount are missing.",
        "documents": []
      }
    },
    {
      "source": "underwriting_rules",
      "details": [
        "Claims missing required information such as policy number, claim ID, loss date, claim amount, or claim type must not be automatically approved.",
        "Claims filed within 7 days of the policy inception date should be flagged for additional review.",
        "Claims whose requested amount is within 2% of the applicable policy coverage limit should be flagged for investigator review.",
        "The loss date must fall within the policy effective period."
      ]
    },
    {
      "source": "fraud_indicator_patterns",
      "details": [
        "Missing loss dates, amounts, policy information, or supporting documents should trigger additional review.",
        "A significant delay between the loss date and claim report may require additional investigation.",
        "A claim submitted shortly after policy inception may require additional investigation.",
        "A claim amount very close to the policy limit is an investigation indicator."
      ]
    },
    {
      "source": "combined_retrieved_facts",
      "details": {
        "policy_expiration_date": "2026-01-01",
        "claim_report_date": "2026-08-20",
        "note": "Claim report date is after policy expiration date (derived from authoritative_policy and claim)."
      }
    }
  ],
  "reasoning": "Authoritative policy POL-4410 lists 'fire' as a covered claim type and has a coverage limit of 40000, so claim_type_covered is true. However the claim is missing the loss_date and the claim amount (claim record shows empty loss_date and description states amount missing), so within_policy_period and amount_within_limit cannot be evaluated and are set to null. Retrieved underwriting rules and fraud patterns state that missing critical information, delayed reporting, and claims reported shortly after policy events require review; the claim's report_date (2026-08-20) is after the policy expiration (2026-01-01),creating an additional anomaly that requires investigation. Because required facts to determine coverage (loss date and amount, and whether loss occurred during the policy period) are missing, the overall coverage_status is set to 'unknown' and the claim should be investigated further rather than approved."
}

Explaination:
coverage_status = "unknown" because required facts are missing.
claim_type_covered = true because fire is covered by POL-4410.
within_policy_period = null because loss_date is missing.
amount_within_limit = null because the amount is missing/ambiguous.
investigation_required = true.
Evidence contains both authoritative repository data and Azure AI Search knowledge.
The derived combined_retrieved_facts is useful because it explicitly shows how the report-date anomaly was derived.




Workflow output

Claim C-2034


===== INTAKE =====
{
  "claim_id": "C-2034",
  "valid": false,
  "missing_fields": [
    "loss_date",
    "amount",
    "documents"
  ],
  "validation_errors": [
    "loss_date is empty or not provided",
    "amount is 0 (missing or not provided)",
    "report_date (2026-08-20) is after policy expiration_date (2026-01-01) — temporal inconsistency between claim report and policy term"
  ],
  "warnings": [
    "No supporting documents attached to the claim (documents array is empty)",
    "Claim description explicitly notes missing loss date and claim amount"
  ],
  "requires_manual_review": true,
  "evidence": [
    {
      "source": "claim_record",
      "details": "claim_id=C-2034, policy_number=POL-4410, claim_type=fire, loss_date='', report_date=2026-08-20, amount=0, description='Fire damage reported, but loss date and claim amount are missing.', documents=[]"
    },
    {
      "source": "policy_record",
      "details": "policy_number=POL-4410, policy_type=homeowners, effective_date=2024-01-01, expiration_date=2026-01-01, coverage_limit=40000, covered_claim_types=['water_damage','fire','theft']"
    }
  ],
  "reasoning": "Claim C-2034 and referenced policy POL-4410 were retrieved. Required claim fields checked: claim_id, policy_number, claim_type, loss_date, report_date, amount. Claim_id, policy_number, claim_type, and report_date are present. loss_date and amount are missing/empty (amount=0), and there are no supporting documents. Policy POL-4410 exists, but its expiration_date (2026-01-01) is before the claim report_date (2026-08-20), a temporal inconsistency that prevents safe automated progression. Because critical required claim information ismissing and there is a policy-term/date inconsistency, the claim is not valid for automated downstream processing and requires manual review. No coverage or fraud determinations were made."
}

===== COVERAGE =====
{
  "claim_id": "C-2034",
  "policy_number": "POL-4410",
  "coverage_status": "unknown",
  "claim_type_covered": true,
  "within_policy_period": null,
  "amount_within_limit": null,
  "anomaly_flags": [
    "missing_loss_date",
    "missing_claim_amount",
    "report_date_after_policy_expiration",
    "missing_supporting_documents"
  ],
  "investigation_required": true,
  "evidence": [
    {
      "source": "authoritative_policy",
      "details": {
        "policy_number": "POL-4410",
        "policy_type": "homeowners",
        "coverage_limit": 40000,
        "effective_date": "2024-01-01",
        "expiration_date": "2026-01-01",
        "covered_claim_types": [
          "water_damage",
          "fire",
          "theft"
        ]
      }
    },
    {
      "source": "claim_record",
      "details": {
        "claim_id": "C-2034",
        "claim_type": "fire",
        "loss_date": "",
        "report_date": "2026-08-20",
        "amount": 0,
        "description": "Fire damage reported, but loss date and claim amount are missing.",
        "documents": []
      }
    },
    {
      "source": "underwriting_knowledge",
      "details": [
        {
          "rule": "Early Policy Claims",
          "summary": "Claims filed within 7 days of the policy inception date should be flagged for additional review."
        },
        {
          "rule": "Near Policy Limit",
          "summary": "Claims whose requested amount is within 2% of the applicable policy coverage limit should be flagged for investigator review."
        },
        {
          "rule": "Policy Period",
          "summary": "The loss date must fall within the policy effective period. Claims outside the policy period require manual review or rejection depending on the coverage determination."
        },
        {
          "rule": "Missing Critical Information",
          "summary": "Claims missing required information such as loss date, claim amount, or supporting documents must not be automatically approved."
        },
        {
          "rule": "Delayed Reporting",
          "summary": "Claims reported more than 7 days after the loss date mayrequire investigation."
        }
      ]
    },
    {
      "source": "fraud_indicator_patterns",
      "details": [
        {
          "indicator": "Missing Information",
          "summary": "Missing loss dates, amounts, policy information, or supporting documents should trigger additional review."
        },
        {
          "indicator": "Delayed Reporting",
          "summary": "A significant delay between the loss date and claim report is a fraud indicator."
        },
        {
          "indicator": "Early Claim",
          "summary": "A claim submitted shortly after policy inception may require additional investigation."
        },
        {
          "indicator": "Near Limit Amount",
          "summary": "A claim amount very close to the policy limit is an investigation indicator."
        }
      ]
    }
  ],
  "reasoning": "Authoritative policy POL-4410 lists 'fire' as a covered claim type, so claim_type_covered is true. The claim record lacks a loss_date and a valid claim amount (description states both are missing and amount field is 0), so within_policy_period and amount_within_limit cannot be evaluated (null). Thereport_date (2026-08-20) is after the policy expiration (2026-01-01), and there are no supporting documents—these, together with the missing critical fields,trigger anomaly flags and require investigation. Because loss date and amount are missing, coverage cannot be confirmed or denied, so overall coverage_statusis set to 'unknown'."
}


End to end workflow:

Normal flow:
C-2031
    ↓
Intake
    ↓
Coverage
    ↓
Briefing
    ↓
Completed

HITL path:

C-2034
    ↓
Intake
    ↓
Coverage
    ↓
HITL
    ↓
Human decision
    ↓
Briefing
    ↓
Completed

Demo output:

Scenario 1: Enter Claim ID C-2034, Human i the loop decision: continue

command python -m main
Claim ID: C-2034
============================================================
      INSURANCE CLAIMS TRIAGE ASSISTANT
============================================================



[SUPERVISOR] Starting claim triage...
[SUPERVISOR] Current step: human_review_checkpoint

[MEMORY] Previous memory found:
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_briefing: Claim C-2034 (policy POL-4410) reports a fire loss but lacks critical information required for automated adjudication: loss_date is missing, claim amount is unspecified (0), and no supporting documents are attached. The claim report_date (2026-08-20) is after the policy expiration (2026-01-01). Policy POL-4410 does list fire as a covered claim type, but coverage cannotbe determined without additional information.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.

[INTAKE AGENT]
  Valid: False
  Manual review: True
  Missing fields: loss_date, amount, supporting_documents
  Validation errors:
    - loss_date is missing or empty.
    - amount is zero or not provided.
    - No supporting documents attached to the claim.
    - report_date (2026-08-20) is after policy expiration_date (2026-01-01).

[COVERAGE & ANOMALY AGENT]
  Coverage status: unknown
  Investigation required: True
  Anomaly flags:
    - missing_loss_date
    - missing_claim_amount_or_zero_value
    - report_date_after_policy_expiration
    - no_supporting_documents

============================================================
              HUMAN REVIEW REQUIRED
============================================================

Reason:
Intake validation requires manual review. Coverage/anomaly analysis requires investigation.

Available actions:
  1. continue
  2. reject

Enter human decision: continue

[SUPERVISOR] Human decision: continue

============================================================
                  FINAL RESULT
============================================================

Status: completed
Current step: completed

[ADJUSTER BRIEFING]

Summary:
Claim C-2034 (fire) is attached to policy POL-4410 (homeowners). The claim record lacks a loss_date, the claim amount is missing/zero, and no supporting documents are attached. The report_date (2026-08-20) is after the policy expiration_date (2026-01-01). Coverage status is unknown and further investigation is required.

Key findings:
  - Claim exists: claim_id C-2034, claim_type: fire.
  - Policy found: policy_number POL-4410 (homeowners), coverage_limit 40000, covers 'fire'.
  - Critical claim fields missing: loss_date empty and amount recorded as 0 / not provided.
  - No supporting documents attached (documents_count: 0).
  - Temporal anomaly: report_date 2026-08-20 is after policy expiration_date 2026-01-01.
  - Coverage status reported as 'unknown' and investigation_required = true.

Recommended action: manual_review

Missing information:
  - loss_date (missing/empty)
  - claim amount (missing or recorded as 0)
  - supporting documents (none attached)
  - confirmation of policy status/dates (to determine if coverage was in forceat time of loss or if any endorsements/reinstatements apply)


Scenario 2: Enter Claim ID: C-2034, Human i the loop decision: reject

============================================================
      INSURANCE CLAIMS TRIAGE ASSISTANT
============================================================

Enter Claim ID: C-2034

[SUPERVISOR] Starting claim triage...
[SUPERVISOR] Current step: human_review_checkpoint

[MEMORY] Previous memory found:
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_briefing: Claim C-2034 (policy POL-4410) reports a fire loss but lacks critical information required for automated adjudication: loss_date is missing, claim amount is unspecified (0), and no supporting documents are attached. The claim report_date (2026-08-20) is after the policy expiration (2026-01-01). Policy POL-4410 does list fire as a covered claim type, but coverage cannotbe determined without additional information.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_note: Loss date and amount are missing. Manual review required.
  - adjuster_briefing: Claim C-2034 (fire) is attached to policy POL-4410 (homeowners). The claim record lacks a loss_date, the claim amount is missing/zero,and no supporting documents are attached. The report_date (2026-08-20) is after the policy expiration_date (2026-01-01). Coverage status is unknown and further investigation is required.

[INTAKE AGENT]
  Valid: False
  Manual review: True
  Missing fields: loss_date, amount, documents
  Validation errors:
    - loss_date is missing or empty
    - amount is zero or unspecified
    - claim report_date (2026-08-20) occurs after policy expiration (2026-01-01)
    - no supporting documents attached to the claim

[COVERAGE & ANOMALY AGENT]
  Coverage status: unknown
  Investigation required: True
  Anomaly flags:
    - missing_critical_information
    - report_date_after_policy_expiration

============================================================
              HUMAN REVIEW REQUIRED
============================================================

Reason:
Intake validation requires manual review. Coverage/anomaly analysis requires investigation.

Available actions:
  1. continue
  2. reject

Enter human decision: reject

[SUPERVISOR] Human decision: reject

============================================================
                  FINAL RESULT
============================================================

Status: rejected_by_human
Current step: human_rejected

The claim was rejected by the human reviewer.