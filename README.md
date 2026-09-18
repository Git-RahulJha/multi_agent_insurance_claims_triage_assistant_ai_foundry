# multi_agent_insurance_claims_triage_assistant_ai_foundry
Claims Triage Assistant - A multiagent system that helps an insurance claims handler process a batch of incoming property/auto claims. 

                    User
                     │
                     ▼
            ┌─────────────────┐
            │ Supervisor Agent│
            │  Orchestrator   │
            └────────┬────────┘
                     │
          ┌──────────┴──────────┐
          │ Explicit Triage     │
          │ Routine / Workflow  │
          └──────────┬──────────┘
                     │
              ┌──────▼──────┐
              │ 1. Intake & │
              │ Validation  │
              │   Agent     │
              └──────┬──────┘
                     │
              validation result
                     │
              ┌──────▼──────┐
              │ 2. Anomaly &│
              │  Coverage   │
              │   Agent     │
              └──────┬──────┘
                     │
             coverage + anomaly
                     │
              ┌──────▼──────┐
              │ 3. Adjuster │
              │  Briefing   │
              │   Agent     │
              └──────┬──────┘
                     │
                     ▼
             Adjuster Recommendation

Knowledge:

knowledge/
│
├── underwriting_rules.md
├── fraud_indicator_patterns.md
└── coverage_guidelines.md

data/
│
├── claims.json
├── policy_coverage.json
├── claim_memory.json
└── customers.json       ← optional

Example Claim with Scenario:

| Claim  | Scenario                            |
| ------ | ----------------------------------- |
| C-2031 | Valid claim                         |
| C-2032 | Previous/similar claim              |
| C-2033 | Early-policy anomaly                |
| C-2034 | Missing data                        |
| C-2035 | Amount exceeds policy limit         |
| C-2036 | Loss date outside policy period     |
| C-2037 | Invalid policy number               |
| C-2038 | Duplicate claim ID                  |
| C-2039 | Suspicious amount near policy limit |
| C-2040 | Normal auto claim                   |

Workflow:

                    START
                      │
                      ▼
               Load Claim Batch
                      │
                      ▼
              Intake Validation
                      │
               ┌──────┴──────┐
               │             │
           Valid/Issues    Fatal Error
               │             │
               ▼             ▼
       Coverage Analysis   Error Handler
               │
               ▼
        Anomaly Detection
               │
               ▼
             HITL?
          ┌────┴────┐
          │         │
         Yes        No
          │         │
          ▼         │
    Human Review    │
          │         │
          └────┬────┘
               ▼
       Adjuster Briefing
               │
               ▼
              END

Project structure:

insurance_claims_agent/
│
├── agents/
│   ├── supervisor_agent.py
│   ├── intake_agent.py
│   ├── coverage_agent.py
│   └── briefing_agent.py
│
├── tools/
│   ├── claim_tools.py
│   ├── policy_tools.py
│   └── memory_tools.py
│
├── orchestration/
│   └── triage_workflow.py
│
├── rag/
│   ├── embeddings.py
│   ├── retriever.py
│   └── knowledge_base.py
│
├── repositories/
│   ├── claim_repository.py
│   ├── policy_repository.py
│   └── memory_repository.py
│
├── data/
│   ├── claims.json
│   ├── policy_coverage.json
│   └── claim_memory.json
│
├── knowledge/
│   ├── underwriting_rules.md
│   ├── fraud_indicator_patterns.md
│   └── coverage_guidelines.md
│
├── tests/
│
├── config.py
├── main.py
├── requirements.txt
└── .env

RAG:
Actual RAG flow follow below architecture:

User/Agent question
       │
       ▼
Generate query embedding
       │
       ▼
Azure AI Search
       │
       ▼
Vector similarity search
       │
       ▼
Top-K relevant chunks
       │
       ▼
LLM
       │
       ▼
Grounded answer

We implemented Azure AI Search, created index with below columns, then embedded using text-embedding-3-small OpenAI model
id
title
content
category
source
chunk_id
content_vector

Chunking: Chunks were make using 500 text plus 100 char overlap
HnswAlgorithm was used while ingestion.

Retrieval:
Both Lexical and Semantic search has been integrated so that system can search the exact keyword as well as semantic meaning of query.

