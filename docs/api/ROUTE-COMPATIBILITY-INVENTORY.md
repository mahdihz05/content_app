# Route Compatibility Inventory

Baseline: `main` at `a73bda74d906a84697e32536aa37361d60d1d91e`, inspected 2026-09-13.

## Classification

- `active`: linked or called by a currently rendered first-party page.
- `compatibility`: retained alias that renders a current template.
- `orphaned`: routed with no reachable first-party consumer, or an unreachable consumer.
- `broken-consumer`: reachable browser code calls a route not present in Django.

## Root And Authentication

| Route | Authentication | Classification / consumer |
| --- | --- | --- |
| `/`, `/api/chat/` | Public | Active landing page and `landing.js` |
| `/admin/` | Django admin | Active operator route |
| `/test/` | Login | Orphaned debug page |
| `/auth/register`, `/auth/login`, `/auth/logout` | Mixed | Active template/session flow |
| `/auth/api/v1/register`, `/auth/api/v1/login` | Public | Active form consumers |
| `/auth/api/v1/users`, `/auth/api/v1/user` | Login | Orphaned API; security review required |

## Dashboard Templates

All dashboard routes require a login session.

| Route family | Classification |
| --- | --- |
| `/dashboard/`, `/dashboard/campaign-list/`, `/dashboard/create-campaign/` | Active |
| `/dashboard/campaign/content-items/<id>/` | Active with broken API consumers |
| `/dashboard/content/create/` | Active AI-chat page with two stale API paths |
| `/dashboard/content/list/` | Active with broken list/edit consumers |
| `/dashboard/content/chat/` | Orphaned alias |
| `/dashboard/messaging/`, `accounts/`, `bulk-send/`, `auto-reply/` | Active templates with absent legacy APIs |
| `/dashboard/messaging/accounts/list/`, `accounts/create/`, `campaigns/`, `campaigns/create/`, `campaigns/<id>/`, `ai-chat/` | Compatibility aliases |
| `/dashboard/telegram/channels/` | Active Telegram management page |
| `/dashboard/test/` | Orphaned debug page |

## Campaign And Platform APIs

| Routes | Classification |
| --- | --- |
| `/campaign/api/v1/campaign_list`, `create_campaign`, `get_goal_list`, `get_goal_schema` | Active |
| `/platform/api/v1/get_platforms` | Active |
| `/campaign/api/v1/campaign_detail`, `update_campaign`, `delete_campaign`, `get_all_goal_schema` | Orphaned or debug-only; retained |

Campaign detail/update/delete use global primary-key lookup and are not accepted as a V2 authorization contract.

## Content APIs

| Routes | Classification |
| --- | --- |
| `/content/api/v1/ai/chat/send/`, `ai/chat/new/` | Active |
| `/content/api/v1/content/<id>/` | Active side-panel lookup |
| `/content/api/v1/ai/chat/generate-image/`, `ai/chat/sessions/<id>/` | Routed but current JS calls different paths |
| `/content/ai/chat/` | Orphaned and references a missing template |
| Remaining `/content/api/v1/content/`, keyword, generation, and source routes | Routed compatibility/backend surface with no reachable current consumer |

Known current JS drift:

| Browser path | Routed path |
| --- | --- |
| `/content/api/v1/ai/generate-image/` | `/content/api/v1/ai/chat/generate-image/` |
| `/content/api/v1/ai/session/<id>/history/` | `/content/api/v1/ai/chat/sessions/<id>/` |

The routed final-generation view also calls absent
`PromptService.build_content_generation_prompt()` and
`AITextService.generate_text()` methods. Characterization tests mock both broken
boundaries to preserve evidence of the current persistence behavior; Phase 0
does not silently redefine or repair the provider contract.

The baseline backend image also referenced `requirements.txt` and `manage.py`
at the `backend/` context root even though both are under `backend/app/`.
Phase 0 corrects only these Docker `COPY` paths so the characterized application
can be built and tested.

## Research And Telegram

- All `/research/api/v1/ai/research/...` routes are consumed only by the unreachable legacy stepper. They currently lack authentication and ownership checks and are not an accepted V2 contract.
- Telegram verification, confirmation, channel list, and delete routes are active.
- Telegram multi/single publish and log routes are routed but have no reachable current consumer.
- Multi-channel publish scopes channels but not the content lookup. This is a known authorization defect, not desired compatibility behavior.

## Broken Browser Consumers

- Current content list calls `/content/api/v1/get-content-items/` and `/content/edit/<id>/`; neither exists.
- Campaign content items calls missing content-list/create routes and contains a localhost-only navigation URL.
- Current messaging templates call inactive `/messaging/api/accounts/`, bulk-send, and auto-reply route families.
- Dashboard links `/ai/chat/`; login links `/forgot-password`; neither exists.
- Unrendered `dashboard/create_content.html` and its scripts call removed stepper endpoints.
- `messaging_automation___older` is not installed or included and remains orphaned legacy code.

## Automated Verification

Resolver discovery recursively walks `django.urls.get_resolver().url_patterns` and records route, name, callback, namespace, and converters. Consumer verification scans first-party HTML/JavaScript for URL tags, form actions, `fetch`, XHR, and location changes, normalizes dynamic IDs, and compares same-origin references to resolver patterns. Browser smoke captures requests and console errors for the scenarios in `BROWSER-SMOKE-SPEC.md`.
