# V2 Master Implementation Plan

## Purpose And Planning Basis

This is an implementation plan only. It does not authorize code changes, schema changes, workflow activation, a UI rewrite, React implementation, or MCP implementation.

The plan reconciles the approved V2 architecture with the repository verified on 2026-09-12 and frozen in `ARCHITECTURE-FREEZE.md`. The implementation remains limited to preserving current campaign/content/Telegram capabilities while adding previous-content ingestion, Content History, Content Intelligence, Workspace Memory/RAG, Brainstorming, Content Map planning, text and visual generation, n8n migration, reusable workflows/tools, the AI Content Agent, permissions, and MCP-compatible tool contracts.

### Verified Starting Point

- The system is a Django 5.2 modular monolith with PostgreSQL configuration, Django templates, and vanilla JavaScript. There is no application React client or frontend build pipeline.
- The ownership chain is `CustomUser -> Campaign -> ContentItem`. Current content state is largely JSON-backed. `GeneratedContent` has version fields but active final generation writes `ContentItem.information["generated_content"]` instead.
- Telegram verification and publishing are active synchronous request-path operations. `scheduled_at` has no executor.
- n8n is provisioned but Django has no routed integration. The persisted n8n SQLite database contains one inactive `ai` research webhook workflow whose callback target (`/api/v1/ai/webhook`) is not routed; it is not reusable V2 integration infrastructure.
- `KnowledgeSource` and `DocumentEmbedding` source files exist but are not exported from `ai.models`, have no migrations, and have no working ingestion/retrieval path. They are not a V2 RAG foundation.
- Celery/Redis settings and dependencies exist, but no deployed worker, scheduler, Redis Compose service, or task dispatch exists. V2 uses n8n for integration orchestration rather than attempting to activate this incomplete queue path.
- First-party tests are stubs and no CI workflow is present. V2 must establish tests before migrating consequential behavior.

### Target Boundaries

| Concern | V2 owner | Classification |
| --- | --- | --- |
| Identity, workspace membership, roles, policy, canonical state, approvals, audit, API validation | Django/PostgreSQL | Deterministic application logic |
| Content versions, history, planning, intelligence facts, memory provenance, retrieval filtering | Django/PostgreSQL + pgvector | Deterministic application logic |
| Provider-specific LLM, embedding, image interfaces and output validation | Django adapters | LLM reasoning occurs only through explicit adapters |
| Draft text, ideas, map proposals, recommendation narration | AI Content Agent + LLM | LLM reasoning; results are proposals, not authority |
| Content normalization, hashes, idempotency, scheduling intent, approval validation, policy decisions | Django services | Deterministic application logic |
| External account verification, paged import, polling, provider retries, media transfer, scheduled delivery, metrics collection | n8n | Deterministic workflow/integration logic |
| Commands, callbacks, result application, retries/dead-letter state | Django; n8n executes named workflows | Django is authoritative; n8n is operational only |
| Interactive authoring/review | Existing Django templates and vanilla JavaScript | Client only calls Django |
| Future external tool discovery | MCP adapter over Django tool gateway | Deferred; not a V2 runtime dependency |

### Explicit V2 Disposition

**Remains in Django**

- Session identity; workspace tenancy; membership roles; object and tool authorization.
- All canonical relational records, version lineage, approvals, command ledger, outbox, audit, metrics facts, and retrieval snapshots.
- Provider adapter interfaces, prompt/template versioning, LLM output validation, text generation, brainstorming, Content Map proposal logic, and Content Intelligence recommendations.
- API contracts, callback authentication, n8n execution grants, feature flags, reconciliation, and UI event/status APIs.

**Moves to n8n**

- Existing direct Telegram delivery and scheduled delivery, once parity is proven.
- Connected-account verification, prior-content backfill and recurring synchronization, media transfer, metrics refresh, and connector-oriented research acquisition.
- Retries, provider rate limiting, pagination, polling, workflow execution telemetry, and reusable operational transforms.

**Becomes an Agent tool**

- `content.search_history`, `memory.retrieve`, `research.discover_sources`, `connection.ingest_content`, `connection.refresh_metrics`, `content.generate_draft`, `visual.generate_asset`, `brainstorm.generate_options`, `content_map.create_or_rebalance`, `content.schedule`, `content.publish`, and `connection.verify`.
- The tool gateway validates typed, versioned schemas and policy before every invocation. The Agent never receives raw n8n URLs, SQL access, or platform credentials.

**Requires LLM reasoning**

- Producing structured text/visual briefs and drafts; generating brainstorm options; proposing/rebalancing Content Maps; synthesizing cited intelligence recommendations; asking clarifying questions; and explaining uncertainty.
- LLM output must be validated before it can create a draft/proposal. It cannot directly schedule, publish, connect accounts, delete, or mutate approval state.

