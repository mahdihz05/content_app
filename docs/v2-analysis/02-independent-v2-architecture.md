# Architecture Decision

Adopt a modular Django application backed by PostgreSQL as the V2 system of record, with a React client as the target product UI and n8n as an external-work orchestration layer. Preserve the existing campaign, content item, generated-content, research-source, chat, platform-account, and Telegram publishing capabilities, but replace their implicit JSON-field workflows and direct side effects with explicit domain records and commands.

Use **Approach A now**: Application Agent -> authenticated native/tool-based n8n workflows. Django owns the tool catalog, authorization, durable command, state transition, and audit record; n8n receives only a scoped workflow invocation. This is the least operationally complex path and keeps the Agent, n8n, and application authorization model under one control plane.

Keep **Approach B optional later**: Application Agent -> MCP -> n8n exposed tools/workflows. Do not make MCP the V2 runtime dependency. Introduce an application-owned tool contract now, then expose the same contracts through an MCP server when third-party MCP clients, cross-product agents, or independently deployable tool discovery have a real need. MCP must not bypass Django authorization or permit direct access to arbitrary n8n webhooks.

The current repository supports this direction: Django and PostgreSQL already hold campaigns, content, generations, research sources, chat sessions, social accounts, and Telegram publish logs; n8n is already deployed but not application-integrated. The checked-in UI is Django templates/static JavaScript rather than a React application, so a React client should be introduced incrementally behind stable Django APIs rather than by a big-bang UI replacement.

# Target Architecture

```text
React client / existing Django UI
             |
             | authenticated API and realtime job updates
             v
Django modular monolith ---------------------------------------------------+
  Workspace and identity | Content domain | Intelligence | Agent runtime    |
  Authorization          | History        | Memory/RAG   | Tool gateway     |
  Command/outbox         | Audit          | Media        | Integration API  |
             |                         |                              |
             | PostgreSQL              | object storage               |
             | relational state        | originals and generated media|
             v                         v                              |
       PostgreSQL + pgvector       provider APIs                       |
             ^                         ^                              |
             |                         |                              |
             +------------- n8n worker/orchestrator ------------------+
                              | connector APIs, schedules, polling,
                              | callbacks, retries and transforms
                              v
                      connected platforms and services
```

Use PostgreSQL with the `pgvector` extension for the initial vector store. Keep vector rows, source metadata, permissions, and transactional state colocated. Store large source files and generated images in object storage; PostgreSQL stores immutable asset metadata and signed-access references. A dedicated vector database is a later scale decision, not a V2 prerequisite.

The application boundary is workspace-first. Every content, memory, connection, content-map, action, job, asset, and retrieval record belongs to a workspace. Existing user-owned records are migrated into a default workspace for that user or account.

# Component Responsibilities

**Django.** Django is the system of record and policy enforcement point. It owns identity, workspaces, memberships, roles, connected-account metadata and encrypted credentials references, content lifecycle, version history, planning, approval records, job/command records, n8n invocation records, provider configuration, audit events, analytics facts, and API contracts. It validates all inbound n8n callbacks, issues short-lived workflow credentials, and is the only component allowed to make authoritative domain-state transitions.

**React client.** The target client owns interactive authoring, review, approval, planning, search, and transparent Agent activity display. It calls Django only. Existing Django pages can consume the same APIs during transition; they do not call n8n or providers directly.

**n8n.** n8n owns connector-oriented, long-running, scheduled, fan-out, polling, and retryable integration steps. It may transform data and retain operational execution data for a limited retention period, but it is not a business database and must not be queried by the product for authoritative status.

**Provider adapters.** Isolate LLM, embedding, image generation, web-search, object-storage, and social-platform API differences behind Django adapter interfaces and n8n connector workflows. No domain service should depend on a vendor response schema.

**Object storage.** Store raw imported payloads, original documents, rendered media, and generated visual assets. Persist content hashes, MIME type, lifecycle, attribution, provider response references, and ownership in Django.

# Agent Architecture

The AI Content Agent is an application service, not a privileged autonomous process. It receives the authenticated actor, workspace, conversation or task context, a bounded context bundle, and an allow-listed set of typed tools. It plans, asks clarifying questions, retrieves evidence, creates drafts and proposals, and explains intended consequences. Django executes policy decisions before each tool call.

Tool calls use versioned JSON schemas with: `tool_name`, `tool_version`, workspace and actor context, command ID, idempotency key, declared effect class, validated inputs, and an explicit result schema. The Agent cannot invoke raw URLs, arbitrary n8n workflows, SQL, or platform credentials.

