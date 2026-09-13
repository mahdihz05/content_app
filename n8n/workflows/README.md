# n8n Workflow Source Control

`n8n/data/` and deployed n8n state are not workflow source of truth. Reviewed workflow exports live here with a manifest entry and immutable version.

## Rules

- Names use `<capability>.v<major>` and filenames use kebab-case.
- Archive evidence is marked `deployable: false` and must never be imported into a connected environment.
- Exports contain no credential IDs, authentication values, webhook secrets, inline tokens, pin data, static data, executions, project/user IDs, or provider payloads.
- Secrets are referenced by approved aliases and injected in n8n credential storage.
- Every production workflow accepts only a Django command envelope, invokes a named capability, and sends a signed/idempotent callback.
- Human review, schema validation, secret scanning, mocked contract tests, version pinning, and rollback metadata are required before deployment.
- Activation and production deployment are separate owner-approved operations. Source control never activates a workflow.
