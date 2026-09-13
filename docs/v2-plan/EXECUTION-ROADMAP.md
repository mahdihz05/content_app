# Execution Roadmap

## 1. Phase Order
1. Phase 0 - Baseline, Safety, Compatibility
2. Phase 1 - Workspace, Policy, Execution Ledger
3. Phase 2 - Canonical Content History
4. Phase 3 - Connections & Previous Content Ingestion
5. Phase 4 - Workspace Memory & RAG
6. Phase 5 - Content Intelligence, Brainstorming & Content Map
7. Phase 6 - AI Content Agent & Generation
8. Phase 7 - n8n Delivery Migration & Scheduling
9. Phase 8 - Product Transition, Observability & MCP Readiness

## 2. Phase Dependencies
- P1 requires P0 acceptance.
- P2 requires P1 acceptance.
- P3 requires P1 and P2 acceptance.
- P4 requires P1 and P2 acceptance.
- P5 requires P3 and P4 acceptance.
- P6 requires P5 acceptance plus P1-P4 foundations.
- P7 requires P1, P3, and P6 acceptance.
- P8 requires P0-P7 acceptance.

## 3. Required Gates
- P0: deployment-owner access, CI/secret-storage decision, secret rotation, backup/migration rehearsal.
- P1: workspace semantics and launch roles.
- P2: object storage, retention, and version-status semantics.
- P3: pilot platform/acquisition mode, Telegram coverage standard, credential/n8n operating model.
- P4: pgvector production-like validation, embedding provider, residency, retention.
- P5: intelligence rubric, research provider/retention decision.
- P6: LLM/visual provider, budgets, platform validation rules.
- P7: n8n operations, publishing approval policy, Telegram idempotency/reconciliation.
- P8: observability, retention/export, production topology, retirement evidence threshold.

## 4. Parallel-Safe Work
- Within P0: route inventory, UI smoke specification, workflow export, and characterization fixtures after baseline access.
- Within P1-P8: only tasks marked `PARALLEL-SAFE` in their phase file may run together under the phase Development Agent.
- After P2 acceptance: P3 and P4 may run concurrently. P5 cannot start until both are accepted.
- No implementation from a later phase may start before its predecessor acceptance gate, except documented `PARALLEL-SAFE` preparation that does not change product behavior or schema.

## 5. Developer/Reviewer/QA Handoffs
- Each phase has one Development Agent responsible for integration, sequencing, and evidence assembly.
- Development Agent completes all enabled task IDs -> Reviewer validates architecture, migrations, security, and compatibility -> QA validates required automated/manual scenarios -> Phase Acceptance owner signs the phase gate.
- Rejected review or QA returns work to the same phase; no dependent phase starts.

## 6. Overall Completion Formula
`overall_completion = sum(phase_weight for each phase whose required development tasks are implemented and whose phase acceptance is signed)`

Individual task completion is tracked only after implementation and required verification pass. Planning, investigation, blocked work, and unaccepted work contribute `0%`.
