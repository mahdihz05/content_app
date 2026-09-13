# Final Architecture

V2 remains a modular Django application backed by PostgreSQL. Django is the system of record and authorization boundary. The existing Django-template and vanilla-JavaScript frontend remains the V2 frontend. n8n is an integration and workflow-orchestration service only. All product, Agent, and workflow interactions use Django-owned contracts and state transitions.

Development is incremental, testable, feature-flagged by workspace, and reversible. Existing functionality remains operational until a replacement has passed its documented parity, reconciliation, and recovery criteria.

# Locked Technology Decisions

- Django and PostgreSQL are the V2 core.
- PostgreSQL with pgvector is the initial RAG store unless Phase 0 or Phase 4 environment validation identifies a concrete blocker.
- The existing Django-template and vanilla-JavaScript frontend remains in place for V2.
- React is not part of the required V2 implementation and no React application or slice will be introduced under this plan.
- n8n workflows are exported as reviewed, source-controlled JSON under `n8n/workflows/`; `n8n/data/database.sqlite` is not a workflow source of truth.
- MCP is not implemented in V2. Tool contracts remain MCP-compatible for a separately approved future adapter.

# Django Responsibilities

Django owns identity, session and workspace context, authorization, policy evaluation, canonical relational state, content/version lineage, approvals, command and outbox records, audit events, feature flags, API validation, provider-adapter contracts, and authoritative domain transitions. It validates n8n callbacks and records their results idempotently.

Django is the sole product API for browser clients and the Agent. It remains the source of truth for product status; n8n execution data is operational evidence only.

# n8n Responsibilities

n8n executes named, Django-authorized integration workflows: connector verification, bounded imports, polling, pagination, provider rate limiting and retries, media transfer, scheduled delivery, and metrics collection. It may transform scoped payloads and report progress/results through signed callbacks.

n8n does not own business records, authorization, approval decisions, product-visible status, arbitrary workflow selection, or direct Agent access.

# Agent Responsibilities

The Agent is an application service operating with an authenticated actor, workspace context, bounded evidence, and an allow-listed set of typed tools. It may retrieve scoped information, ask questions, and create drafts or proposals subject to Django policy and validation.

The Agent cannot invoke raw URLs, n8n webhooks, SQL, credentials, arbitrary workflows, or direct provider/platform APIs. Consequential actions require Django authorization and a persisted approval bound to the exact command payload.

# Tool Gateway Contract

Every Agent tool call goes through the Django Tool Gateway. Contracts are versioned JSON schemas containing at least `tool_name`, `tool_version`, actor and workspace context, command ID, idempotency key, effect class, validated input, and explicit result schema.

For asynchronous or side-effecting operations, Django persists the command and outbox event atomically, dispatches only the named workflow, and returns a Django job/action reference. n8n callbacks are signed, replay-safe, idempotent, and applied through Django domain services. No callback directly mutates business state.

# MCP Decision

MCP is explicitly out of V2 scope. No MCP server, adapter, client, transport, or externally discoverable MCP tool is implemented during V2. Tool contracts must remain framework-independent and MCP-compatible so a future, separately approved MCP adapter can delegate to the Django Tool Gateway without changing authorization or exposing n8n.

# Frontend Decision

V2 uses the existing Django templates and vanilla JavaScript. Template pages may consume new Django APIs behind feature flags while preserving current routes and flows. React adoption is deferred outside V2 and is not a V2 dependency, deliverable, or phase exit criterion.

# RAG Decision

V2 RAG uses PostgreSQL plus pgvector, colocating vector rows, provenance, permissions, and transactional state. Phase 4 validates extension availability and migration behavior in a production-like environment before enabling it. A dedicated vector database is deferred unless that validation demonstrates a concrete blocker.

# Telegram Historical Ingestion Decision

Telegram Bot API support is limited to bot-visible updates and bot-authorized channel operations such as the existing verification and publishing flow. It must not be assumed to provide a complete, arbitrary historical channel archive. The V2 Bot API connector may import only history demonstrably available to that bot under documented channel membership, permissions, and API behavior; it must record the resulting coverage and limitations.

MTProto using a Telegram user session can provide materially different historical access, but it is not approved for production V2. No user-session credentials, API ID/hash, session files, or MTProto service will be introduced without a separate architecture and security decision covering consent, credential custody, retention, access control, operational ownership, and Telegram terms/compliance.

The approved fallback for complete or otherwise unavailable historical content is user-provided Telegram export or manual import. Django validates, normalizes, deduplicates, and records provenance and coverage for those imports. Phase 3 may proceed with Bot-API-limited ingestion and/or export/manual import; MTProto is not a dependency or an implied fallback.

# Security Boundaries

- Browser clients and the Agent call Django only.
- Django is the authorization boundary for every resource, tool, command, and callback.
- n8n receives narrowly scoped execution grants and named workflow inputs, never a user session, database access, broad credentials, or authorization authority.
- Raw n8n webhooks, workflow identifiers beyond the Django allow-list, SQL, credentials, and arbitrary workflow execution are never exposed to the Agent or browser.
- Credentials are managed as scoped secret references and never stored in content JSON, Agent context, logs, or workflow exports.
- Consequential actions use immutable payload fingerprints, expiry-bound approval records, idempotency keys, reconciliation, and authorized recovery.

# Phase Dependencies

- Phase 0 establishes compatibility characterization, test/CI baseline, source-controlled workflow standards, secret rotation, backup rehearsal, and feature-flag conventions.
- Phase 1 establishes workspace tenancy, policy, approval, command, outbox, audit, and callback substrate.
- Phase 2 establishes canonical content history and compatibility projections.
- Phase 3 depends on Phases 1-2 and uses only approved ingestion modes. Telegram historical ingestion follows the decision above.
- Phase 4 depends on Phases 1-2 and pgvector environment validation.
- Phases 5-6 depend on their required canonical history, RAG, policy, and tool-gateway capabilities.
- Phase 7 depends on the command/callback substrate, approved n8n operating model, and proven Telegram delivery parity. Direct delivery remains available behind its legacy flag until then.
- Phase 8 completes operational rollout and tool-contract conformance only; it does not add React or MCP.

# Remaining Blockers

- Phase 0 release prerequisites require deployment-owner access for exposed-secret rotation, backup/migration rehearsal, and CI/secret-storage decisions.
- Phase 1 requires launch workspace semantics and roles to be finalized before tenancy implementation.
- Phase 3 requires the supported Telegram import mode and pilot scope to be selected. Complete historical Telegram ingestion is blocked unless an export/manual-import path is accepted or a separate MTProto architecture/security decision is approved.
- Phase 4 requires production-like pgvector extension and migration validation; no repository evidence currently establishes a blocker.
- Provider, retention, data-residency, n8n operating-model, and publishing-approval decisions remain phase-specific gates already recorded in the Master Plan.

# Development Readiness

Architecture is frozen. Phase 0 development may begin because its purpose is to establish the baseline and resolve its explicit release prerequisites; no later phase may begin until its documented dependencies and gates are accepted. No product feature implementation is authorized by this document.
