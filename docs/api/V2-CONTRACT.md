# V2 API And Tool Contract

## Compatibility

Existing routes and response bodies remain unchanged. V2 interfaces are mounted under `/api/v2/`. Correlation headers are additive to both legacy and V2 responses.

## Correlation

Requests may supply `X-Correlation-ID` containing 1-128 ASCII letters, digits, `.`, `_`, or `-`. Invalid or absent values are replaced with a UUID. Every response returns the effective ID.

## Errors

V2 errors use this non-sensitive shape:

```json
{
  "error": {
    "version": "v2",
    "code": "authentication_required",
    "message": "Authentication is required.",
    "details": {},
    "correlation_id": "request-id"
  }
}
```

Raw exceptions, provider payloads, credentials, SQL, and tracebacks are prohibited. This convention does not retroactively normalize legacy APIs.

## Health And Readiness

- `GET /api/v2/health/` is authenticated and reports process availability.
- `GET /api/v2/readiness/` is authenticated and checks the default database without disclosing dependency errors.

## Feature Flags

`V2_FEATURE_FLAGS` is a comma-separated environment value. Unknown and omitted flags are disabled. Phase 0 enables no V2 product behavior. Phase 1 may add workspace-aware resolution behind the same `is_feature_enabled(name, workspace)` interface.

## Future Tool Envelope

No Agent tool is enabled in Phase 0. Future calls use framework-independent versioned JSON containing `tool_name`, `tool_version`, actor/workspace context, command ID, idempotency key, effect class, validated input, and an explicit result schema. Allowed effect classes are `read`, `draft`, `mutate_internal`, and `consequential`. MCP runtime is not implemented.