Approach A is implemented as an internal Django tool gateway. Read-only and draft-producing tools can return synchronously when fast. Asynchronous and side-effecting tools create an `AutomationCommand`, invoke a named n8n workflow through a private authenticated endpoint, and return a job/action reference. n8n reports progress and result to a signed Django callback endpoint. The Agent reads the resulting domain state rather than treating the n8n response as truth.

Prepare for MCP by keeping tool definitions independent of the Agent framework. A future MCP server is an adapter over Django's tool gateway, with per-tool scopes and the same command/approval flow. It may call n8n through Django only; n8n webhook URLs, credentials, and operational APIs are never published as MCP tools.

# n8n Architecture

Use one workflow per stable integration capability, plus reusable sub-workflows for common behavior: validate command envelope, retrieve a scoped connection, pagination/rate limiting, media download/upload, provider error normalization, callback delivery, and dead-letter notification. Version workflows as exported source-controlled JSON and deploy through a controlled CI/CD path; do not rely on manually edited production workflows.

Every workflow starts from a Django command envelope or a schedule controlled by Django. Scheduled polling first asks Django which active connections and cursors are eligible, then reports observations back using idempotent upsert APIs. n8n may maintain its own execution database and credentials store, but secrets are scoped to named integrations and are never copied into content records or logs.

Operate n8n in queue mode with separate worker capacity for ingestion, publishing, and expensive media work when production load warrants it. Apply concurrency and rate limits per provider account. Keep execution retention short and redact request bodies that contain content, tokens, or personal data; Django retains the durable audit trail.

The execution lifecycle is: Django validates request and policy -> writes command and outbox event in one transaction -> dispatches a named workflow -> n8n acknowledges and executes -> n8n sends signed progress/result callbacks -> Django validates callback, idempotently records the result, applies the domain transition, and emits UI/audit events. Commands remain pending until Django records a terminal outcome. Retry only transient, classified failures with exponential backoff, jitter, attempt limits, and provider-aware rate limiting. Never automatically retry an ambiguous external publish without an idempotency key or a reconciliation lookup; send exhausted commands to a Django-visible dead-letter queue for authorized recovery.

# Workflow / Tool Catalog

| Tool / workflow | Effect | Owner | Notes |
| --- | --- | --- | --- |
| `content.search_history` | Read | Django | Filtered search across normalized imported and first-party content. |
| `memory.retrieve` | Read | Django | Permission-filtered hybrid retrieval with citations. |
| `research.discover_sources` | Read/create | n8n | Search/fetch/normalize sources; Django persists selected sources. |
| `connection.ingest_content` | Create | n8n | Cursor-based import of previous content and metrics from one connected account. |
| `connection.refresh_metrics` | Update | n8n | Refreshes performance facts for imported/published content. |
| `content.generate_draft` | Create | Django/LLM | Structured, cited text generation; creates a version, never overwrites approved work. |
| `visual.generate_asset` | Create | n8n or Django adapter | Provider call and object-storage upload; returns asset metadata. |
| `brainstorm.generate_options` | Create | Django/LLM | Produces scored idea proposals, not scheduled content. |
| `content_map.create_or_rebalance` | Create/update | Django/LLM | Produces a plan proposal and coverage analysis. |
| `content.schedule` | Consequential | Django | Creates schedule intent after authorization. |
| `content.publish` | Consequential | n8n | Delivers an approved immutable version to an approved account. |
| `connection.verify` | Consequential | n8n | Verifies ownership/permissions of a connected destination. |
| `analytics.aggregate` | Update | n8n | Scheduled aggregation of provider metrics into Django facts. |

Tools that create drafts, ideas, plans, or internal analysis are reversible. Publishing, scheduling, account connection, credential refresh, deletion, and external communication are consequential. A tool may compose reusable n8n sub-workflows, but a tool must expose one bounded business outcome and a stable input/output contract.

# Content Intelligence

Content intelligence is a Django domain service that combines normalized history, performance metrics, research, workspace memory, brand/profile constraints, and plan coverage. It should emit explainable recommendations with evidence references, confidence, freshness, and known gaps rather than opaque scores.

Store raw metrics as append-only observations with source and collection time. Derive platform-normalized measures such as impressions, reach, engagement, saves, shares, clicks, conversions where available, and rate metrics with the denominator recorded. Maintain score snapshots so a later provider refresh does not rewrite the evidence used for an earlier recommendation.

Generation uses a structured brief: target platform and format, audience, campaign objective, selected Content Map slot, brand constraints, retrieved memory/history/source citations, required claims, prohibited claims, and output schema. The model first returns a draft plus self-reported citations and assumptions; a validator checks schema, length, platform rules, duplicate/similarity thresholds, citation eligibility, and policy constraints before a `ContentVersion` is created.

