# Automation V2 Internal Contract

## Integration

The automation and audit apps are additive Phase 1 primitives. They intentionally are not mounted or enabled by this change because the parallel workspace implementation is not yet present.

After the `workspaces.Workspace` initial migration exists:

1. Add `audit` and `automation` to `INSTALLED_APPS`, after `workspaces`.
2. Mount `path('api/v2/internal/', include('automation.urls'))` in the project URL configuration.
3. Run `python manage.py migrate` and `python manage.py test audit automation`.
4. Register only reviewed `ToolSpec` instances in `automation.registry.registry` during application startup.

All public resource IDs are UUIDs. All datetimes are timezone-aware UTC values serialized as ISO 8601. Clients must not send database primary keys.

## Tool Preflight V1

`ToolRegistry.preflight` accepts an exact tool name/version, JSON payload, actor, workspace, and policy evaluator. The policy evaluator must return `PolicyDecision`. Unknown tools, unsupported schema values, denied policy, or a consequential tool that does not require approval fail closed.

`automation.policy.workspace_policy_preflight` is the V1 adapter for the Phase 1 workspace role/policy service. It rejects inactive/non-members, unknown actions, and mismatches between a tool effect and workspace policy effect. Its fingerprint facts bind the membership role and applicable policy-grant revision.

The supported JSON Schema subset is `type`, `required`, `properties`, `additionalProperties`, `items`, `enum`, `minItems`, `maxItems`, `minLength`, `maxLength`, `minimum`, and `maximum`. Both tool input and successful callback results are validated.

Payload and policy fingerprints are SHA-256 over UTF-8 canonical JSON with sorted keys, compact separators, ASCII escaping, and non-finite numbers rejected.

## Command And Approval API

These session-authenticated routes require an exact `X-Workspace-ID` UUID header and active workspace membership. Unauthorized or cross-workspace object lookups return `404` to avoid identifier enumeration.

| Method | Route | Purpose |
| --- | --- | --- |
| `GET` | `commands/<command-uuid>/` | Read authoritative command status and result. |
| `GET` | `approvals/<approval-uuid>/` | Read approval status and expiry. |
| `POST` | `approvals/<approval-uuid>/decision/` | Approve or reject; requires `automation.decide_actionapproval`. |

Decision request:

```json
{
  "decision": "approve",
  "reason": "Reviewed exact destination and immutable payload"
}
```

Consequential command creation is a domain-service operation. `create_command` consumes an approved, unexpired approval only when workspace, tool/version, payload fingerprint, and current policy fingerprint all match. The command, one outbox event, audit event, and approval consumption commit in one transaction. The idempotency key is unique per workspace and cannot be reused for changed request semantics.

## Execution Grant V1

`issue_execution_grant` returns a Django-signed, short-lived bearer capability. Lifetime is at most 300 seconds. Claims are:

```json
{
  "version": "v1",
  "jti": "uuid",
  "command_id": "uuid",
  "execution_id": "uuid",
  "workspace_id": "uuid",
  "workflow_name": "allow-listed-name",
  "workflow_version": "version",
  "scopes": ["execution:callback"],
  "iat": 0,
  "exp": 0,
  "callback_secret": "per-grant-random-secret"
}
```

The grant conveys no user session, database authority, credentials, arbitrary URL, or arbitrary workflow selection. Receivers must treat the full grant and `callback_secret` as secrets and discard them at expiry.

## Signed Callback V1

Route: `POST callbacks/executions/`

Required headers:

| Header | Value |
| --- | --- |
| `X-Automation-Grant` | Signed execution grant. |
| `X-Automation-Timestamp` | Current Unix timestamp; accepted skew is 300 seconds. |
| `X-Automation-Nonce` | New UUID for each logical callback attempt. |
| `Idempotency-Key` | Stable key for retries of the same logical callback, maximum 128 characters. |
| `X-Automation-Signature` | Lowercase hex HMAC-SHA256. |

Callback body:

```json
{
  "contract_version": "v1",
  "status": "succeeded",
  "result": {}
}
```

`status` is `running`, `succeeded`, or `failed`. A failed callback may include `error` with `code` and `message`. Additional top-level fields are rejected.

Calculate the signature with the grant's `callback_secret` as the HMAC key and this UTF-8 message:

```text
<timestamp>\n<nonce>\n<idempotency-key>\n<sha256-of-canonical-body>
```

Canonical body encoding uses the fingerprint rules above. Django validates the grant signature, expiry, callback scope, exact execution/workspace/command/workflow binding, callback HMAC, clock window, body schema, and registered result schema before a transaction changes ledger state.

A retry with the same idempotency key and same body returns the prior result with `duplicate: true`. Reusing an idempotency key with another body or reusing a nonce for another callback returns `409 callback_replay`. Durable callback receipts and state row locks make this replay behavior authoritative across processes.

## Audit Contract

`AuditEvent` is append-only through instance and queryset APIs. PostgreSQL additionally installs a trigger rejecting SQL `UPDATE` and `DELETE`. Audit writes recursively replace values under known credential keys with `[REDACTED]`. Command payload bodies and grant secrets are not copied into command lifecycle audit events.

The trigger means reversing the initial audit migration drops the trigger before dropping the table. Operational retention must archive rather than update or delete audit rows unless a separately approved retention migration deliberately changes this invariant.

## Assumptions

- The parallel tenancy work supplies `workspaces.Workspace` in migration `workspaces.0001_initial`, with a unique `public_id` UUID.
- Workspace policy and membership services supply the callable passed to `ToolRegistry.preflight`; this package does not infer roles.
- `USE_TZ=True`, `TIME_ZONE='UTC'`, and a protected production `SECRET_KEY` remain deployment invariants.
- No outbox dispatcher, n8n workflow, Agent, provider call, or business-object callback mutation is part of Phase 1.
