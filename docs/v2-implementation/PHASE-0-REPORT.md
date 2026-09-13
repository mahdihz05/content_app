# Implemented Tasks

- `P0-BE-001`: complete. Active, compatibility, orphaned, and broken-consumer routes are inventoried in `docs/api/ROUTE-COMPATIBILITY-INVENTORY.md`; resolver assertions cover representative active and stale paths.
- `P0-BE-002`: complete. Additive V2 correlation ID, error envelope, authenticated health/readiness, and fail-closed feature-flag interfaces are implemented and locally verified.
- `P0-DB-001`: complete. Seeded PostgreSQL 16 migration/dump/restore reconciliation passed.
- `P0-UI-001`: complete. Two Chromium smoke tests pass inside the built backend image.
- `P0-N8N-001`: complete. Sanitized evidence/governance pass and deployed n8n volume state is verified empty.
- `P0-SEC-001`: blocked after partial remediation. Hard-coded source credentials were removed; rotation/revocation and tracked `.env` remediation require deployment-owner action.
- `P0-TST-001`: complete. Twenty-three tests pass against PostgreSQL 16.
- `P0-TST-002`: in progress. GitHub Actions configuration exists and equivalent local steps pass; hosted execution is pending.

# Files / Components Changed

- Added `backend/app/common/` for Phase 0 cross-cutting interfaces.
- Updated `backend/app/main/settings.py` and `backend/app/main/urls.py` additively.
- Added/updated authentication, content, Telegram, route, and browser characterization tests.
- Replaced import-time package exports with lazy exports in two legacy/internal packages so full Django test discovery no longer fails on circular/uninstalled model imports.
- Added API compatibility, browser smoke, migration, security, and n8n governance evidence.
- Deleted two tracked executable ad-hoc provider scripts that contained credentials.

# Database / Migrations

No V2 schema or data migration was created. The pre-existing
`backend/app/content/migrations/0019_alter_contentitem_status.py` remains
content-unchanged and is included after review. All 56 migrations applied on
PostgreSQL 16. A seeded custom-format dump restored with matching 35-table,
migration, and representative domain counts; restore checks passed.

# APIs

- Added authenticated `GET /api/v2/health/`.
- Added authenticated `GET /api/v2/readiness/` with non-sensitive 503 errors.
- Added `X-Correlation-ID` to responses without changing legacy bodies.
- Documented V2 error and future tool-envelope contracts.
- Removed or renamed no legacy route.

# UI

No product UI was added. Existing Django templates and vanilla JavaScript are
unchanged. Two browser smoke tests cover active create-content/Telegram DOM and
the characterized current/stale AI routes.

# n8n

The repository SQLite snapshot was read-only inspected. It contains one
workflow named `ai`, marked inactive, with no registered webhook, credential
row, or stored execution. A fully parameter-redacted topology is archived as
`n8n/workflows/archive/legacy-ai.v1.sanitized.json`, marked evidence-only and
non-deployable. No workflow was activated or invoked. The deployed Compose
volume contains zero workflows, webhooks, credentials, and executions.

# AI / Agent

No Agent or tool runtime was enabled. The future framework-independent tool
envelope and effect classes are documentation only. Characterization confirmed
that final generation currently calls missing
`PromptService.build_content_generation_prompt` and
`AITextService.generate_text` methods; tests mock these boundaries rather than
silently repairing behavior.

# Security

- Removed hard-coded AI and Telegram credentials from tracked Python source.
- Runtime AI settings now use environment variables.
- Added `.env` patterns to `.gitignore`.
- Removed `.env`, `n8n/data/`, and `volume/` from the Git index while preserving local ignored files.
- Text-source credential-pattern scan excluding runtime n8n data found only the already tracked `.env`.
- Actual credential rotation/revocation, approved secret injection, Git-history remediation, and runtime artifact handling remain blocked by deployment-owner access.

# Tests Executed

- `python manage.py check`
- `python manage.py makemigrations --check --dry-run`
- `python -m compileall -q .`
- JSON parsing for the n8n manifest, schema, and sanitized archive
- `python -m pip check`
- PostgreSQL-targeted characterization test command
- SQLite diagnostic run for `user.tests content.tests messaging_automation.tests common.tests`
- SQLite diagnostic browser test discovery
- credential-pattern scans
- `git diff --check`

# Test Results

- Django system check: PASS, zero issues.
- Migration drift check: PASS for model/file drift, with database-history warning because host `db` is unavailable.
- Python compilation: PASS.
- n8n JSON parse checks: PASS.
- Python dependency check: PASS.
- SQLite diagnostic characterization: PASS, 21/21.
- PostgreSQL characterization: PASS, 23/23.
- Full Django test discovery: PASS, 23/23 after two baseline import-time defects were corrected.
- Browser smoke: PASS, 2/2 in the built backend image.
- Seeded PostgreSQL dump/restore reconciliation: PASS.
- GitHub Actions workflow validation with `actionlint`: PASS.
- `check --deploy`: exits successfully with two documented HSTS subdomain/preload warnings; those settings require production TLS/domain approval.

# Regression Results

No verified legacy response or route regression was found in the 23-test
PostgreSQL suite or two browser smoke tests. Hosted CI and external
credential revocation evidence remain incomplete, so phase acceptance is not
granted.

# Acceptance Criteria

- Route inventory: met for development scope.
- Baseline tests in accepted CI: not met.
- No exposed active secret remains and rotation is proven: not met; tracked `.env` and external revocation remain.
- Backup/rehearsal evidence: production-like local rehearsal met; no claim is made about the real production database.
- Workflow governance/no legacy workflow use: met for repository and deployed local volume.
- Phase acceptance gate: not signed.

# Known Issues

- Existing final-generation service contract is broken at two missing methods.
- Current browser/API route drift is recorded in the route inventory.
- Existing campaign/research/multi-channel publish authorization gaps remain recorded for the approved later security migration.
- Git history still contains previously tracked secret/runtime material.
- Production HSTS subdomain/preload behavior is intentionally not enabled without the production TLS/domain gate.

# Deferred Items

- Hosted CI execution is pending a pushed branch/PR.
- Credential rotation/revocation and clean history scan are deferred pending deployment-owner access.

# Rollback Notes

Disable/remove the `common` URL and correlation middleware entries to roll back
the additive runtime interfaces. Legacy routes and bodies remain present. Do
not restore revoked credentials; no migration or data rollback is required.

# Evidence

- Baseline branch: `main`.
- Baseline commit: `a73bda74d906a84697e32536aa37361d60d1d91e`.
- Initial unrelated/untracked state: `docs/` and `content/migrations/0019_alter_contentitem_status.py`.
- PostgreSQL characterization: 23 passed in 26.164 seconds.
- Chromium browser smoke: 2 passed in 7.070 seconds.
- Source/restore: 56 migration rows, 35 public tables, and matching representative domain counts.
- Deployed local n8n volume: zero workflows/webhooks/credentials/executions.

# Phase Status

**IN PROGRESS / BLOCKED FROM ACCEPTANCE**

Completed phases: 0/9. Phase 0 development tasks complete: 6/8 (75%). Accepted
weighted progress: 0%. Remaining accepted weighted work: 100%.
