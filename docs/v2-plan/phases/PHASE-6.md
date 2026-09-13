# Phase 6 - AI Content Agent & Generation

## Objective
Provide a bounded AI Content Agent that creates validated, cited text drafts and reviewable visual assets without external side effects.

## Starting Preconditions
- Phase 5 acceptance passed; Phase 1-4 foundations remain accepted.
- LLM, visual, and embedding providers; residency, budget, and platform validation rules are approved.

## Architecture Constraints
- Agent uses Django Tool Gateway only; no raw URLs, n8n webhooks, SQL, credentials, or provider APIs.
- Generation creates immutable draft versions/assets; it never overwrites approved work.
- Existing chat stays available until V2 parity is accepted; React and MCP are excluded.

## Exact Deliverables
- AgentRun/ToolInvocation/evaluation data, provider adapters, structured briefs, validated draft/asset flow, activity/review UI, compatibility projection, and allowed read/draft tools.

## Implementation Workstreams
Provider adapters, Agent runtime, generation validation, asset lifecycle, template UI, legacy parity, security, and evaluation. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P6-BE-001 | Create provider adapter interfaces and repair AI client method mismatches only behind adapters. | SEQUENTIAL | `integrations/`, `ai/clients/`, `ai/services/` | Provider gate | Stable text/image/embedding contracts. | Fake-provider and normalized-error tests. |
| P6-BE-002 | Create Agent runtime/run/tool-invocation services with bounded context, tool allow-list, and activity state. | SEQUENTIAL | Add `agent/`, automation/memory/history | P1, P4, P5 accepted | Workspace-scoped Agent execution service. | Tool scope/effect/schema tests. |
| P6-BE-003 | Implement structured brief, text draft/version creation, citation/similarity/platform validation, and legacy projection pilot. | SEQUENTIAL | Add `generation/`, content history, existing chat view | P6-BE-001/P6-BE-002 | Validated immutable draft flow. | Validator, immutability, and legacy parity tests. |

## Database / Migration Tasks
- P6-DB-001, SEQUENTIAL: add AgentRun, ToolInvocation, GenerationEvaluation, prompt/provider revision, structured brief, validation, cost/latency fields; link versions/assets. Area: agent/generation migrations. Depends on P6-BE-002. Verify migration and retention/redaction tests.

## UI Tasks
- P6-UI-001, SEQUENTIAL: add template Agent activity, evidence/assumptions/tool status, version comparison, edit/review, and visual review screens. Areas: `create_content_ai.html`, dashboard templates/scripts. Depends on P6-BE-003. Verify browser review/approval and feature-flagged legacy parity.

## n8n Tasks
- P6-N8N-001, BLOCKED-BY-GATE: implement `visual.generate_asset` only when provider/media transfer requires n8n; otherwise record Django-adapter selection. Area: `n8n/workflows/`. Depends on visual-provider decision, P1-BE-003. Verify callback returns asset metadata only.

## Agent / AI Tasks
- P6-AI-001, SEQUENTIAL: activate `content.generate_draft` and prior read/draft tools with explicit schemas/results. Depends on P6-BE-002/P6-BE-003. Verify no consequential tool can be invoked.
- P6-AI-002, SEQUENTIAL: activate `visual.generate_asset` through selected adapter/workflow and bind output to ContentAsset review state. Depends on P6-N8N-001 or adapter decision. Verify asset hash/authorization tests.

## Security Tasks
- P6-SEC-001, SEQUENTIAL: enforce prompt/data retention redaction, tool allow-list, untrusted-evidence separation, cost/budget controls, and workspace scope. Depends on P6-BE-002. Verify injection, leakage, denial, and quota tests.

## Tests
- P6-TST-001, PARALLEL-SAFE: fake LLM/provider fixtures for valid/invalid citations, length, platform rule, similarity, timeout, and provider error cases.
- P6-TST-002, SEQUENTIAL: Agent/tool/approval boundary, draft immutability, visual asset, cost, and legacy chat parity integration/E2E suite. Depends on enabled generation tasks.

## Acceptance Criteria
- Authorized users create/review cited drafts and visual assets with visible Agent activity.
- Agent cannot cross workspace boundaries or initiate consequential actions; approved versions remain immutable.

## Definition of Done
All enabled P6 tasks are accepted and text/visual generation has documented provider and legacy-parity evidence.

## Rollback Strategy
Disable Agent/generation flags and return users to legacy chat; retain runs, versions, assets, and evaluations for audit/export.

## Dependencies
Phase 5 acceptance; provider/residency/budget/platform-rule gates.

## Decisions/Gates Required Before Starting
- Provider selection and data-processing constraints.
- Cost budgets/quotas and visual asynchronous execution choice.

## Risks
Hallucinations, provider failure, costs, and legacy drift. Use validation, citations, deterministic fakes, feature flags, and compatibility tests.

## Explicitly Out of Scope
Auto-publish, auto-schedule, delegated external action, React, MCP.

## Development Checklist
- [ ] P6-BE-001
- [ ] P6-BE-002
- [ ] P6-BE-003
- [ ] P6-DB-001
- [ ] P6-UI-001
- [ ] P6-N8N-001
- [ ] P6-AI-001
- [ ] P6-AI-002
- [ ] P6-SEC-001
- [ ] P6-TST-001
- [ ] P6-TST-002

## Reviewer Checklist
- [ ] Adapter boundary resolves legacy contract drift without broad rewrites.
- [ ] Tool allow-list, evidence, validators, and immutable versions are correct.
- [ ] Visual workflow selection preserves Django authority.

## QA Checklist
- [ ] Draft, revise, approve, asset review, failure, and budget paths pass.
- [ ] Injection and cross-workspace scenarios are denied.
- [ ] Existing chat remains usable during pilot.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates Agent/generation work, Reviewer validates model/tool safety and lineage, QA validates end-to-end authoring and parity, then acceptance unlocks Phase 7.