# History

Model content history as a canonical cross-platform corpus, not as a side effect of current `ContentItem` fields. `ContentRecord` represents one logical item, with origin (`first_party`, `imported`, `manual`), workspace, source account, platform, external ID, canonical URL, content type, published/scheduled times, current state, and immutable source fingerprint. A unique constraint on source account plus external ID prevents duplicate imports.

`ContentVersion` stores each editable or generated text/structured payload, author or producing agent, parent version, status (`draft`, `review`, `approved`, `superseded`), model/prompt revision, retrieval snapshot, and content hash. `Publication` represents each destination attempt and references the approved version and external delivery identifiers. This preserves existing `GeneratedContent` value while replacing a single integer version and JSON blobs with durable lineage.

Ingestion is incremental: authenticate/verify the account, capture a cursor or watermark, fetch pages, normalize platform payloads, upsert content records and media references, store raw payloads in protected object storage where policy allows, record observations, enqueue embeddings, and advance the cursor only after the page commits. Support an initial bounded backfill, manual re-sync, and provider-specific deletion/unavailability semantics.

# Memory / RAG

Workspace Memory is curated knowledge, distinct from the full history corpus. It includes brand voice, products, audiences, policies, editorial rules, approved examples, campaign briefs, uploaded documents, decisions, and optionally approved distilled learnings from history. Memory entries have scope (`workspace`, `campaign`, `content_record`), source/provenance, owner, visibility, freshness/expiry, confidence, and review status.

An ingestion pipeline extracts text, preserves the original asset, chunks deterministically, generates embeddings, and writes `MemoryChunk` rows using pgvector. Each chunk stores source/version IDs, ordinal, token count, embedding model/version, content hash, language, metadata filters, and access scope. Re-embedding creates a new embedding revision; it never silently replaces provenance.

Retrieval is hybrid: permission-filtered metadata query, full-text search, vector nearest-neighbor search, reciprocal-rank fusion, optional reranking, diversity limits, and a bounded token budget. Results always return citations and freshness. The Agent must use only returned workspace-scoped chunks; it cannot query raw embeddings or another workspace's corpus. Imported history is retrievable through a separate corpus selector so it can be included intentionally without turning every historical post into durable brand guidance.

# Brainstorming

Brainstorming takes a defined objective, campaign or map context, platform/format, horizon, constraints, and optional research request. It retrieves a compact evidence pack from memory, history performance, plan coverage, and selected sources; it does not treat model brainstorming as factual research.

The result is a set of `IdeaProposal` records with hook, audience tension, angle, format, CTA hypothesis, supporting evidence, predicted fit, novelty/similarity signal, risks, and suggested Content Map slot. Users can shortlist, reject with a reason, edit, or promote an idea into a planned item. These feedback events are retained for future ranking, but no idea is scheduled or published by brainstorming alone.

# Content Map

The Content Map is the planning aggregate. `ContentMap` defines a workspace/campaign, planning horizon, channels, business objectives, audience segments, content pillars, formats, cadence, and constraints. `ContentMapSlot` represents an intended publication opportunity with time window, platform, pillar, funnel stage, objective, format, status, linked idea/content record, and rationale.

The planning service analyzes historical frequency, recent similarity, pillar/funnel/channel coverage, observed performance, seasonal dates, constraints, and open slots. It returns a proposal with explicit trade-offs and confidence rather than automatically replacing the plan. Users approve map revisions; approved slots create or link draft content records. Calendar scheduling remains a separate consequential operation because a plan is not a publishing instruction.

# Permissions

Use workspace membership roles plus resource-level policy. Suggested baseline roles are owner, admin, editor, contributor, analyst, and viewer. Permissions are evaluated in Django for each resource and tool invocation; n8n receives a narrow execution grant, never the user's broad session or database credentials.

For Agent actions, assign an effect class:

| Effect class | Examples | Authorization behavior |
| --- | --- | --- |
| Read | retrieve history, memory, map, metrics | Allow only within actor's workspace and scopes. |
| Draft | generate text, visual asset, ideas, plan proposal | Allow to users with create/edit rights; label output as AI-produced. |
| Mutate internal | save a version, select sources, alter a map | Enforce edit rights; confirmation when it replaces or archives material work. |
| Consequential | connect account, refresh credentials, schedule, publish, delete, send messages | Require an explicit approval record bound to exact command payload and expiry. |