**Deterministic workflow logic**

- Authorization, idempotency, validation, cursor advancement, normalization, deduplication, content hashes, retry classification, callback verification, state transitions, approval binding, scheduling, retrieval filtering/ranking, and provider delivery.

**Potential future MCP surface**

- The versioned Django tool contracts above, exposed through an MCP adapter only after an external MCP client or cross-product agent is approved.
- MCP uses the same scopes, approvals, command records, and result schemas. It never exposes n8n webhooks, credentials, or arbitrary workflows.

## Cross-Phase Rules

- Use expand/migrate/contract changes. New V2 tables are additive; do not delete or repurpose legacy columns during V2 feature rollout.
- Use UUID public IDs, UTC timestamps, workspace foreign keys, immutable version records, JSON only for provider payloads, and relational columns for queried state.
- Feature-flag every V2 capability by workspace. Keep legacy direct Telegram publishing available until n8n parity, reconciliation, and recovery acceptance criteria pass.
- Every consequential action requires a persisted approval bound to an immutable command payload fingerprint, destination, version/asset hash, and expiry.
- Django writes a command and outbox event atomically. n8n callbacks are signed, replay-safe, idempotent, and never directly mutate a business object without a Django domain transition.
- Export n8n workflow JSON to source control under `n8n/workflows/`; the mutable `n8n/data/database.sqlite` is not a workflow source of truth.
- Preserve existing Django-template/vanilla-JavaScript flows while V2 APIs are introduced. React is outside V2 scope and is not a V2 dependency or deliverable.

## Phase 0 - Baseline, Safety, And Compatibility Contract

**Objective:** Establish a tested, observable compatibility baseline before introducing tenancy, external workflows, or AI-driven V2 data writes.

**Exact scope:** Inventory active endpoints and legacy consumers; codify current content and Telegram behavior; introduce V2 feature-flag conventions, correlation IDs, API error contract, and test infrastructure. Rotate exposed secrets and define environment-only configuration as a release prerequisite, without changing product scope.

**Affected components/files:** `backend/app/main/settings.py`, `main/urls.py`, `content/urls.py`, `content/views/ai_chat.py`, `messaging_automation/urls.py`, `messaging_automation/services/telegram_*`, `campaigns/views/`, `research/views/`, `backend/app/requirements.txt`, `docker-compose.yml`, `.gitignore`; add `backend/app/common/`, `backend/app/*/tests/`, `docs/api/`, and CI configuration.

**Database changes:** Add only additive `FeatureFlag`/workspace capability configuration if a database-backed flag system is selected; otherwise use a documented environment/config adapter. No content migration in this phase.

**API changes:** Publish an API inventory and versioning/error conventions. Add authenticated health/readiness endpoints and correlation IDs. Do not remove or rename existing routes.

**Frontend changes:** None required beyond preserving existing template behavior. Add no React application.

**n8n workflows:** Export and archive the inactive legacy `ai` workflow for evidence; do not activate it. Define workflow naming, versioning, secret redaction, callback, and deployment standards.

**Agent tools:** None exposed. Define the versioned JSON tool-envelope specification and effect classes (`read`, `draft`, `mutate_internal`, `consequential`).

**Dependencies:** Access to deployment environment owners for secret rotation and a decision on CI runner/secret storage.

**Migration requirements:** Record schema migration state, including the untracked `content/migrations/0019_alter_contentitem_status.py`, before creating new migrations. Obtain a production backup and migration rehearsal dataset.

**Tests:** Route/authentication smoke tests; characterization tests for content creation, generation persistence, Telegram verification/publish/logging, and legacy template API calls; migration-state check; static checks; CI execution.

**Acceptance criteria:** Baseline tests run in CI; active versus orphaned routes are documented; no V2 process relies on the inactive n8n workflow; exposed credentials are rotated and removed from tracked/configured source; a rollback-tested database backup exists.

**Rollback considerations:** This phase is additive. Disable correlation/flag middleware if needed; retain legacy routes and behavior.

**Risks:** Characterization can reveal currently broken generation contracts (`AITextService.generate*` calls) or frontend route drift. Record defects and decide whether a narrowly scoped compatibility repair is needed before migration; do not silently change behavior.

**Definition of done:** The current system has a reproducible test baseline, release safety prerequisites are met, and an agreed compatibility contract exists for all behavior V2 must preserve.

## Phase 1 - Workspace Tenancy, Policy, And Execution Ledger

**Objective:** Establish the authorization and durable-command substrate required before any shared history, RAG, Agent, or n8n operation.

