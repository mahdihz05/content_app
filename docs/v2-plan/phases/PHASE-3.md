# Phase 3 - Connections & Previous Content Ingestion

## Objective
Ingest authorized prior content and metrics incrementally into canonical history, with documented coverage and no duplicate records.

## Starting Preconditions
- Phase 2 acceptance passed; Phase 1 command/callback substrate remains accepted.
- Pilot platform, acquisition mode, credentials standard, and n8n operating ownership are approved.

## Architecture Constraints
- Telegram Bot API ingestion is limited to demonstrably bot-visible history; record coverage/limitations.
- Export/manual import is the approved fallback; MTProto/user sessions are prohibited.
- n8n executes scoped named workflows; Django validates/canonicalizes all results.

## Exact Deliverables
- Connection/credential/cursor/capability records; verify/import/metrics workflows; signed callbacks; bounded backfill/re-sync; coverage UI; pilot reconciliation.

## Implementation Workstreams
Connection domain, secure credential references, n8n connectors, import normalization, callbacks, template UI, and pilot operations. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P3-BE-001 | Create `connections` domain APIs for capability, verification, import request/status, and manual re-sync. | SEQUENTIAL | Add `connections/`, `platforms/`, `automation/` | P1/P2 accepted | Workspace-scoped connection contract. | API/schema/policy tests. |
| P3-BE-002 | Implement normalized page/media/cursor callback handlers that upsert canonical history idempotently. | SEQUENTIAL | `connections/`, `content_history/`, `automation/` | P3-BE-001 | Callback domain service and reconciliation state. | Duplicate/out-of-order/partial-page tests. |
| P3-BE-003 | Implement export/manual-import validation and provenance/coverage recording. | PARALLEL-SAFE | `connections/`, `content_history/` | P2 accepted, import-mode gate | Approved fallback importer. | Sanitized export fixtures and coverage tests. |

## Database / Migration Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P3-DB-001 | Add PlatformConnection, CredentialReference, Verification, Cursor, capability, import-batch/observation records and canonical links. | SEQUENTIAL | `connections/migrations/`, content history migrations | P3-BE-001 | Additive constrained schema. | Migration, encryption-reference, and uniqueness tests. |
| P3-DB-002 | Map SocialAccount, CampaignSocialAccount, TelegramChannel, and verification records without retiring legacy data. | SEQUENTIAL | Data migration/command | P3-DB-001 | Legacy connection mapping report. | Count/cursor/ownership reconciliation. |

## UI Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P3-UI-001 | Deliver Django-template connection management, import range, coverage, progress, retry, and failure views. | SEQUENTIAL | dashboard/messaging templates and scripts | P3-BE-001/P3-BE-002 | Feature-flagged pilot UI. | Browser flow with mocked callbacks; no credential exposure. |

## n8n Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P3-N8N-001 | Implement exported reusable envelope, scoped-connection, pagination/rate-limit, error, media, and callback sub-workflows. | SEQUENTIAL | `n8n/workflows/` | P1-BE-003, n8n gate | Reviewed workflow JSON fixtures. | Mock-provider workflow contract suite. |
| P3-N8N-002 | Implement named `connection.verify`, `connection.ingest_content`, and `connection.refresh_metrics` pilot workflows. | SEQUENTIAL | `n8n/workflows/` | P3-N8N-001, P3-BE-002 | Versioned pilot workflows. | Signed callback, resume, rate-limit, and idempotency test runs. |

## Agent / AI Tasks
- P3-AI-001, SEQUENTIAL: register `connection.verify`, `connection.ingest_content`, and `connection.refresh_metrics` in Tool Gateway with bounded schemas/effects. Depends on P3-BE-001/P3-N8N-002. Verify policy and job-reference tests; no direct provider access.

## Security Tasks
- P3-SEC-001, SEQUENTIAL: implement credential-reference access, callback verification, grant scope, and import payload redaction. Depends on P3-DB-001/P3-N8N-001. Verify forgery, replay, cross-workspace, and log-redaction tests.

## Tests
- P3-TST-001, PARALLEL-SAFE: connector normalization/cursor/deduplication fixtures for bot-visible and export sources.
- P3-TST-002, SEQUENTIAL: pilot E2E backfill, recurring sync, reconciliation, and recovery tests. Depends on all connector tasks.

## Acceptance Criteria
- Pilot workspace verifies a supported connection or submits an approved export, imports a bounded history without duplicates, and sees accurate coverage/progress.
- Cursors advance only after Django commits a page; n8n is not queried for product status.

## Definition of Done
All P3 IDs are accepted and pilot reconciliation/recovery evidence is recorded.

## Rollback Strategy
Disable connection/schedule flags and stop dispatch. Preserve cursors, observations, raw references, and imported records; do not delete data after workflow failure.

## Dependencies
Phase 1 and 2 acceptance, selected pilot/acquisition mode, secret management, n8n operating model.

## Decisions/Gates Required Before Starting
- Telegram Bot API pilot scope/coverage standard and export/manual-import acceptance.
- No MTProto decision is needed because MTProto is out of scope.
- Credentials, retention, and n8n deployment/callback boundary approved.

## Risks
Provider history depth and quotas vary; report coverage rather than claim completeness. Large import failures require resumable cursor semantics.

## Explicitly Out of Scope
MTProto, user sessions, arbitrary platform imports, autonomous publishing, React, MCP.

## Development Checklist
- [ ] P3-BE-001
- [ ] P3-BE-002
- [ ] P3-BE-003
- [ ] P3-DB-001
- [ ] P3-DB-002
- [ ] P3-UI-001
- [ ] P3-N8N-001
- [ ] P3-N8N-002
- [ ] P3-AI-001
- [ ] P3-SEC-001
- [ ] P3-TST-001
- [ ] P3-TST-002

## Reviewer Checklist
- [ ] Acquisition mode, cursor commits, and canonical upserts obey frozen boundaries.
- [ ] Workflow JSON and callback grant scope are reviewed.
- [ ] Coverage/provenance and secret redaction are sufficient.

## QA Checklist
- [ ] Bounded backfill, re-sync, duplicate, retry, and partial-page scenarios pass.
- [ ] Export/manual import coverage is correctly displayed.
- [ ] Cross-workspace connection/callback access is denied.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates connector and workflow implementation, Reviewer validates security/normalization, QA executes pilot and recovery evidence, then acceptance unlocks dependent Phase 5 and Phase 7 work.
