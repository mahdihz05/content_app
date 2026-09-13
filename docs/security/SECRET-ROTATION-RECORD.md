# Secret Rotation Record

## Repository Remediation

- 2026-09-13: hard-coded AI credentials were removed from Django settings and ad-hoc scripts.
- 2026-09-13: hard-coded Telegram credentials and executable ad-hoc provider scripts were removed.
- 2026-09-13: `.env` patterns were added to `.gitignore`; the file was removed from the tracked tree while Git history remains pending owner-controlled remediation.
- 2026-09-13: `.env`, `n8n/data/`, and `volume/` were removed from the Git index while their local ignored files were preserved.
- 2026-09-13: 1,636 committed Chromium browser-profile files were removed from the Git index and permanently ignored while local files were preserved.
- Runtime settings now read AI and Telegram credentials from environment variables.
- Provider clients are initialized only when called, so checks and non-provider operations do not require placeholder credentials.
- The resulting tracked tree has zero Gitleaks findings. A redacted full-history scan reports 13 findings.

## External Actions Required

- Revoke and rotate every exposed AI, Telegram, database, Django, n8n, and browser-profile credential or token with the deployment owner.
- Update the approved secret store/deployment injection and verify smoke checks with replacement references.
- Coordinate a Git-history rewrite and re-run the history scan after provider revocation; current-tree cleanup alone does not remove historical blobs.

Status: **INTERNAL REMEDIATION COMPLETE / EXTERNAL ROTATION PENDING**. No credential is recorded as rotated or revoked without deployment-owner evidence.
