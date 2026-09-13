# V2 Plan Progress

**Weighted completion: 0%**

Phase 0 implementation is complete: all eight internal development tasks have
passed their technically executable verification. Phase acceptance and its 8%
weight remain at 0% pending provider-side credential revocation, deployment
secret-store validation, coordinated history remediation, and owner sign-off.

| Phase | Weight | Status | Completion | Exit checkpoint |
| --- | ---: | --- | ---: | --- |
| 0. Baseline, Safety, And Compatibility Contract | 8% | Implementation complete; acceptance pending external gates (8/8 internal) | 0% | Characterized, tested current behavior and safe release baseline |
| 1. Workspace Tenancy, Policy, And Execution Ledger | 16% | Not started | 0% | Workspace isolation, approvals, commands, audit, and outbox proven |
| 2. Canonical Content History And Asset Foundation | 15% | Not started | 0% | Legacy content/version/publication history reconciled |
| 3. Connections And Previous-Content Ingestion | 14% | Not started | 0% | Pilot connector imports incrementally without duplicates |
| 4. Workspace Memory And RAG | 13% | Not started | 0% | Cited, permission-filtered retrieval proven |
| 5. Content Intelligence, Brainstorming, And Content Map | 12% | Not started | 0% | Explainable, reversible planning proposals available |
| 6. AI Content Agent And Text/Visual Draft Production | 10% | Not started | 0% | Validated, reviewable Agent drafts/assets available |
| 7. n8n Delivery Migration, Scheduling, And Reusable Operations | 8% | Not started | 0% | Approved n8n Telegram delivery parity and recovery proven |
| 8. Product Transition, Observability, And Tool-Contract Readiness | 4% | Not started | 0% | Controlled rollout, operations, and MCP-compatible tool contracts complete |
| **Total** | **100%** | **In progress** | **0%** | **All phase definitions of done accepted** |

## Task Ledger

Every item below starts at `Not started / 0%`. Check an item only after implementation and its required verification pass. Phase weights are credited only at signed phase acceptance, not when individual tasks are checked.

### Phase 0 - 8% - 0%

- [x] `P0-BE-001` - Complete - 100% - Route/consumer matrix reviewed; resolver characterization passes in the available isolated test environment.
- [x] `P0-BE-002` - Complete - 100% - Additive V2 correlation/error/health/readiness/flag interfaces implemented; contract tests pass in the available isolated test environment.
- [x] `P0-DB-001` - Complete - 100% - PostgreSQL 16 forward migration and seeded custom-dump restore rehearsal passed with matching counts.
- [x] `P0-UI-001` - Complete - 100% - Two Chromium smoke tests pass in the built backend image against PostgreSQL.
- [x] `P0-N8N-001` - Complete - 100% - Sanitized evidence/governance validated; deployed volume has zero workflows/webhooks/credentials/executions.
- [ ] `P0-SEC-001` - Implementation complete / acceptance pending external gate - 0% accepted - Tracked tree is clean and environment loading is implemented; provider revocation, deployment secret-store validation, and coordinated history remediation require external authority.
- [x] `P0-TST-001` - Complete - 100% - 23 authentication/content/Telegram/common characterization tests pass on PostgreSQL 16.
- [x] `P0-TST-002` - Complete - 100% - Hosted GitHub Actions run `34755437493` passed from a clean checkout on PostgreSQL 16, including browser smoke.

### Phase 1 - 16% - 0%

- [ ] `P1-BE-001` - Not started - 0%
- [ ] `P1-BE-002` - Not started - 0%
- [ ] `P1-BE-003` - Not started - 0%
- [ ] `P1-DB-001` - Not started - 0%
- [ ] `P1-DB-002` - Not started - 0%
- [ ] `P1-UI-001` - Not started - 0%
- [ ] `P1-SEC-001` - Not started - 0%
- [ ] `P1-TST-001` - Not started - 0%
- [ ] `P1-TST-002` - Not started - 0%

### Phase 2 - 15% - 0%

- [ ] `P2-BE-001` - Not started - 0%
- [ ] `P2-BE-002` - Not started - 0%
- [ ] `P2-BE-003` - Not started - 0%
- [ ] `P2-DB-001` - Not started - 0%
- [ ] `P2-DB-002` - Not started - 0%
- [ ] `P2-UI-001` - Not started - 0%
- [ ] `P2-N8N-001` - Not started - 0%
- [ ] `P2-SEC-001` - Not started - 0%
- [ ] `P2-TST-001` - Not started - 0%
- [ ] `P2-TST-002` - Not started - 0%

### Phase 3 - 14% - 0%

