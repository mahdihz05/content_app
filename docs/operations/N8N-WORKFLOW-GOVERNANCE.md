# n8n Workflow Governance

The inspected repository snapshot contains one inactive workflow named `ai`, no registered webhook, no credential row, and no stored execution. This proves snapshot state only: Compose uses the separate `n8n_data` named volume, which was unavailable on 2026-09-13 because Docker was not running.

Production export requires a quiesced SQLite backup (including WAL state), pinned n8n image digest, network-isolated export, parameter and identifier redaction, schema/secret scan, human review, and manifest digest. Raw exports remain outside Git. Deployment requires owner approval, a named Django capability contract, mocked provider tests, pinned version, and documented rollback. No workflow was activated by Phase 0 work.
