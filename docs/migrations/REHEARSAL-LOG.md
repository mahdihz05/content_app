# Migration And Restore Rehearsal Log

## Required Procedure

1. Identify the production-like PostgreSQL snapshot and record a non-sensitive backup checksum.
2. Capture `showmigrations --plan`, row counts, and schema version before change.
3. Restore into an isolated database, apply the tracked migration graph, and run system/characterization checks.
4. Reconcile schema, row counts, and representative content/Telegram records.
5. Restore the pre-migration backup into a second isolated target and repeat checks.
6. Record owner, timestamps, commands, checksums, results, and approval without credentials or personal data.

## Current Run

Status: **PASS** on 2026-09-13 against disposable PostgreSQL 16.12.

- Applied all 56 migrations through `content.0019` to `content_app_ci`.
- Seeded one user, campaign, content item, Telegram channel, and publish log.
- Created a custom-format `pg_dump` and restored it into the separate `content_app_restore` database with `--exit-on-error`.
- Source and restore both contained 56 migration rows, 35 public tables, and domain counts of one for each seeded entity.
- `python manage.py check` and `python manage.py migrate --check` passed against the restored database.
- No backup artifact, credentials, production data, or database volume was added to source control.

## Verification Repeat

Status: **PASS** on 2026-09-13 against disposable PostgreSQL 16.

- Recreated the source database from an empty database and applied all 56 migrations through `content.0019`.
- Seeded one user, campaign, content item, Telegram channel, and publish log.
- Created one custom-format dump and restored it with `--exit-on-error` into two independent empty databases.
- Source and both restores matched at 56 migration rows, 35 public tables, and one row for each representative domain model.
- `python manage.py check` and `python manage.py migrate --check` passed against both restores.
- Non-sensitive dump checksum: `afd2fa8e669f42e812053f03fb5062e9bec1ba1e7fb10f209c40c66fe7f6ea95`.
- The three disposable databases and dump artifact were removed after verification.

This is production-like migration/restore rehearsal evidence, not a claim that the real production database has been backed up or changed.