The UI presents the exact destination, version/asset hash, schedule, expected external effect, and any cost before approval. Django stores an `ActionApproval` containing actor, policy decision, command fingerprint, scope, expiry, and approval method. n8n checks the one-time execution grant supplied by Django. Any material payload, destination, or schedule change invalidates approval. Publish defaults to per-action confirmation; a workspace owner may define narrowly scoped, time-limited delegated publishing policies for named channels and approved content states, all fully audited.

# Observability

Every request, Agent run, tool call, command, approval, n8n invocation, provider call, domain transition, and callback receives correlation and causation IDs. Django maintains append-only `AuditEvent` records with workspace, actor type/id, object reference, action, before/after summaries, policy outcome, trace IDs, and redacted metadata.

`AutomationCommand` is the durable execution ledger: command type/version, validated input hash, idempotency key, status, attempts, workflow/version, external execution ID, callback payload hash, retry timing, result reference, and normalized error. `AgentRun` stores model/provider revision, prompt/template revision, tool plan, retrieval snapshot IDs, token/cost/latency data, and output references; sensitive prompts and source excerpts require controlled retention and redaction.

Export structured logs, traces, and metrics to a centralized observability service. Monitor queue age, workflow success/latency, callback failures, provider and platform rate limits, ingestion lag, publishing outcomes, vector retrieval latency, model cost, approval abandonment, and duplicate suppression. Alert on failed consequence-class commands, dead-letter growth, stale ingestion cursors, and anomalous cross-workspace access denials.

# Data Model Changes

Introduce these V2 aggregates while retaining legacy records during migration:

| Aggregate | Essential records |
| --- | --- |
| Workspace and access | `Workspace`, `WorkspaceMembership`, `Role`, `PolicyGrant` |
| Connections | `PlatformConnection`, `CredentialReference`, `ConnectionCursor`, `ConnectionVerification` |
| Content and delivery | `ContentRecord`, `ContentVersion`, `ContentAsset`, `Publication`, `ContentMetricObservation` |
| Planning and ideas | `ContentMap`, `ContentMapRevision`, `ContentMapSlot`, `IdeaProposal`, `IdeaFeedback` |
| Knowledge | `MemorySource`, `MemoryEntry`, `MemoryChunk`, `EmbeddingRevision`, `RetrievalSnapshot` |
| Execution and safety | `AgentRun`, `ToolInvocation`, `AutomationCommand`, `WorkflowExecution`, `ActionApproval`, `AuditEvent`, `OutboxEvent`, `DeadLetter` |
| Learning | `Recommendation`, `RecommendationOutcome`, `GenerationEvaluation`, `ExperimentAssignment` |

Use UUID public identifiers, UTC timestamps, explicit ownership/workspace foreign keys, immutable version records, JSON only for provider-specific payloads, and relational columns for queried state. Add unique constraints for idempotency keys, external content IDs per connection, content version numbers per record, metric observation source/time dimensions, and one-time approval/execution grants. Encrypt provider tokens outside JSON metadata and rotate them independently.

Future learning and analytics require outcome data, not only generated text: input brief and constraints revision, retrieval/source snapshot, model and prompt revision, tool path, latency, token/provider cost, user edits and approval/rejection reasons, publish destination/time, external platform metrics collected with timestamps, normalized business outcomes where connected, experiment assignment, and recommendation acceptance/dismissal. Store these as attributable events linked to content/version/map/idea IDs, with consent, retention, and privacy controls. Use them first for offline evaluation and reporting; do not train or automate decisions from them until data quality, bias, and governance review are approved.

# Migration Strategy

1. Stabilize the Django API boundary and add workspace tenancy, audit, command, approval, and outbox tables without moving behavior.
2. Backfill a default workspace for each existing owner. Map campaigns, content items, chat sessions, research sources, generated content, Telegram channels, publish logs, and social accounts to that workspace. Preserve legacy IDs as migration references.
3. Introduce `ContentRecord` and `ContentVersion` alongside `ContentItem`. Backfill each content item and its existing generated rows into versions, preserving timestamps, approval state where inferable, research context, and publish history. Make new features write V2 records first while legacy pages read a compatibility projection during the transition.
4. Introduce connection records and ingestion cursors. Begin with Telegram, because publishing and channel records already exist, then add connected platforms only where authorized APIs and data scopes are viable. Run initial history import in small, observable batches and reconcile counts and fingerprints before enabling recurring sync.
5. Enable pgvector, object storage, memory ingestion, and retrieval for curated workspace sources. Keep legacy JSON embeddings readable only until they are re-embedded and provenance has been validated.
6. Implement the Django tool gateway and command/callback protocol. Move one low-risk workflow first, such as research-source discovery or metrics refresh, then history ingestion, asset generation, scheduled publishing, and remaining connector automation. Keep direct Telegram publishing behind a feature flag until n8n delivery parity and reconciliation are proven.
7. Introduce Agent drafting, brainstorming, and map proposals before any delegated external action. Add approval UI and policy enforcement before enabling schedule/publish tools.
8. Deprecate direct provider calls in request handlers and direct publish paths after dual-run reconciliation. Archive legacy fields only after retention, export, and rollback windows are agreed.