- [ ] `P3-BE-001` - Not started - 0%
- [ ] `P3-BE-002` - Not started - 0%
- [ ] `P3-BE-003` - Not started - 0%
- [ ] `P3-DB-001` - Not started - 0%
- [ ] `P3-DB-002` - Not started - 0%
- [ ] `P3-UI-001` - Not started - 0%
- [ ] `P3-N8N-001` - Not started - 0%
- [ ] `P3-N8N-002` - Not started - 0%
- [ ] `P3-AI-001` - Not started - 0%
- [ ] `P3-SEC-001` - Not started - 0%
- [ ] `P3-TST-001` - Not started - 0%
- [ ] `P3-TST-002` - Not started - 0%

### Phase 4 - 13% - 0%

- [ ] `P4-BE-001` - Not started - 0%
- [ ] `P4-BE-002` - Not started - 0%
- [ ] `P4-BE-003` - Not started - 0%
- [ ] `P4-DB-001` - Not started - 0%
- [ ] `P4-UI-001` - Not started - 0%
- [ ] `P4-AI-001` - Not started - 0%
- [ ] `P4-SEC-001` - Not started - 0%
- [ ] `P4-TST-001` - Not started - 0%
- [ ] `P4-TST-002` - Not started - 0%

### Phase 5 - 12% - 0%

- [ ] `P5-BE-001` - Not started - 0%
- [ ] `P5-BE-002` - Not started - 0%
- [ ] `P5-BE-003` - Not started - 0%
- [ ] `P5-DB-001` - Not started - 0%
- [ ] `P5-UI-001` - Not started - 0%
- [ ] `P5-N8N-001` - Not started - 0%
- [ ] `P5-AI-001` - Not started - 0%
- [ ] `P5-AI-002` - Not started - 0%
- [ ] `P5-SEC-001` - Not started - 0%
- [ ] `P5-TST-001` - Not started - 0%
- [ ] `P5-TST-002` - Not started - 0%

### Phase 6 - 10% - 0%

- [ ] `P6-BE-001` - Not started - 0%
- [ ] `P6-BE-002` - Not started - 0%
- [ ] `P6-BE-003` - Not started - 0%
- [ ] `P6-DB-001` - Not started - 0%
- [ ] `P6-UI-001` - Not started - 0%
- [ ] `P6-N8N-001` - Not started - 0%
- [ ] `P6-AI-001` - Not started - 0%
- [ ] `P6-AI-002` - Not started - 0%
- [ ] `P6-SEC-001` - Not started - 0%
- [ ] `P6-TST-001` - Not started - 0%
- [ ] `P6-TST-002` - Not started - 0%

### Phase 7 - 8% - 0%

- [ ] `P7-BE-001` - Not started - 0%
- [ ] `P7-BE-002` - Not started - 0%
- [ ] `P7-BE-003` - Not started - 0%
- [ ] `P7-DB-001` - Not started - 0%
- [ ] `P7-UI-001` - Not started - 0%
- [ ] `P7-N8N-001` - Not started - 0%
- [ ] `P7-N8N-002` - Not started - 0%
- [ ] `P7-AI-001` - Not started - 0%
- [ ] `P7-SEC-001` - Not started - 0%
- [ ] `P7-TST-001` - Not started - 0%
- [ ] `P7-TST-002` - Not started - 0%

### Phase 8 - 4% - 0%

- [ ] `P8-BE-001` - Not started - 0%
- [ ] `P8-BE-002` - Not started - 0%
- [ ] `P8-BE-003` - Not started - 0%
- [ ] `P8-DB-001` - Not started - 0%
- [ ] `P8-UI-001` - Not started - 0%
- [ ] `P8-N8N-001` - Not started - 0%
- [ ] `P8-AI-001` - Not started - 0%
- [ ] `P8-SEC-001` - Not started - 0%
- [ ] `P8-TST-001` - Not started - 0%
- [ ] `P8-TST-002` - Not started - 0%

## Checklist

### Phase 0 - 8%

- [x] Inventory and classify active, compatibility, and orphaned routes/assets.
- [x] Add characterization coverage for active content and Telegram behavior.
- [x] Establish CI, health/readiness, correlation IDs, and error conventions.
- [x] Export/archive the inactive legacy n8n workflow; define source-controlled workflow standards.
- [ ] Complete external provider revocation, deployment secret-store validation, coordinated history remediation, and acceptance sign-off. Repository remediation and backup/migration rehearsal are complete.

### Phase 1 - 16%

