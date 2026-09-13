# Phase 8 - Product Transition, Observability & MCP Readiness

## Objective
Complete V2 rollout, operational controls, controlled legacy retirement, and frozen MCP-compatible Tool Gateway contracts without implementing MCP.

## Starting Preconditions
- Phase 7 acceptance passed; all prior phases are accepted.
- Observability, retention/export, and production topology decisions are approved.

## Architecture Constraints
- Django templates/vanilla JavaScript remain the V2 UI; do not add React.
- MCP server/adapter/client/transport is out of scope; validate contract compatibility only.
- Legacy paths are retired only after documented parity, retention, export, reconciliation, telemetry, and rollback windows.

## Exact Deliverables
- Rollout/flag plan, structured observability/alerts, retention/export controls, workflow deployment/backup drills, tool-contract conformance suite, security/load/chaos evidence, and accepted retirement decisions.

## Implementation Workstreams
Operations/observability, rollout/retirement, n8n lifecycle, contract conformance, template UI completion, and reliability/security testing. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P8-BE-001 | Add correlation/causation-aware structured telemetry for requests, tools, commands, callbacks, providers, and domain transitions. | SEQUENTIAL | common/automation/audit/settings | P7 accepted, observability gate | Exported metrics/log/trace contract. | Redaction and correlation integration tests. |
| P8-BE-002 | Freeze/version V2 public and Tool Gateway schemas; add deprecation behavior for approved legacy replacements. | SEQUENTIAL | API modules, docs/contracts | P8-BE-001 | Versioned conformance fixtures and deprecation inventory. | Contract compatibility suite. |
| P8-BE-003 | Implement approved retention/export/archive jobs and feature-flag rollout/retirement controls. | SEQUENTIAL | domain apps, settings, ops scripts | Retention gate, P8-BE-002 | Auditable retention and rollout controls. | Retention/export/restore and flag rollback tests. |

## Database / Migration Tasks
- P8-DB-001, BLOCKED-BY-GATE: add only measured indexes/partitions/retention markers. Areas: all V2 migrations. Depends on production load evidence and retention policy. Verify query plan/load and reversible migration rehearsal.

## UI Tasks
- P8-UI-001, SEQUENTIAL: complete V2 Django-template status/recovery/retirement notices and remove orphaned stepper assets only after approved telemetry. Areas: templates/static scripts. Depends on P8-BE-003. Verify responsive/accessibility and replacement-path browser tests.

## n8n Tasks
- P8-N8N-001, SEQUENTIAL: establish controlled workflow deployment, version pinning, capacity/rate limits, redacted retention, backup/restore, monitoring, and rollback runbooks. Areas: `n8n/workflows/`, Compose, operations docs. Depends on P7 accepted. Verify deployment and restore drills.

## Agent / AI Tasks
- P8-AI-001, SEQUENTIAL: freeze tool schemas and run framework-independent MCP-compatibility conformance only. Depends on P8-BE-002. Verify no MCP endpoint, transport, or discovery is created.

## Security Tasks
- P8-SEC-001, SEQUENTIAL: execute final credential-leak, approval replay, callback forgery, tenant isolation, retention, and prompt-injection security review. Depends on P8-BE-001/P8-BE-003/P8-N8N-001. Verify documented remediation/accepted residual-risk record.

## Tests
- P8-TST-001, PARALLEL-SAFE: load/chaos fixtures for ingestion, retrieval, provider/n8n failure, and workflow callback disorder.
- P8-TST-002, SEQUENTIAL: full migration, browser/API/Agent/n8n E2E regression, accessibility, backup/restore, and rollback drill suite. Depends on all P8 operational tasks.

## Acceptance Criteria
- Alerts cover command failures, dead letters, ingestion lag, retrieval latency, provider limits, and cross-workspace denials.
- Legacy retirement is supported by evidence and reversible; Tool Gateway is frozen/MCP-compatible with no MCP implementation.

## Definition of Done
All P8 IDs are accepted, operational drills pass, and V2 rollout acceptance is signed.

## Rollback Strategy
Disable flags per workspace, pin known workflow versions, restore compatibility projections, stop new commands, and restore from tested backup. Never delete canonical V2 history, approvals, commands, or audit records as rollback.

## Dependencies
All prior phase acceptances plus observability, retention/export, and production topology gates.

## Decisions/Gates Required Before Starting
- Observability provider/ownership and alert routing.
- Data retention/deletion/export and production backup/restore ownership.
- Evidence threshold for legacy retirement.

## Risks
Premature retirement, insufficient monitoring, cost growth, and future MCP boundary erosion. Gate retirement, enforce budgets, and preserve Django-only tool access.

## Explicitly Out of Scope
React implementation, MCP implementation, new product features, unapproved integration expansion.

## Development Checklist
- [ ] P8-BE-001
- [ ] P8-BE-002
- [ ] P8-BE-003
- [ ] P8-DB-001
- [ ] P8-UI-001
- [ ] P8-N8N-001
- [ ] P8-AI-001
- [ ] P8-SEC-001
- [ ] P8-TST-001
- [ ] P8-TST-002

## Reviewer Checklist
- [ ] Observability, retention, and retirement evidence is sufficient.
- [ ] Tool schema freeze is MCP-compatible without an MCP implementation.
- [ ] No React/MCP or unapproved feature work was introduced.

## QA Checklist
- [ ] Full regression, load/chaos, security, accessibility, backup/restore, and rollback drills pass.
- [ ] Alerts fire for defined failure conditions.
- [ ] Legacy replacements and retirement notices work in templates.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates operational transition work, Reviewer validates retirement/contract boundaries, QA executes reliability and rollback drills, then V2 acceptance closes the program.
