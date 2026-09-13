# n8n Workflow Governance

The inspected repository snapshot contains one inactive workflow named `ai`, no registered webhook, no credential row, and no stored execution. This proves snapshot state only. A later read-only inspection of the separate deployed Compose `n8n_data` volume also found no workflow, webhook, credential, or execution records.

Production export requires a quiesced SQLite backup (including WAL state), pinned n8n image digest, network-isolated export, parameter and identifier redaction, schema/secret scan, human review, and manifest digest. Raw exports remain outside Git. Deployment requires owner approval, a named Django capability contract, mocked provider tests, pinned version, and documented rollback. Compose pins n8n 2.8.3 by image digest. No workflow was activated by Phase 0 work.