User/Agent query
      │
      ├── Keyword search (BM25)
      │       └── exact terms
      │
      └── Vector search
              └── semantic meaning
                    │
                    ▼
             Azure AI Search
                    │
                    ▼
             Top relevant chunks


Coverage Agent:
Crosschecks each claim against the policyholder's coverage record 
To confirm the claim type is covered 
The claim amount is within policy limits
The loss date falls within the active policy period


                    Coverage Agent
                          │
             ┌────────────┼────────────┐
             │            │            │
             ▼            ▼            ▼
        get_claim()   get_policy()  search_knowledge()
             │            │            │
             ▼            ▼            ▼
          Claims       Policy DB      Azure AI Search
          JSON          JSON          RAG knowledge
             │            │            │
             └────────────┼────────────┘
                          ▼
                    LLM reasoning
                          │
                          ▼
                Coverage/Anomaly Result

Intake Agent: 
Basic flow:

Claim ID
   ↓
Retrieve claim
   ↓
Check basic claim integrity
   ↓
Identify missing/inconsistent data
   ↓
Return structured validation result

Briefing Agent:
Basic flow:

Intake Agent
     ↓
"What is wrong/missing?"

Coverage Agent
     ↓
"Is it covered and what anomalies exist?"

Briefing Agent
     ↓
"Give the adjuster a concise picture of the claim."

claim workflow:
process_claim("C-2034")
        │
        ▼
   Intake Agent
        │
        ▼
 IntakeValidation
        │
        ▼
  Coverage Agent
        │
        ▼
 CoverageAnalysis
        │
        ▼
 Briefing Agent
        │
        ▼
 AdjusterBriefing


Memory:
Short-term state and long-term memory become clearly different:

ClaimTriageState → current claim/workflow state.
claim_memory.json / memory repository → persistent historical information.

Sample persistent memory data:
[
  {
    "claim_id": "C-2034",
    "memory_type": "adjuster_note",
    "content": "Loss date and amount are missing. Manual review required."
  }
]

ClaimTriageState
    └── Short-term memory
        ├── intake
        ├── coverage
        └── briefing

claim_memory.json
    └── Long-term persistent memory
        └── previous claim interactions / notes

Using memory the workflow will be:

Claim ID
   ↓
Load previous memory
   ↓
Intake Agent
   ↓
Coverage Agent
   ↓
Briefing Agent
   ↓
Save important result to long-term memory
   ↓
Final State

HITL (Human In The Loop) scenario:

                    ┌── continue ──→ Briefing → Memory → Complete
                    │
Supervisor → HITL ──┤
                    │
                    └── reject ───→ Rejected

Observability:
After adding logging, workflow should look like:
                     Supervisor
                         │
                    Load Memory
                         │
                         ▼
                  ┌─────────────┐
                  │ Intake Agent│
                  └──────┬──────┘
                         │
                    Timeout
                    Error capture
                         │
                         ▼
                ┌──────────────────┐
                │ Coverage Agent   │
                └────────┬─────────┘
                         │
                    Timeout
                    Error capture
                         │
                         ▼
                    HITL Checkpoint
                         │
                         ▼
                ┌──────────────────┐
                │ Briefing Agent   │
                └────────┬─────────┘
                         │
                    Timeout
                    Error capture
                         │
                         ▼
                    Save Memory
                         │
                         ▼
                      Complete

with logging look like (copied from demo output):
[SUPERVISOR] Starting claim triage...
2026-09-18 17:26:45,984 | INFO | claims.supervisor | Starting claim triage | claim_id=C-2034
2026-09-18 17:26:45,985 | INFO | claims.supervisor | Loading persistent memory| claim_id=C-2034
2026-09-18 17:26:45,986 | INFO | claims.supervisor | Executing Intake Agent | claim_id=C-2034


Final outcomes are as follow:
| Demo requirement            | Status |
| --------------------------- | ------ |
| Supervisor Agent            | ✅      |
| Intake Agent                | ✅      |
| Coverage & Anomaly Agent    | ✅      |
| Adjuster Briefing Agent     | ✅      |
| Explicit orchestration      | ✅      |
| Short-term state            | ✅      |
| Long-term persistent memory | ✅      |
| Azure AI Search grounding   | ✅      |
| HITL checkpoint             | ✅      |
| HITL resume                 | ✅      |
| 3+ function tools           | ✅      |
| Timeout handling            | ✅      |
| Structured errors           | ✅      |
| Basic logging               | ✅      |
