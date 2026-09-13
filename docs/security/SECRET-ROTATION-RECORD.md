# Secret Rotation Record

## Repository Remediation

- 2026-09-13: hard-coded AI credentials were removed from Django settings and ad-hoc scripts.
- 2026-09-13: hard-coded Telegram credentials and executable ad-hoc provider scripts were removed.
- 2026-09-13: `.env` patterns were added to `.gitignore`; the already tracked file and Git history still require owner-controlled remediation.
- 2026-09-13: `.env`, `n8n/data/`, and `volume/` were removed from the Git index while their local ignored files were preserved.
- Runtime settings now read AI and Telegram credentials from environment variables.

## External Actions Required

- Revoke and rotate every exposed AI, Telegram, database, Django, and n8n credential with the deployment owner.
- Update the approved secret store/deployment injection and verify smoke checks with replacement references.
- Complete Git-history remediation according to the owner's retention and incident-response policy; current-tree untracking does not erase history.
- Run a clean repository and history secret scan and retain its non-sensitive result.

Status: **BLOCKED**. No credential is recorded as rotated or revoked without deployment-owner evidence.