**Exact scope:** Add workspace-first ownership, membership roles, resource policy evaluation, audit events, approvals, durable commands, outbox, workflow executions, and dead-letter records. Backfill a default workspace for each existing owner without changing legacy UI semantics.

**Affected components/files:** Add Django apps `backend/app/workspaces/`, `backend/app/automation/`, and `backend/app/audit/`; update `main/settings.py`, `main/urls.py`, `user/models/CustomUser.py`, `campaigns/models/`, `content/models/`, `platforms/models/`, `research/models/`, `messaging_automation/models/`, and their migrations/admin/tests.

**Database changes:** Add `Workspace`, `WorkspaceMembership`, role/policy representation, `ActionApproval`, `AutomationCommand`, `WorkflowExecution`, `OutboxEvent`, `DeadLetter`, and `AuditEvent`. Add nullable `workspace` foreign keys and legacy-owner reference fields to Campaign, ContentItem, AI chat/session data, ResearchSource, SocialAccount, TelegramChannel, and TelegramPublishLog. Add public UUIDs, indexes, idempotency constraints, and append-only audit protections.

**API changes:** Add workspace selection/context endpoint, membership/role administration endpoints, and internal command/approval status endpoints. Existing APIs infer the owner default workspace during transition and retain their current request shapes.

**Frontend changes:** Add a minimal workspace context indicator/selector only when users can belong to more than one workspace. Existing templates continue to function under a default workspace.

**n8n workflows:** None operational. Define the Django-issued scoped execution-grant format, signed callback contract, and workflow manifest schema.

**Agent tools:** Implement the internal tool registry and policy preflight only; do not connect an LLM Agent. Tool context includes actor, workspace, command ID, idempotency key, effect class, and schema version.

**Dependencies:** Phase 0 baseline; architectural approval of workspace meaning and launch roles.

**Migration requirements:** Create default workspaces transactionally per legacy user; backfill all listed user/campaign-owned data; reconcile row counts and null workspace references; block new V2 writes for records without a workspace.

**Tests:** Tenant-isolation tests for all migrated relationships; role matrix tests; approval fingerprint/expiry/replay tests; command/outbox atomicity and idempotency tests; migration forward/reverse tests.

**Acceptance criteria:** Every V2-addressable record resolves to one workspace; a user cannot access another workspace by direct API ID; consequential commands cannot execute without a valid approval; audit and command records are created for every V2 mutation.

**Rollback considerations:** Disable workspace enforcement by feature flag and use legacy owner checks; retain populated workspace data and mappings. Do not reverse a production backfill that would orphan records.

**Risks:** Existing endpoints with incomplete ownership checks can bypass tenancy. Their authorization must be corrected before exposing equivalent V2 resources.

**Definition of done:** Workspace tenancy, policy evaluation, audit, approval, command, outbox, and compatibility backfill are deployed and independently tested.

## Phase 2 - Canonical Content History And Asset Foundation

**Objective:** Create an immutable, cross-platform content history without breaking existing `ContentItem` pages or Telegram delivery.

**Exact scope:** Introduce canonical content records, version lineage, assets, publications, and metric observations. Backfill first-party content and publication history. Build a compatibility projection so legacy views continue reading/writing during the transition.

**Affected components/files:** Add `backend/app/content_history/`; update `content/models/ContentItem.py`, `GeneratedContent.py`, `content/views/ai_chat.py`, `content/urls.py`, `messaging_automation/models/telegram_publish_log.py`, `messaging_automation/services/telegram_publisher.py`, `campaigns/models/`, `main/settings.py`; add object-storage adapter under `backend/app/integrations/`.

**Database changes:** Add `ContentRecord`, immutable `ContentVersion`, `ContentAsset`, `Publication`, and append-only `ContentMetricObservation`. Add origin, source account, external ID, canonical URL, source fingerprint, state, parent version, version number, hash, model/prompt revision, retrieval snapshot reference, and publication external IDs. Enforce unique `(source_account, external_id)` where external IDs exist and `(content_record, version_number)`.

**API changes:** Add `/api/v2/content-records/`, version create/list/review endpoints, history search endpoint, publication read endpoints, and asset metadata/upload-init endpoints. Keep `/content/api/v1/` stable; do not return V2-only status values through legacy responses.

**Frontend changes:** Add Content History list/detail/version timeline pages or template panels backed by V2 APIs. Preserve the current content list and AI chat pages; link each legacy item to its history projection.

**n8n workflows:** No delivery migration yet. Define `content.publish` callback payload and media-reference contract for Phase 7.

**Agent tools:** Implement read-only `content.search_history`. Its filters are workspace-bound and return normalized records, versions, metrics summaries, and citations; no raw provider payload is returned.

