# Phase 7 - n8n Delivery Migration & Scheduling

## Objective
Migrate Telegram delivery and scheduling from synchronous request-path behavior to approved, command-driven, source-controlled n8n workflows.

## Starting Preconditions
- Phase 3 and Phase 6 acceptance passed; Phase 1 ledger/callback substrate is accepted.
- n8n operating model, credential custody, callback boundary, approval policy, and Telegram idempotency/reconciliation strategy are approved.

## Architecture Constraints
- Django owns schedule intent, approval, command, publication state, recovery, and product status.
- n8n runs named scoped workflows and reports signed callbacks; never publish twice intentionally.
- Direct Telegram publisher remains behind legacy flag until parity/recovery acceptance.

## Exact Deliverables
- Dispatch/outbox, schedule intent, approval UI, publish/schedule commands, source-controlled workflows/sub-workflows, reconciliation/dead-letter recovery, and non-duplicating Telegram pilot.

## Implementation Workstreams
Command dispatch, schedule/publication domain, Telegram workflow, UI approval/recovery, reconciliation, security, and pilot operations. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P7-BE-001 | Implement outbox dispatcher, named workflow selection, callback application, retry classification, and dead-letter recovery service. | SEQUENTIAL | `automation/`, settings, internal routes | P1, n8n gate | Authoritative command lifecycle. | Atomic dispatch, callback/replay, retry, and dead-letter tests. |
| P7-BE-002 | Implement schedule intent and publish command services bound to immutable approved version/asset/destination fingerprints. | SEQUENTIAL | content history/automation | P7-BE-001, P6 accepted | Consequential state transitions. | Approval invalidation/idempotency/reconciliation tests. |
| P7-BE-003 | Add legacy Telegram projection/flag controls and non-delivering preflight reconciliation. | SEQUENTIAL | messaging services/views, content history | P7-BE-002 | Safe coexistence controls. | No-double-publish and legacy compatibility tests. |

## Database / Migration Tasks
- P7-DB-001, SEQUENTIAL: extend commands/executions/publications/approvals/outbox/dead-letters and add schedule intent records. Area: automation/content history migrations. Depends on P7-BE-002. Verify constraints and migration/reconciliation fixtures.

## UI Tasks
- P7-UI-001, SEQUENTIAL: add template approval modal, schedule/publish status, failures, reconciliation, and authorized recovery views. Areas: messaging/dashboard templates/scripts. Depends on P7-BE-002. Verify exact payload/destination/time/hash display and recovery browser tests.

## n8n Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P7-N8N-001 | Implement reviewed reusable grant, account, rate-limit, media, error, callback, and dead-letter sub-workflows. | SEQUENTIAL | `n8n/workflows/` | P3-N8N-001, P7-BE-001 | Versioned reusable workflow JSON. | Mocked provider contract and redaction tests. |
| P7-N8N-002 | Implement `content.publish`, scheduled dispatch, and `analytics.aggregate` workflows. | SEQUENTIAL | `n8n/workflows/` | P7-N8N-001/P7-BE-002 | Named delivery workflows. | Timeout/rate-limit/ambiguous-result/callback test runs. |

## Agent / AI Tasks
- P7-AI-001, SEQUENTIAL: activate consequential `content.schedule` and `content.publish` Tool Gateway schemas. Depends on P7-BE-002/P7-N8N-002. Verify exact approval fingerprint/expiry is mandatory and Agent only receives command reference.

## Security Tasks
- P7-SEC-001, SEQUENTIAL: enforce one-time execution grants, callback signatures, delivery idempotency, n8n network/credential isolation, and redacted execution retention. Depends on P7-BE-001/P7-N8N-001. Verify forgery/replay/altered payload/credential leak tests.

## Tests
- P7-TST-001, PARALLEL-SAFE: mocked Telegram fixtures for timeout, rate limit, ambiguous delivery, duplicate callback, and reconciliation lookup.
- P7-TST-002, SEQUENTIAL: E2E approve/schedule/publish-once/recover failure pilot. Depends on all P7 delivery tasks.

## Acceptance Criteria
- Django shows authoritative command/publication state; user approves exact consequence and can recover classified failures.
- Pilot never produces a duplicate known delivery; direct path is disabled only after parity, reconciliation, and recovery drill evidence.

## Definition of Done
All P7 IDs pass and Telegram pilot acceptance explicitly approves migration parity.

## Rollback Strategy
Disable n8n schedule/delivery flags, stop dispatch, pin workflow versions, and re-enable direct publisher for approved legacy operations. Preserve ambiguous commands for reconciliation; never auto-retry them.

## Dependencies
Phase 1, 3, and 6 acceptance plus n8n/publish-policy gates.

## Decisions/Gates Required Before Starting
- n8n deployment/queue/callback/credential and retention model.
- Publish/schedule approval and any delegation policy.
- Telegram idempotency/reconciliation method.

## Risks
Duplicate posts, forged callbacks, provider limits, and n8n downtime. Mitigate through immutable fingerprints, grants, reconciliation, rate limits, and dead letters.

## Explicitly Out of Scope
Other platform publishing, arbitrary workflows, MTProto, React, MCP.

## Development Checklist
- [ ] P7-BE-001
- [ ] P7-BE-002
- [ ] P7-BE-003
- [ ] P7-DB-001
- [ ] P7-UI-001
- [ ] P7-N8N-001
- [ ] P7-N8N-002
- [ ] P7-AI-001
- [ ] P7-SEC-001
- [ ] P7-TST-001
- [ ] P7-TST-002

## Reviewer Checklist
- [ ] Django remains source of truth and approval binding is immutable.
- [ ] Workflow JSON, callback security, retries, and reconciliation are reviewed.
- [ ] Direct delivery retirement is not proposed before pilot evidence.

## QA Checklist
- [ ] Exact approval, schedule, publish-once, timeout, duplicate callback, and recovery scenarios pass.
- [ ] Product status is correct without querying n8n.
- [ ] Rollback drill re-enables legacy path safely.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates delivery migration, Reviewer validates consequence/security/reconciliation design, QA runs the pilot and recovery drill, then acceptance unlocks Phase 8.
