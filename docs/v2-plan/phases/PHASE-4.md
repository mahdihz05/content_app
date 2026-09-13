# Phase 4 - Workspace Memory & RAG

## Objective
Provide curated, workspace-isolated, cited memory retrieval using PostgreSQL plus pgvector.

## Starting Preconditions
- Phase 2 acceptance passed; Phase 1 policy and object-storage boundaries are accepted.
- pgvector production-like validation, embedding provider, data residency, and retention decisions are approved.

## Architecture Constraints
- Curated memory is distinct from imported history; history inclusion is explicit.
- Django owns sources, chunks, provenance, scopes, snapshots, and retrieval policy.
- No dedicated vector database, React, MCP, or raw embedding API exposure.

## Exact Deliverables
- pgvector migration validation, memory source/entry/chunk/revision/snapshot records, protected ingestion, hybrid cited retrieval, Django-template management/retrieval UI, and `memory.retrieve` tool.

## Implementation Workstreams
Database/vector validation, source ingestion, embedding adapter, retrieval, UI, security, and tests. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P4-BE-001 | Create `memory` domain for source lifecycle, review/freshness, deterministic extraction/chunking, and provenance. | SEQUENTIAL | Add `memory/`, integrations | P1/P2 accepted | Workspace-scoped memory services. | Source/chunk lifecycle tests. |
| P4-BE-002 | Implement hybrid retrieval: policy-filter, full-text/vector search, rank fusion, diversity/token limits, and citations. | SEQUENTIAL | `memory/` services/APIs | P4-BE-001, P4-DB-001 | Retrieval result with snapshot/freshness. | Ranking, budget, citation, and scope fixtures. |
| P4-BE-003 | Retire or map unregistered `ai` knowledge/embedding scaffolding without treating it as a deployed table. | PARALLEL-SAFE | `ai/models/KnowledgeSource.py`, `DocumentEmbedding.py`, `memory/` | P4-DB-001 | Explicit migration/retirement record. | Import/model registration and provenance checks. |

## Database / Migration Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P4-DB-001 | Validate and enable `vector` extension through guarded migration; add source, entry, chunk, revision, snapshot tables/indexes. | BLOCKED-BY-GATE | PostgreSQL provisioning, `memory/migrations/` | pgvector gate | Rehearsed pgvector schema. | Production-like forward/rollback performance and extension checks. |

## UI Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P4-UI-001 | Add Django-template Memory library, upload/status/review, scope selection, and cited retrieval panel. | SEQUENTIAL | templates/scripts, memory APIs | P4-BE-002 | Feature-flagged workspace UI. | Browser upload/review/retrieval and authorization tests. |

## n8n Tasks
No core n8n workflow. External document conversion is deferred; any future `memory.extract_source` must return text/asset metadata only.

## Agent / AI Tasks
- P4-AI-001, SEQUENTIAL: expose read-only `memory.retrieve` with bounded excerpts/citations and untrusted-evidence labeling. Depends on P4-BE-002/P1-BE-003. Verify schema, scope, and injection-boundary tests.

## Security Tasks
- P4-SEC-001, SEQUENTIAL: enforce source/asset visibility, signed object access, retention/expiry, and retrieval scope filters. Depends on P4-BE-001. Verify direct-ID, cross-workspace, expired-source, and raw-vector denial tests.

## Tests
- P4-TST-001, PARALLEL-SAFE: deterministic chunk/hash and re-embedding provenance fixtures.
- P4-TST-002, SEQUENTIAL: pgvector/full-text integration, hybrid ranking, tenant isolation, token budget, citation, and prompt-injection suite. Depends on P4-DB-001/P4-BE-002/P4-SEC-001.

## Acceptance Criteria
- Authorized users can ingest/review curated sources and retrieve only scoped, cited, fresh evidence.
- Imported history is included only by explicit corpus selection; no retrieval leaks across workspaces.

## Definition of Done
All P4 IDs are accepted with pgvector rehearsal and retrieval security evidence.

## Rollback Strategy
Disable memory ingestion/retrieval flags; retain source/provenance/chunks and the pgvector extension. Do not drop vectors during rollback.

## Dependencies
Phase 1/2 acceptance and pgvector/storage/provider/retention gates. P4 may execute concurrently with Phase 3 after Phase 2 acceptance.

## Decisions/Gates Required Before Starting
- pgvector availability and migration performance validated.
- Object storage, embedding provider, data residency, retention/deletion policy approved.

## Risks
Extraction quality, sensitive content, retrieval cost, and weak ranking. Use review states, quotas, deterministic provenance, and bounded retrieval.

## Explicitly Out of Scope
Dedicated vector DB, unreviewed history-as-memory, asynchronous conversion workflow, React, MCP.

## Development Checklist
- [ ] P4-BE-001
- [ ] P4-BE-002
- [ ] P4-BE-003
- [ ] P4-DB-001
- [ ] P4-UI-001
- [ ] P4-AI-001
- [ ] P4-SEC-001
- [ ] P4-TST-001
- [ ] P4-TST-002

## Reviewer Checklist
- [ ] pgvector design/provenance and hybrid retrieval are correct.
- [ ] Curated memory and history corpora remain distinct.
- [ ] Scope/retention/object-access controls are complete.

## QA Checklist
- [ ] Upload, review, expiry, retrieval, and citation paths pass.
- [ ] Tenant, campaign/content scope, and injection tests pass.
- [ ] Production-like pgvector rehearsal evidence is reproducible.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates vector and memory work, Reviewer validates data/security boundaries, QA validates retrieval behavior and migration rehearsal, then acceptance unlocks Phase 5 and Phase 6 dependencies.