**Dependencies:** Phase 1; object-storage provider/retention decision; content-version status semantics approved.

**Migration requirements:** Backfill one `ContentRecord` for every ContentItem; create versions from `GeneratedContent` and `information.generated_content`, preserving timestamps, author/model provenance where available; create publications from Telegram logs; record ambiguity rather than inventing approval state. Run count, hash, and sample-content reconciliation. Use bounded dual-write only after projection tests pass.

**Tests:** Backfill/reconciliation fixtures; version immutability and parent lineage tests; external-ID deduplication tests; legacy projection tests; history search workspace filtering; object metadata authorization tests.

**Acceptance criteria:** Every existing ContentItem has a traceable V2 content record; generation never overwrites an approved version; every legacy Telegram log maps to a publication or documented exception; legacy pages remain functional under flag-off and flag-on projections.

**Rollback considerations:** Stop V2 dual writes and serve legacy content. Retain immutable V2 records for later reconciliation; do not delete imported/backfilled versions or assets.

**Risks:** Legacy JSON is incomplete and status vocabularies conflict. Preserve original JSON and mark inferred fields/provenance rather than normalizing away uncertainty.

**Definition of done:** Content History is a canonical, workspace-scoped, versioned corpus with verified legacy compatibility.

## Phase 3 - Connections And Previous-Content Ingestion

**Objective:** Ingest prior content and metrics from authorized connected accounts incrementally, safely, and observably.

**Exact scope:** Add connection lifecycle/cursors/capabilities. Telegram Bot API ingestion is limited to history demonstrably available to an authorized bot and must record coverage; it must not be represented as complete channel history. Support Telegram export/manual import for unavailable history. Add other platforms only with approved official APIs or accepted user-export ingestion. MTProto/user-session ingestion is out of scope unless separately approved through an architecture/security decision. Support initial bounded backfill, manual re-sync, recurring synchronization, media references, normalized metrics, and source deletion/unavailability states.

**Affected components/files:** Add `backend/app/connections/`; update `platforms/models/{Platform,SocialAccount}.py`, `campaigns/models/CampaignSocialAccount.py`, `messaging_automation/models/{telegram_channel,channel_verification}.py`, `content_history/`, `automation/`, `main/urls.py`, and Compose/n8n deployment configuration; add `n8n/workflows/` manifests and exports.

**Database changes:** Add `PlatformConnection`, encrypted `CredentialReference`, `ConnectionVerification`, `ConnectionCursor`, connection capability/scope records, import batch/observation records, and connection links on ContentRecord/Publication. Store provider payload hashes and object-storage references, not tokens in JSON.

**API changes:** Add connection create/verify/status/capability endpoints, import request/status endpoints, manual re-sync endpoint, and internal callback endpoints for normalized pages, media, cursor commits, and failures. Callbacks require a workflow execution grant and signed payload.

**Frontend changes:** Add connection management, permission/capability display, import range selection, progress/error/retry views, and imported-history source indicators. Do not expose platform credentials in browser payloads.

**n8n workflows:** Implement source-controlled `connection.verify`, `connection.ingest_content`, and `connection.refresh_metrics`; reusable sub-workflows for command-envelope validation, scoped connection lookup, pagination/rate limiting, media transfer, error normalization, and signed callback delivery. A schedule asks Django for eligible cursors and advances only after Django accepts the page.

**Agent tools:** Expose `connection.verify`, `connection.ingest_content`, and `connection.refresh_metrics` through the Django tool gateway. Verification/import are consequential or create effects as defined by policy; imports have a bounded payload and job reference.

**Dependencies:** Phases 1-2; approved first platform list, permitted data sources (official APIs versus exports), credential encryption/secret-management standard, and n8n deployment ownership.

**Migration requirements:** Map `SocialAccount`, `CampaignSocialAccount`, TelegramChannel, and verification data to PlatformConnection records without retiring legacy records. Seed cursors conservatively. Run initial imports in small batches; reconcile source fingerprints/counts before recurring sync is enabled.

**Tests:** Connector normalization fixture tests; cursor commit/retry/idempotency tests; duplicate import tests; signed callback/replay/forgery tests; rate-limit and partial-page tests; tenant isolation across workflow inputs; export-import tests if exports are supported.

**Acceptance criteria:** An authorized pilot workspace can verify a supported connection, backfill a bounded history without duplicates, see progress and recoverable failures, and re-sync only new/changed items. Django retains the canonical result and n8n is not queried for product status.

**Rollback considerations:** Disable connector feature flags/schedules and stop dispatching commands. Preserve cursors, raw references, and observations; do not delete imported records solely because a workflow fails.