Use expand/migrate/contract database changes, feature flags by workspace, dual-write only for bounded transition windows, and reconciliation jobs that compare legacy and V2 publication/content counts. Roll back by disabling V2 feature flags and stopping new commands; do not delete migrated history or n8n executions.

# Testing Strategy

Unit-test domain services, state transitions, policy decisions, content/map rules, ingestion normalization, idempotency, retrieval filtering, and output validation. Use deterministic fake LLM/provider adapters for all non-provider tests.

Integration-test Django/PostgreSQL/pgvector with tenant isolation, migrations, command/outbox transaction behavior, signed n8n callbacks, credential reference access, object-storage metadata, and provider adapter error normalization. Test every workflow contract against versioned JSON fixtures and run n8n workflows in an isolated environment with mocked provider endpoints.

End-to-end-test critical user paths: connect/verify account, backfill history, retrieve cited workspace knowledge, produce/revise/approve a draft, generate/review visual media, create/approve a Content Map, schedule, publish once, and recover a failed publish. Verify that a user cannot access another workspace through direct APIs, Agent retrieval, workflow inputs, callbacks, or exports.

Add contract tests between Django tool schemas and n8n workflows, replay tests from sanitized captured payloads, load tests for concurrent ingestion/retrieval, chaos tests for provider timeouts and duplicate callbacks, and security tests for approval replay, altered payloads, webhook forgery, credential leakage, and prompt-injection attempts in imported documents. Human evaluation should score factual grounding, brand adherence, platform fit, novelty, and visual suitability against stored rubrics.

# Risks

| Risk | Mitigation |
| --- | --- |
| Platform API access, quotas, and historical-data limits vary | Build connector capabilities per platform, record capability/scope, and degrade to user exports/manual upload where necessary. |
| Duplicate external publication from retries | Use immutable approved versions, command idempotency keys, provider external IDs, preflight reconciliation, and manual recovery states. |
| Cross-workspace data leak through RAG or automation | Enforce workspace scope in every query and callback, use row-level checks in Django, and test tenant isolation end to end. |
| Prompt injection or untrusted imported sources influencing tools | Treat retrieved text as untrusted data, separate instructions from evidence, restrict tools, validate outputs, and require approval for effects. |
| n8n becomes an accidental source of truth | Keep durable commands, state, approvals, results, and audit events in Django; use n8n execution data only operationally. |
| Cost and latency of LLM, embeddings, and visuals | Track per-run cost/latency, cache by content hash where safe, use budgets/quotas, and make expensive operations asynchronous. |
| Current direct integrations lack durable retries and audit depth | Migrate behind the command/outbox model before broadening publishing automation. |
| Existing configuration contains development-style security posture and application-held secrets | Move secrets to managed environment/secret storage, rotate exposed keys, lock down CORS/debug settings, and isolate n8n credentials before production rollout. |

# Decisions Requiring Review

1. Confirm tenancy: should a workspace represent one organization, one paying account, or both, and which roles are required at launch?
2. Confirm first supported ingestion platforms and whether official APIs, user data exports, or both are acceptable sources for prior content.
3. Confirm whether `pgvector` is acceptable as the initial RAG store and the expected workspace/document scale that would trigger a dedicated vector service review.
4. Confirm object-storage provider, retention/deletion policy, and whether raw imported provider payloads may be retained.
5. Define publish approval defaults, any permissible delegated-autopublish policy, and whether schedule creation itself requires confirmation.
6. Select LLM, embedding, visual-generation providers and data-processing/residency constraints; provider adapters are required regardless of selection.
7. Confirm n8n operating model: self-hosted queue-mode deployment, workflow source-control/deployment ownership, credential-management standard, and execution-data retention.
8. Confirm React adoption scope and timing, since the present repository contains Django-rendered templates/static JavaScript rather than a checked-in React client.
9. Define the success measures and labeled feedback process required before recommendation ranking or any future learning loop influences automated decisions.
10. Revisit MCP only when an external MCP client, multi-agent topology, or reusable cross-product tool surface is funded; until then retain the MCP-ready contract without MCP runtime complexity.
