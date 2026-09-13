# Phase 0 - Baseline, Safety, Compatibility

## Objective
Establish a reproducible, secure, characterized baseline for existing Django content and Telegram behavior before V2 state or workflow changes.

## Starting Preconditions
- Architecture freeze is accepted; no later phase may start.
- Current repository and production migration state can be inspected without modifying production data.

## Architecture Constraints
- Preserve all active routes and Django-template/vanilla-JavaScript flows.
- Do not activate the persisted n8n `ai` workflow; export it only as evidence.
- No React, MCP, Celery activation, or V2 product feature is introduced.

## Exact Deliverables
- Versioned API/route compatibility inventory, characterization suite, CI baseline, feature-flag convention, correlation/error contract, n8n workflow source-control standard, secret-rotation record, and backup/migration rehearsal evidence.

## Implementation Workstreams
Backend/API baseline, test/CI, deployment safety, workflow governance, and migration readiness. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P0-BE-001 | Inventory routed APIs, template consumers, and legacy/orphaned paths without changing routes. | PARALLEL-SAFE | `main/urls.py`, `*/urls.py`, `templates/`, `static/assets/scripts/` | None | Reviewed route/consumer matrix in `docs/api/`. | Route matrix matches automated URL discovery and browser-script references. |
| P0-BE-002 | Define versioned V2 error, correlation-ID, and feature-flag interfaces without enabling V2 features. | SEQUENTIAL | Add `common/`; `main/settings.py`, middleware, URLs | P0-BE-001 | Documented contract and additive implementation. | Unit tests show header/error behavior and legacy response compatibility. |

## Database / Migration Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P0-DB-001 | Reconcile migration inventory, including untracked `content/migrations/0019_alter_contentitem_status.py`; record a production-like migration rehearsal. | BLOCKED-BY-GATE | All `*/migrations/`, deployment database | Backup/rehearsal access | Signed migration inventory and rehearsal log. | `showmigrations`, forward migration, and restore exercise evidence. |

## UI Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P0-UI-001 | Add no new product UI; capture active template/API behavior in browser smoke fixtures. | PARALLEL-SAFE | `templates/dashboard/`, `templates/messaging_automation/`, scripts | P0-BE-001 | Repeatable browser smoke specification. | Existing create-content and Telegram pages load and use documented routes. |

## n8n Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P0-N8N-001 | Export/archive the inactive legacy workflow and establish reviewed JSON naming, redaction, manifest, and deployment rules. | PARALLEL-SAFE | `n8n/workflows/`, `n8n/data/database.sqlite` | n8n access | Archived evidence export and workflow governance document. | Export contains no secrets; no workflow is activated; manifest review passes. |

## Agent / AI Tasks
No Agent is enabled. P0-BE-002 defines only the future tool-envelope/effect-class contract.

## Security Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P0-SEC-001 | Rotate exposed credentials and move configuration to approved secret references/environment injection. | BLOCKED-BY-GATE | `.env`, settings, Compose, n8n credentials | Deployment-owner and secret-store access | Rotation record; tracked secrets removed; deployment variables documented. | Secret scan is clean; old credentials are revoked; smoke checks use new references. |

## Tests
- P0-TST-001, PARALLEL-SAFE: add characterization tests for authentication, content create/chat/generation persistence, Telegram verify/publish/logging, and error shapes. Areas: `*/tests/`. Verify in CI against PostgreSQL.
- P0-TST-002, SEQUENTIAL: add CI commands for migrations, unit/integration suites, static checks, and browser smoke tests. Depends on P0-TST-001. Verify a clean checkout pipeline.

## Acceptance Criteria
- Active and compatibility routes are inventoried; baseline tests run in CI.
- No exposed active secret remains in tracked source/configuration, and backup/rehearsal evidence exists.
- Workflow governance exists and no V2 component uses the legacy n8n workflow.

## Definition of Done
All P0 task IDs are accepted, required gates are evidenced, and the Phase 0 acceptance gate is signed.

## Rollback Strategy
Revert additive middleware/CI configuration if it disrupts legacy behavior; retain route inventory, test fixtures, exported workflow evidence, and backups. Do not restore revoked secrets.

## Dependencies
Architecture freeze only. P1-P8 are blocked by Phase 0 acceptance; documentation-only preparation is allowed.

## Decisions/Gates Required Before Starting
- Deployment-owner access for secret rotation and backup/rehearsal.
- CI runner and secret-storage approach.

## Risks
Characterization can expose currently broken AI generation contracts or stale browser endpoints. Record deviations; do not silently redefine legacy behavior.

## Explicitly Out of Scope
Workspace schema, content-history schema, n8n integration, React, MCP, and feature replacement.

## Development Checklist
- [ ] P0-BE-001
- [ ] P0-BE-002
- [ ] P0-DB-001
- [ ] P0-UI-001
- [ ] P0-N8N-001
- [ ] P0-SEC-001
- [ ] P0-TST-001
- [ ] P0-TST-002

## Reviewer Checklist
- [ ] Compatibility inventory distinguishes active from orphaned paths.
- [ ] No contract breaks or workflow activation occurred.
- [ ] Secret rotation and migration rehearsal evidence is valid.

## QA Checklist
- [ ] CI passes from a clean checkout.
- [ ] Active content and Telegram smoke paths match characterization results.
- [ ] No secret is emitted by logs, exports, or test reports.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates all P0 tasks, Reviewer approves compatibility/security evidence, QA validates CI and smoke behavior, then the acceptance owner unlocks Phase 1.