**Risks:** Platform access scopes, history depth, and deletion semantics differ. Telegram Bot API cannot be assumed to retrieve complete historical channel content. Release capability-by-capability and provide the approved Telegram export/manual-import fallback; do not introduce MTProto/user credentials without a separate architecture/security decision.

**Definition of done:** Previous-content ingestion is production-operable for the approved pilot connection(s), with reconciliation, retries, and secure workflow boundaries.

## Phase 4 - Workspace Memory And RAG

**Objective:** Deliver curated, citation-producing workspace memory distinct from the imported content corpus.

**Exact scope:** Build memory sources/entries/chunks, protected original assets, deterministic extraction/chunking, pgvector embeddings, hybrid retrieval, retrieval snapshots, re-embedding revisions, and review/freshness controls. Imported history is opt-in as a separate corpus selector.

**Affected components/files:** Add `backend/app/memory/` and `backend/app/integrations/embeddings.py`; replace or explicitly retire the unregistered `ai/models/KnowledgeSource.py` and `DocumentEmbedding.py` scaffolding through migrations/data mapping; update `main/settings.py`, PostgreSQL image/provisioning, content-history APIs, and template/API clients.

**Database changes:** Enable PostgreSQL `vector` extension through a guarded migration. Add `MemorySource`, `MemoryEntry`, `MemoryChunk`, `EmbeddingRevision`, and `RetrievalSnapshot`; use vector column/indexes, full-text fields/indexes, scope (`workspace`, `campaign`, `content_record`), source/version provenance, chunk ordinal/hash, language, metadata filters, visibility, freshness/expiry, and review status.

**API changes:** Add source upload/create, ingestion status, review/expiry, retrieval, and citation endpoints. Retrieval accepts an explicit corpus selector and returns bounded, permission-filtered citations, freshness, and source metadata; raw embeddings are never serialized.

**Frontend changes:** Add Workspace Memory library, upload/status/review UI, campaign/content scope selection, and cited retrieval panels in authoring. Existing content UI remains available.

**n8n workflows:** None required for core extraction/retrieval. If document extraction requires asynchronous external conversion, invoke it through a bounded `memory.extract_source` workflow later; it must return extracted text/asset metadata to Django, not own chunk state.

**Agent tools:** Expose read-only `memory.retrieve`; optionally an authorized internal memory-source submission tool after review workflow exists. The Agent receives only scoped excerpts/citations and treats all retrieved content as untrusted evidence.

**Dependencies:** Phases 1-2; pgvector approval and migration support; object-storage provider; embedding provider/data-residency decision; document retention/deletion policy.

**Migration requirements:** Do not assume the old scaffolding has tables. If any historical JSON embedding data exists, import it as legacy provenance only and re-embed into new revisions; validate source hashes before marking it usable. Roll out pgvector migration in a production-like database first.

**Tests:** Chunk determinism/hash tests; vector/full-text hybrid ranking fixtures; strict workspace/campaign/content scope tests; citation and token-budget tests; re-embedding/provenance tests; prompt-injection containment tests; extension migration tests.

**Acceptance criteria:** Authorized users can add curated sources, monitor ingestion, retrieve only permitted cited/fresh material, and include history only by explicit selection. Retrieval cannot leak cross-workspace data.

**Rollback considerations:** Disable ingestion/retrieval flags and retain source/provenance records. Keep vector indexes/data intact; do not drop the extension during rollback.

**Risks:** Embedding cost, poor extraction quality, and sensitive document retention. Apply quotas, content hashes/caching where safe, review states, and retention jobs before broad upload access.

**Definition of done:** Workspace Memory/RAG is a tested, workspace-isolated, auditable retrieval capability with citations and versioned provenance.

## Phase 5 - Content Intelligence, Brainstorming, And Content Map

**Objective:** Turn canonical history, metrics, memory, and research into explainable recommendations, draft ideas, and approval-based plans.

**Exact scope:** Add normalized intelligence facts/snapshots, recommendations/outcomes, IdeaProposals and feedback, Content Maps/revisions/slots, coverage analysis, deterministic validation, and LLM proposal services. No automatic scheduling or publishing from any proposal.

**Affected components/files:** Add `backend/app/intelligence/`, `backend/app/planning/`, `backend/app/brainstorming/`, and `backend/app/agent/` domain services; update `content_history/`, `memory/`, `research/`, `campaigns/`, API routing, templates/static scripts, and future React API contract documentation.

**Database changes:** Add score/recommendation snapshots and outcomes, `IdeaProposal`, `IdeaFeedback`, `ContentMap`, `ContentMapRevision`, and `ContentMapSlot`; link all to workspace and optionally campaign/content record. Persist evidence references, confidence, freshness, known gaps, plan constraints, slot time windows, pillar/funnel/objective/format, feedback reasons, and proposal/model/prompt revisions.

