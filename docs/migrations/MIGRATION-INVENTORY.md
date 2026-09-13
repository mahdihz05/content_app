# Migration Inventory

Baseline: `main` at `a73bda74d906a84697e32536aa37361d60d1d91e`, 2026-09-13.

- `content/migrations/0019_alter_contentitem_status.py` began as an untracked user-provided leaf depending on `0018_contentitem_auto_publish_and_more`; it is included in this implementation after review/rehearsal.
- With that file present, `python manage.py makemigrations --check --dry-run` reports no model changes.
- `python manage.py check` passes.
- PostgreSQL 16 forward migration applies all 56 migrations through `content.0019`; `showmigrations --plan` and `migrate --check` pass on the restored rehearsal database.
- The tracked SQLite file is not selected by Django settings and is not migration evidence.

No V2 migration was generated in Phase 0.
