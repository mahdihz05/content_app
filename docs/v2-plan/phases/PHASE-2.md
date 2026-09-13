# Phase 2 - Canonical Content History

## Objective
Create the workspace-scoped immutable content corpus and compatibility projection required for all history, planning, generation, and delivery work.

## Starting Preconditions
- Phase 1 acceptance passed.
- Object-storage provider, retention policy, and content-version status semantics are approved.

## Architecture Constraints
- `ContentRecord`/`ContentVersion` are canonical; `ContentItem` remains during transition.
- Approved versions are immutable. Django remains authoritative for publications and metrics.
- Legacy JSON is retained as provenance; ambiguity is recorded, never invented.

## Exact Deliverables
- ContentRecord, ContentVersion, ContentAsset, Publication, ContentMetricObservation; backfill/reconciliation; V2 history APIs/UI; compatibility projection; `content.search_history` tool.

## Implementation Workstreams
Canonical schema, backfill/projection, APIs, template history UI, object metadata, and history search. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P2-BE-001 | Create `content_history` domain services for version lifecycle, hash/provenance, publications, and metrics. | SEQUENTIAL | Add `content_history/` | P1 accepted | Canonical state-transition services. | Immutability and lineage unit tests. |
| P2-BE-002 | Add V2 history/version/publication/asset APIs and legacy compatibility projection. | SEQUENTIAL | `content_history/urls.py`, views; `content/urls.py`, `ai_chat.py` | P2-BE-001 | `/api/v2/` contract while `/content/api/v1/` remains stable. | API contract and projection tests. |
| P2-BE-003 | Implement workspace-filtered `content.search_history` Tool Gateway adapter. | PARALLEL-SAFE | `content_history/`, `automation/` | P1 accepted, P2-BE-001 | Read-only typed tool result with citations. | Scope/filter/schema tests. |

## Database / Migration Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P2-DB-001 | Add canonical content, version, asset, publication, and metric tables with version/external-ID constraints. | SEQUENTIAL | `content_history/migrations/` | P2-BE-001 | Expand-only schema. | Migration and uniqueness tests. |
| P2-DB-002 | Backfill ContentItem, GeneratedContent, generated JSON, and Telegram logs; generate reconciliation report. | SEQUENTIAL | Data migration/management command; legacy models | P2-DB-001 | Mapped records with provenance/ambiguity markers. | Count, hash, sampled-content, and publication-log reconciliation. |

## UI Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P2-UI-001 | Add feature-flagged Django-template Content History list/detail/version timeline and legacy-item links. | SEQUENTIAL | dashboard templates/scripts, V2 APIs | P2-BE-002, P2-DB-002 | Workspace-scoped history UI. | Browser tests for list, detail, version lineage, and legacy links. |

## n8n Tasks
- P2-N8N-001, PARALLEL-SAFE: version the `content.publish` callback/media-reference JSON contract only. Area: `n8n/workflows/` manifests. Depends on P1-BE-003. Verify schema contract fixture; do not dispatch delivery.

## Agent / AI Tasks
Only P2-BE-003 is enabled; no draft generation or Agent run is introduced.

## Security Tasks
- P2-SEC-001, SEQUENTIAL: enforce workspace authorization for history, assets, publications, and object-storage references. Depends on P2-BE-002. Verify direct-ID and signed-access denial tests.

## Tests
- P2-TST-001, PARALLEL-SAFE: backfill fixtures covering missing/duplicated JSON, multiple generated rows, and conflicting legacy statuses.
- P2-TST-002, SEQUENTIAL: immutable version, parent lineage, external-ID dedupe, projection, object metadata, and tenant-isolation integration suite. Depends on P2-DB-002/P2-SEC-001.

## Acceptance Criteria
- Each ContentItem maps to a traceable content record; every Telegram log maps to a Publication or documented exception.
- Approved versions cannot be overwritten; legacy flows work with flags both off and on.
- History search and asset access are workspace isolated.

## Definition of Done
All P2 tasks are accepted and reconciliation/projection evidence is retained.

## Rollback Strategy
Stop dual-write and serve legacy projections; preserve immutable V2 rows/assets for reconciliation. Never delete migrated history.

## Dependencies
Phase 1 acceptance, storage/retention decision, content-version semantics.

## Decisions/Gates Required Before Starting
- Object storage and retention/deletion policy.
- Version statuses and approval interpretation for legacy content.

## Risks
Inconsistent legacy fields may make lineage uncertain. Preserve original payloads and label inference.

## Explicitly Out of Scope
External ingestion, embeddings, brainstorming, Agent drafts, scheduling, React, MCP.

## Development Checklist
- [ ] P2-BE-001
- [ ] P2-BE-002
- [ ] P2-BE-003
- [ ] P2-DB-001
- [ ] P2-DB-002
- [ ] P2-UI-001
- [ ] P2-N8N-001
- [ ] P2-SEC-001
- [ ] P2-TST-001
- [ ] P2-TST-002

## Reviewer Checklist
- [ ] Immutable lineage and compatibility projection are correct.
- [ ] Backfill never fabricates approval/provenance.
- [ ] Storage and tenancy boundaries are enforced.

## QA Checklist
- [ ] Reconciliation thresholds and sample data pass.
- [ ] Legacy content/chat pages remain functional.
- [ ] History UI cannot access another workspace.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates schema, APIs, projection, and UI; Reviewer approves lineage/reconciliation; QA validates data and compatibility; acceptance unlocks Phase 3 and Phase 4.