**API changes:** Add intelligence recommendation/history endpoints; brainstorm create/list/shortlist/reject/promote endpoints; map create/propose/revise/approve/slot endpoints; content-record creation from an approved slot. All proposal APIs return evidence, assumptions, and validation results.

**Frontend changes:** Add Content Intelligence views with evidence/freshness, Brainstorming board with shortlist/reject/promote actions, and Content Map calendar/coverage/revision review in Django templates and vanilla JavaScript. Do not replace the dashboard with React during V2.

**n8n workflows:** Implement `research.discover_sources` only if source acquisition is approved and can meet the command/callback contract. It uses reusable rate-limit/normalization/callback sub-workflows and persists selected sources through Django. Metrics aggregation schedules can begin after imported metrics exist.

**Agent tools:** Expose `research.discover_sources`, `brainstorm.generate_options`, and `content_map.create_or_rebalance`. The latter two are draft-producing LLM tools; Django validates inputs, retrieves bounded evidence, stores proposal records, and returns no schedule/publish effect.

**Dependencies:** Phases 1-4; approved intelligence success measures and feedback rubric; policy decision on research providers and retained source content.

**Migration requirements:** Convert campaign goals/forms to map constraints where unambiguous, leaving original values intact. Seed no inferred ideas or maps. Backfill metrics snapshots only from timestamped observations.

**Tests:** Explainability/evidence completeness tests; deterministic coverage and slot-rule tests; idea/map permission and transition tests; fake-LLM schema/validator tests; research workflow contract tests; user feedback retention tests.

**Acceptance criteria:** Users can view evidence-backed recommendations, generate and manage non-publishing idea proposals, create/review map revisions, and promote approved ideas/slots to draft content. No proposal can create an external effect.

**Rollback considerations:** Disable proposal/intelligence flags; retain snapshots, ideas, and maps as user-created records. Do not remove approved plans or promoted content records.

**Risks:** Opaque scoring and weak evidence can erode trust. Require explicit citations, freshness, confidence, known gaps, and user feedback; never treat scores as autonomous decisions.

**Definition of done:** Intelligence, Brainstorming, and Content Map features produce explainable, permissioned, reversible planning outputs from V2 evidence.

## Phase 6 - AI Content Agent And Text/Visual Draft Production

**Objective:** Introduce a bounded AI Content Agent that creates validated, cited drafts and visual assets while preserving the existing chat workflow until parity is proven.

**Exact scope:** Add Agent runs, tool invocations, structured brief/retrieval snapshots, text draft/version generation, visual asset requests, validation, review states, transparent activity display, cost/latency tracking, and compatibility adapters for current AI clients. Repair provider method contract mismatches as part of the controlled adapter boundary, not in scattered legacy views.

**Affected components/files:** Add `backend/app/agent/`, `backend/app/generation/`, provider adapters under `backend/app/integrations/`; update `ai/clients/ai_client.py`, `ai/services/ai_text_service.py`, `ai/orchestration/conversation_orchestrator.py`, `content/views/ai_chat.py`, `content_history/`, `memory/`, `automation/`, templates/static scripts, and API documentation.

**Database changes:** Add `AgentRun`, `ToolInvocation`, `GenerationEvaluation`, provider/prompt/template revision records or fields, model token/cost/latency fields, structured brief, validation result, and retrieval snapshot references. Link generated text and visual outputs to immutable ContentVersion/ContentAsset rows.

**API changes:** Add Agent conversation/run/status/activity endpoints; draft generation/revision/review endpoints; visual brief/request/status/review endpoints; explicit approve/reject/edit endpoints. Keep existing chat routes as compatibility paths until V2 behavior parity is accepted.

**Frontend changes:** Add transparent Agent activity, cited evidence, assumptions, tool status, draft version comparison, and visual review UI. The current `create_content_ai.html` may consume V2 APIs behind a feature flag. Do not introduce a React authoring slice during V2.

**n8n workflows:** Implement `visual.generate_asset` only if visual provider/media transfer benefits from n8n; otherwise a Django adapter is allowed. It returns immutable asset metadata via command/callback and never writes domain state directly. Reuse callback/error/media sub-workflows.

**Agent tools:** Activate `content.generate_draft` and `visual.generate_asset`, plus prior read/draft tools. The Agent may invoke only allow-listed typed tools. Text generation is synchronous only when bounded; costly visual work is asynchronous via command/job.

**Dependencies:** Phases 1-5; LLM, embedding, and visual provider choices; model data-processing constraints; output validation rules by target platform.

