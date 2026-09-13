# Phase 1 - Workspace, Policy, Execution Ledger

## Objective
Make Django the tested workspace authorization and durable-command boundary for all V2 work.

## Starting Preconditions
- Phase 0 acceptance passed.
- Workspace semantics, launch roles, and default-workspace mapping are approved.

## Architecture Constraints
- Django/PostgreSQL owns tenancy, policy, approvals, commands, audit, and callbacks.
- Legacy owner-based routes remain compatible during additive migration.
- n8n receives no user session, database authority, or broad credentials.

## Exact Deliverables
- Workspace/membership/policy model, default-workspace backfill, execution ledger/outbox/audit/approval records, signed callback grant contract, tool registry preflight, and isolation test suite.

## Implementation Workstreams
Tenancy/policy, execution ledger, legacy mapping, APIs/templates, and tests. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P1-BE-001 | Create `workspaces` app with workspace context resolution, membership roles, and policy service. | SEQUENTIAL | Add `workspaces/`; `main/settings.py`, `main/urls.py` | P0 accepted, role gate | Typed workspace/policy API. | Role-matrix unit tests and request-context tests. |
| P1-BE-002 | Create `automation` and `audit` apps for commands, approvals, outbox, executions, dead letters, and audit events. | PARALLEL-SAFE | Add `automation/`, `audit/` | P0 accepted | Domain services with explicit state transitions. | Transaction, idempotency, and append-only audit tests. |
| P1-BE-003 | Add internal tool registry/preflight and callback grant validation; do not run an Agent or n8n workflow. | SEQUENTIAL | `automation/`, `workspaces/`, API routes | P1-BE-001, P1-BE-002 | Versioned tool envelope and signed callback interface. | Schema, scope, expiry, and replay tests. |

## Database / Migration Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P1-DB-001 | Add additive Workspace, Membership, policy, approval, command, outbox, execution, dead-letter, and audit tables with UUIDs/indexes/constraints. | SEQUENTIAL | New app migrations | P1-BE-001, P1-BE-002 | Expand-only migrations. | Forward/reverse migration tests on production-like snapshot. |
| P1-DB-002 | Add nullable workspace links and backfill default workspaces for owned legacy entities; reconcile counts. | SEQUENTIAL | campaign/content/research/platform/messaging/AI migrations and command | P1-DB-001 | Mapping report and compatibility links. | Null/count reconciliation and tenant-isolation queries. |

## UI Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P1-UI-001 | Add workspace context indicator/selector only for multi-workspace membership; preserve legacy pages under default context. | SEQUENTIAL | dashboard base template, scripts, workspace APIs | P1-BE-001, P1-DB-002 | Feature-flagged template UI. | Browser tests for default and switched workspaces. |

## n8n Tasks
No operational workflow. P1-BE-003 supplies the required manifest, grant, and signed-callback contract for later workflows.

## Agent / AI Tasks
No LLM Agent. P1-BE-003 registers schemas/policy preflight only.

## Security Tasks
- P1-SEC-001, SEQUENTIAL: correct object authorization for V2-equivalent access paths and prohibit unscoped IDs. Areas: campaign/content/research/messaging APIs. Depends on P1-BE-001/P1-DB-002. Verify cross-workspace denial tests.

## Tests
- P1-TST-001, PARALLEL-SAFE: workspace membership and resource-policy matrix fixtures. Verify all roles and default mappings.
- P1-TST-002, SEQUENTIAL: command/outbox atomicity, approval fingerprint/expiry, callback signature/replay, and audit redaction integration tests. Depends on P1-BE-002/P1-BE-003.

## Acceptance Criteria
- Every V2-addressable record has exactly one workspace mapping.
- Cross-workspace direct API, tool, and callback access is denied.
- Consequential command creation requires valid policy/approval and produces audit/outbox records atomically.

## Definition of Done
All P1 IDs pass review/QA and workspace/policy/ledger acceptance evidence is recorded.

## Rollback Strategy
Disable workspace enforcement flags and use legacy ownership checks; retain backfilled mappings and ledger data. Never reverse a production backfill in a way that orphans records.

## Dependencies
Phase 0 acceptance; approved workspace semantics and roles.

## Decisions/Gates Required Before Starting
- Workspace represents the approved organization/account boundary.
- Launch role set and membership administration are final.

## Risks
Legacy APIs with global primary-key fetches can bypass isolation; no V2 resource may expose before P1-SEC-001 passes.

## Explicitly Out of Scope
Content History, connection import, RAG, Agent execution, publishing migration, React, and MCP.

## Development Checklist
- [ ] P1-BE-001
- [ ] P1-BE-002
- [ ] P1-BE-003
- [ ] P1-DB-001
- [ ] P1-DB-002
- [ ] P1-UI-001
- [ ] P1-SEC-001
- [ ] P1-TST-001
- [ ] P1-TST-002

## Reviewer Checklist
- [ ] Expand/migrate compatibility and UUID/constraint design are correct.
- [ ] Policy decisions and callbacks cannot bypass Django.
- [ ] Backfill reconciliation and authorization coverage are complete.

## QA Checklist
- [ ] Role matrix and workspace-switch browser tests pass.
- [ ] Duplicate/replayed callback and approval cases are rejected.
- [ ] Legacy pages retain default-workspace behavior.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates tenancy and ledger work, Reviewer validates policy/migration boundaries, QA proves isolation and legacy compatibility, then acceptance unlocks Phase 2.
