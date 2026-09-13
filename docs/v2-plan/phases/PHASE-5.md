# Phase 5 - Content Intelligence, Brainstorming & Content Map

## Objective
Deliver evidence-backed, reversible recommendations, ideas, and Content Map proposals without scheduling or publishing effects.

## Starting Preconditions
- Phase 3 and Phase 4 acceptance passed, plus Phase 1/2 foundations.
- Intelligence success measures, feedback rubric, research provider, and retention policy are approved.

## Architecture Constraints
- Django computes/stores facts, recommendations, proposals, and approval transitions.
- LLM outputs are proposals with evidence/assumptions, never authority or external effects.
- Django templates/vanilla JavaScript remain the UI.

## Exact Deliverables
- Metric/recommendation snapshots/outcomes, IdeaProposal/Feedback, ContentMap/Revision/Slot, deterministic coverage validation, LLM proposal services, research workflow contract when approved, and template UI.

## Implementation Workstreams
Intelligence facts, map/idea domain, proposal services, research acquisition, UI, policy, and evaluation. One Development Agent integrates all workstreams.

## Backend Tasks
| ID | Task | Class | Area/files | Depends on | Expected output | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| P5-BE-001 | Create intelligence snapshot/recommendation/outcome services with evidence, freshness, confidence, and known gaps. | SEQUENTIAL | Add `intelligence/`, content history/memory | P3/P4 accepted | Explainable recommendation API. | Evidence completeness and deterministic fact tests. |
| P5-BE-002 | Create brainstorming idea/feedback and Content Map/revision/slot services with explicit transitions. | PARALLEL-SAFE | Add `brainstorming/`, `planning/` | P2 accepted, policy foundation | Reversible proposal aggregates. | State/permission/slot-rule tests. |
| P5-BE-003 | Implement deterministic coverage/similarity validation and promote approved ideas/slots to draft content records only. | SEQUENTIAL | planning/brainstorming/content history | P5-BE-002 | Validated promotion service. | No-schedule/no-publish and provenance tests. |

## Database / Migration Tasks
- P5-DB-001, SEQUENTIAL: add snapshots/outcomes, ideas/feedback, maps/revisions/slots with workspace/campaign/content links. Area: new app migrations. Depends on P5-BE-001/P5-BE-002. Verify migration and relational constraints.

## UI Tasks
- P5-UI-001, SEQUENTIAL: add Django-template Intelligence evidence views, Brainstorm board, and Content Map review/calendar/coverage screens. Areas: dashboard templates/scripts. Depends on P5-BE-001/P5-BE-003. Verify browser proposal, feedback, approve, and promote flows.

## n8n Tasks
- P5-N8N-001, BLOCKED-BY-GATE: implement `research.discover_sources` and optional `analytics.aggregate` from reviewed contracts, using reusable rate-limit/normalization/callback flows. Area: `n8n/workflows/`. Depends on research/provider gate, P1-BE-003, P3-N8N-001. Verify mocked provider contracts and Django persistence.

## Agent / AI Tasks
- P5-AI-001, SEQUENTIAL: expose `brainstorm.generate_options` and `content_map.create_or_rebalance` with bounded evidence and fake-LLM validation. Depends on P5-BE-002/P5-BE-003/P4-AI-001. Verify results create proposals only.
- P5-AI-002, BLOCKED-BY-GATE: expose `research.discover_sources` only after P5-N8N-001. Verify tool schema/policy/job-reference tests.

## Security Tasks
- P5-SEC-001, SEQUENTIAL: enforce workspace/campaign policy on recommendations, ideas, maps, and promotions; redact research/provider payloads. Depends on P5-BE-001/P5-BE-002. Verify cross-workspace and effect-boundary tests.

## Tests
- P5-TST-001, PARALLEL-SAFE: create deterministic history/metric/coverage fixtures and stored evaluation rubric fixtures.
- P5-TST-002, SEQUENTIAL: test evidence, citation, map transitions, feedback retention, fake-LLM schema validation, and prohibition on consequential effects. Depends on all enabled workstreams.

## Acceptance Criteria
- Recommendations disclose evidence/freshness/confidence/gaps.
- Users can manage ideas/maps and promote approved work to drafts; no proposal schedules, publishes, or contacts a platform.

## Definition of Done
All enabled P5 tasks pass and each gated research task is either accepted or explicitly excluded by recorded gate decision.

## Rollback Strategy
Disable intelligence/planning/brainstorm flags; retain user-created ideas, maps, snapshots, and promoted drafts.

## Dependencies
Phase 3/4 acceptance, intelligence/rubric/research gates.

## Decisions/Gates Required Before Starting
- Success metrics and labeled feedback governance.
- Research provider, retained source content, and whether source acquisition is enabled.

## Risks
Opaque recommendations can erode trust; require evidence and never automate decisions. Sparse metrics must produce known gaps rather than false precision.

## Explicitly Out of Scope
Scheduling, publishing, autonomous optimization, training models, React, MCP.

## Development Checklist
- [ ] P5-BE-001
- [ ] P5-BE-002
- [ ] P5-BE-003
- [ ] P5-DB-001
- [ ] P5-UI-001
- [ ] P5-N8N-001
- [ ] P5-AI-001
- [ ] P5-AI-002
- [ ] P5-SEC-001
- [ ] P5-TST-001
- [ ] P5-TST-002

## Reviewer Checklist
- [ ] Evidence and uncertainty are visible and persisted.
- [ ] Map/idea transitions cannot create external effects.
- [ ] Research workflow and tool remain Django-authorized.

## QA Checklist
- [ ] Recommendation, brainstorm, map, feedback, and promotion flows pass.
- [ ] Permission and no-consequence tests pass.
- [ ] Research behavior is absent when its gate is not accepted.

## Handoff
**DEVELOPER -> REVIEWER -> QA -> PHASE ACCEPTANCE**: Development Agent integrates all proposal work, Reviewer confirms evidence/effect boundaries, QA validates UI and no-consequence paths, then acceptance unlocks Phase 6.