**Migration requirements:** Dual-write generated output to `ContentVersion` and the legacy projection only for a bounded workspace pilot. Map legacy AI chat sessions/messages to workspace context but do not reinterpret historical conversation content as memory without review.

**Tests:** Fake-provider deterministic tests; output schema/length/platform/citation/similarity validation tests; tool allow-list tests; prompt-injection tests; cost/timeout/error normalization tests; draft immutability and approval tests; visual asset authorization/hash tests; legacy chat parity tests.

**Acceptance criteria:** An authorized user can request a cited text draft and visual asset, inspect Agent/tool activity, edit/review versions, and approve an immutable version. The Agent cannot take consequential action or access data outside workspace scope.

**Rollback considerations:** Disable Agent and V2 generation flags; route users to legacy chat/generation. Retain created versions/assets/runs for audit and export.

**Risks:** Provider failures, hallucinated claims, and direct legacy-client calls. Enforce adapter interfaces, validators, citations, bounded tool sets, and feature-flagged migration rather than replacing the existing chat path prematurely.

**Definition of done:** The AI Content Agent reliably produces transparent, validated, workspace-scoped draft text and visuals, with no autonomous external side effects.

## Phase 7 - n8n Delivery Migration, Scheduling, And Reusable Operations

**Objective:** Replace direct synchronous Telegram publication with durable, approved command-driven n8n delivery and add safe scheduled publishing.

**Exact scope:** Implement dispatch/outbox worker, signed callbacks, n8n workflow deployment, delivery reconciliation, schedule intent, retries/dead-letter recovery, and Telegram delivery parity. Extend to other approved connection workflows only after Telegram parity.

**Affected components/files:** Update `automation/`, `content_history/`, `content/`, `messaging_automation/services/{telegram_publisher,telegram_api}.py`, `messaging_automation/views/channel_management.py`, `messaging_automation/urls.py`, `main/settings.py`, `docker-compose.yml`; add `n8n/workflows/{content-publish,scheduled-publish,analytics-aggregate}.json` and reusable sub-workflows; add deployment/runbook docs.

**Database changes:** Extend `AutomationCommand`, `WorkflowExecution`, `Publication`, `ActionApproval`, `DeadLetter`, and `OutboxEvent` with delivery idempotency keys, attempt state, workflow/version, provider execution IDs, callback hashes, retry schedule, reconciliation state, and immutable approved version/asset fingerprints. Add schedule intent records if scheduling must support revisions/audit independently of ContentRecord.

**API changes:** Add schedule create/change/cancel and approval endpoints; publish command/status/recovery endpoints; signed internal dispatch/callback endpoints; publication reconciliation endpoint. Existing Telegram endpoints remain behind a legacy feature flag during dual-run.

**Frontend changes:** Add explicit publish/schedule approval modal showing exact destination, immutable version/asset, time, external effect, and cost where known; add command progress, failure, and authorized recovery UI. Preserve existing Telegram channel pages during migration.

**n8n workflows:** Implement `content.publish`, scheduled dispatch, and `analytics.aggregate`; reusable sub-workflows for envelope validation, grant verification, account lookup, rate limiting, media upload, error classification, callback, and dead-letter notification. Workflows are exported, reviewed, source-controlled, and deployed through controlled automation. n8n execution retention is short and redacted.

**Agent tools:** Activate `content.schedule` and `content.publish` as consequential tools only. The tool gateway requires an unexpired approval matching exact payload/destination/hash; any material change invalidates approval.

**Dependencies:** Phases 1-3 and 6; n8n operational model, queue/worker capacity, credential storage, webhook network boundary, publishing approval/delegation policy, and Telegram idempotency/reconciliation strategy.

**Migration requirements:** Keep direct `TelegramPublisher` behind a flag. Dual-run only non-delivering preflight/reconciliation where possible; never intentionally double-publish. Map legacy `scheduled_at`, `publish_status`, and logs to schedule/publication records. Enable n8n delivery per pilot workspace/channel after parity and recovery drill.

**Tests:** Command/outbox dispatch tests; signed callback/replay/duplicate/out-of-order tests; workflow JSON contract tests; mocked Telegram timeout/rate-limit/ambiguous result tests; idempotency/reconciliation tests; approval mutation tests; scheduled delivery E2E and dead-letter recovery tests.

**Acceptance criteria:** A user can approve, schedule, publish once, see authoritative Django status, and recover a classified failure. Duplicate callback/retry cannot duplicate a known delivery. n8n has no authoritative business state and direct delivery is disabled only after pilot parity is proven.

**Rollback considerations:** Disable n8n delivery/schedule flags, stop new dispatch, and re-enable direct Telegram publishing for approved legacy operations. Do not retry ambiguous deliveries automatically; preserve commands/executions for reconciliation.

