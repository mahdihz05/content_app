# Deferred External Gates

Only actions requiring provider, deployment, remote-history policy, or acceptance-owner authority are listed here. No item is recorded as verified until non-sensitive evidence is attached.

| Gate | Required external action | Completion evidence |
| --- | --- | --- |
| Credential revocation | Revoke or rotate every historically exposed AI, Telegram, database, Django, n8n, and browser-profile credential or token. | Provider/account owner, non-sensitive credential identifier, revocation timestamp, and validation result. |
| Deployment secret injection | Store replacement values in the approved secret manager and inject only environment references into the deployment. | Deployment identifier, secret-store reference names, and smoke result without values. |
| Git-history remediation | Approve and coordinate a history rewrite, force-update policy, collaborator notification, and stale clone/cache invalidation. | Approved incident record, rewritten boundary commit, clean redacted history scan, and owner confirmation. |
| Phase acceptance | Reviewer, QA, and owner validate the Phase 0 evidence and sign the gate. | Review/QA result and dated owner sign-off. |

Repository implementation, local verification, and hosted CI are complete and are not deferred.