- [ ] Add workspace, membership, role, and policy model/API.
- [ ] Backfill default workspaces and map existing owned records.
- [ ] Add audit events, approvals, commands, outbox, executions, and dead letters.
- [ ] Implement tenant/object/tool authorization and execution grants.
- [ ] Pass migration, isolation, policy, idempotency, and approval-replay tests.

### Phase 2 - 15%

- [ ] Add canonical content, version, asset, publication, and metric models.
- [ ] Backfill and reconcile ContentItem, GeneratedContent, JSON generation, and Telegram logs.
- [ ] Deliver V2 Content History APIs and compatibility projection.
- [ ] Deliver workspace-scoped history UI.
- [ ] Prove immutable versioning and legacy page compatibility.

### Phase 3 - 14%

- [ ] Add platform connections, credential references, verification, and cursors.
- [ ] Implement source-controlled verify/import/metrics n8n workflows and reusable sub-workflows using approved acquisition modes only.
- [ ] Build signed callback, cursor, normalization, deduplication, and reconciliation paths.
- [ ] Deliver connection/import progress and recovery UI.
- [ ] Complete a bounded pilot backfill and recurring sync for approved platform(s), recording Telegram Bot API history coverage or using export/manual import.

### Phase 4 - 13%

- [ ] Enable and validate pgvector in production-like migration rehearsal.
- [ ] Add memory source, entry, chunk, embedding revision, and retrieval snapshot records.
- [ ] Implement protected ingestion, deterministic chunking, hybrid retrieval, and citations.
- [ ] Deliver Workspace Memory management and authoring retrieval UI.
- [ ] Pass tenant-isolation, provenance, retrieval, and prompt-injection tests.

### Phase 5 - 12%

- [ ] Add intelligence snapshots/recommendations and outcome feedback.
- [ ] Add idea proposals, feedback, Content Maps, revisions, and slots.
- [ ] Implement evidence-backed LLM proposal services and deterministic validators.
- [ ] Deliver Intelligence, Brainstorming, and Content Map UI.
- [ ] Prove proposals cannot schedule or publish.

### Phase 6 - 10%

- [ ] Add Agent runs, tool invocations, generation evaluation, and provider adapters.
- [ ] Implement validated text drafts as immutable content versions.
- [ ] Implement reviewed visual assets with hashes and metadata.
- [ ] Deliver transparent Agent activity and review UI.
- [ ] Prove bounded tools, citations, workspace isolation, and legacy parity.

### Phase 7 - 8%

- [ ] Implement command/outbox dispatch and signed n8n result callbacks.
- [ ] Implement source-controlled publishing, scheduling, and metrics workflows.
- [ ] Deliver approval, progress, reconciliation, and dead-letter recovery UI.
- [ ] Complete non-duplicating Telegram pilot and failure recovery drill.
- [ ] Retire direct Telegram delivery only after accepted parity evidence.

### Phase 8 - 4%

- [ ] Complete rollout telemetry, alerts, retention/export, and backup/restore drills.
- [ ] Retain and complete the Django-template/vanilla-JavaScript UI for V2.
- [ ] Freeze MCP-compatible tool schemas and run Tool Gateway conformance without implementing MCP.
- [ ] Complete load, chaos, security, migration, and end-to-end regression suites.
- [ ] Approve legacy retirement based on reconciliation and rollback windows.

## Completion Rules

- A task is complete only when its implementation and stated verification are accepted; planning work counts as `0%`.
- A phase receives its full weight only when every enabled task, required gate, QA checklist, and Definition of Done are accepted. A deferred `BLOCKED-BY-GATE` task must have a documented approved exclusion; otherwise the phase remains unaccepted.
- Weighted completion is the sum of fully accepted phase weights; partial implementation does not change the reported percentage.
- A consequential workflow is never marked complete solely because n8n reports success. Django reconciliation, audit, and recovery acceptance are required.
- Changes outside the approved V2 scope do not count toward completion.

## Architecture Review Gates

- [ ] Workspace tenancy and initial role model approved.
- [ ] Initial ingestion platforms and allowed data-acquisition modes approved, including Telegram Bot API coverage limits and export/manual-import fallback.
- [ ] pgvector, object storage, retention, and data-residency decisions approved.
- [ ] Provider, budget, and publishing-approval policies approved.
- [ ] n8n deployment, credentials, workflow source control, and callback boundary approved.
- [x] Django-template/vanilla-JavaScript frontend retained for V2; React and MCP implementation deferred outside V2.
- [ ] Migration inventory and backup rehearsal accepted.

ARCHITECTURE FROZEN: YES
READY FOR PHASE 0 DEVELOPMENT: YES