**Risks:** Duplicate external posts, callback forgery, rate limits, and n8n availability. Mitigate with immutable payload fingerprints, per-provider idempotency/reconciliation, grants, network isolation, limits, and visible dead letters.

**Definition of done:** Telegram publication and scheduling operate through approved, auditable, source-controlled n8n workflows with proven parity and recovery.

## Phase 8 - Product Transition, Observability, And Tool-Contract Readiness

**Objective:** Complete controlled rollout, retire V2-replaced direct paths only after evidence, and freeze framework-independent tool contracts for possible future MCP adoption.

**Exact scope:** Complete feature-flag rollout, observability, data retention/export, legacy compatibility retirement decisions, security/load/chaos evaluation, and tool-contract conformance. React and MCP implementation are out of V2 scope.

**Affected components/files:** `backend/app/common/`, `workspaces/`, `automation/`, `audit/`, `agent/`, all V2 domain apps, `main/settings.py`, `docker-compose.yml`, `n8n/workflows/`, Django templates/static scripts, operational runbooks and retention documentation.

**Database changes:** Add only indexes/partitions/retention markers required by observed load. Apply archival/retention policies to raw payload references, Agent material, workflow execution metadata, audit exports, and metrics while preserving required content/version/publication lineage.

**API changes:** Freeze and document V2 public and Tool Gateway contracts; add version negotiation/deprecation headers for retired compatibility endpoints. Contracts remain MCP-compatible, but no MCP adapter is implemented. No direct client-to-n8n API is introduced.

**Frontend changes:** Complete the V2 UI in Django templates and vanilla JavaScript. Retire orphaned legacy stepper assets only after usage telemetry and documented replacement paths.

**n8n workflows:** Promote reviewed workflows through controlled deployment, capacity/rate-limit configuration, monitoring, retention, backup/restore drills, and version rollback procedures. Delete neither legacy workflow state nor execution evidence until retention policy allows.

**Agent tools:** Freeze tool schemas and conformance suite. Validate MCP-compatible contract properties without building or enabling an MCP adapter.

**Dependencies:** All prior phases; decisions on observability provider, retention, and production deployment topology.

**Migration requirements:** Remove legacy dual writes and direct publish paths only after export, retention, reconciliation, telemetry, and rollback windows are approved. Archive rather than delete legacy JSON fields until contractual retention expires.

**Tests:** Full regression suite; migration upgrade tests from production-like snapshot; E2E tenant isolation across browser/API/Agent/n8n callback; tool-contract conformance tests; load tests for ingestion/retrieval; chaos tests for provider/n8n failure; security tests for credential leakage, approval replay, and prompt injection; accessibility/responsive browser tests.

**Acceptance criteria:** Rollout telemetry and audit trails demonstrate V2 adoption and parity; operational alerts cover command failures, dead letters, ingestion lag, retrieval latency, provider limits, and cross-workspace denials; a documented rollback drill succeeds; Tool Gateway contracts are frozen and MCP-compatible without n8n exposure.

**Rollback considerations:** Disable V2 flags per workspace, pin n8n workflow version, restore API compatibility projections, and stop new V2 commands. Never delete canonical V2 history, commands, approvals, or audit records as a rollback action.

**Risks:** Premature legacy removal, split UI behavior, cost growth, and an accidental future MCP security bypass. Gate retirement on measured parity; retain the template UI during V2; enforce budgets/quotas; require any future MCP access to use the Django gateway only.

**Definition of done:** V2 is operationally supported, measured, reversible, and has frozen MCP-compatible Tool Gateway contracts. MCP itself is not implemented.

## Architecture Review Decisions

The following are decisions required to begin the dependent implementation phases; they are not reasons to begin development before review:

1. Workspace meaning, initial roles, invitation/membership administration, and whether an existing user maps to one default workspace.
2. First ingestion platforms and approved acquisition modes: official API, user export, or both.
3. PostgreSQL `pgvector` suitability, expected scale, and object-storage provider/retention/deletion policy.
4. LLM, embedding, image, and research providers plus data residency, budgets, and content-retention constraints.
5. Publish approval default, scheduling confirmation, and any narrowly delegated auto-publish policy.
6. n8n self-hosted operating model, queue-mode timing, workflow deployment ownership, credential standard, callback network boundary, and execution retention.
7. React is deferred outside V2; no V2 implementation decision is required.
8. Intelligence success metrics, human evaluation rubric, and feedback governance before recommendations influence automation.
9. Production migration inventory/backup rehearsal, including resolution of the untracked `content/migrations/0019_alter_contentitem_status.py` state.

READY FOR ARCHITECTURAL REVIEW: YES
