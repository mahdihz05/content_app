# Executive Summary

**VERIFIED.** The repository contains a Django 5.2 project with PostgreSQL configuration, Django-template/vanilla-JavaScript UI, OpenAI-compatible AI calls, and an active Telegram channel/publishing integration. It is not a React application: no React source, Node application manifest, or frontend build configuration was found; rendered pages and browser logic are under `backend/app/templates/` and `backend/app/static/assets/scripts/`.

**VERIFIED.** The active product has campaign-owned content records, an AI chat-led content workflow, keyword/outline/final-content endpoints, research-source records, and direct synchronous Telegram publishing. The primary route composition is `backend/app/main/urls.py:10-30`; active content API routes are in `backend/app/content/urls.py:46-200`; active messaging routes are in `backend/app/messaging_automation/urls.py:12-54`.

**VERIFIED.** n8n is provisioned as a Docker Compose service (`docker-compose.yml:101-135`) and a persisted n8n SQLite file exists at `n8n/data/database.sqlite`. No Django-to-n8n HTTP client, webhook, workflow export, or workflow invocation was found in tracked Python sources. The individual persisted n8n workflow definitions were not decoded during this audit, so their contents are **UNKNOWN**.

**VERIFIED.** There are major delivery and security gaps: secrets are present in tracked/configured files (`.env`, `backend/app/main/settings.py:23,179-180`, `backend/app/utils/test.py:44`); production settings are development-oriented (`settings.py:26-28`); several API paths lack ownership checks; and first-party test modules are generated stubs. These are current-state findings, not a redesign proposal.

# Current Architecture

**VERIFIED.** The running Compose topology is PostgreSQL 16 (`db`), Django (`web`), n8n, and Nginx on one bridge network: `docker-compose.yml:7-180`.

**VERIFIED.** Django is configured for PostgreSQL, not SQLite, through `DATABASES` in `backend/app/main/settings.py:89-98`; Compose injects the database host as `db` at `docker-compose.yml:55-60`. A local `backend/app/db.sqlite3` is also present in the worktree, but no settings path selects it, so its runtime role is **UNKNOWN**.

**VERIFIED.** The Docker web command waits for PostgreSQL, runs migrations, attempts `collectstatic`, then starts `python manage.py runserver 0.0.0.0:8000` (`docker-compose.yml:72-88`). WSGI and ASGI modules exist (`backend/app/main/wsgi.py`, `backend/app/main/asgi.py`), but no production WSGI/ASGI server configuration was found.

**VERIFIED.** The Nginx service mounts `nginx/default.conf` (`docker-compose.yml:142-162`), and that configuration file is empty. Consequently, an intended Nginx reverse-proxy/TLS configuration is **UNKNOWN/not evidenced**.

**VERIFIED.** Django has the following installed first-party apps: `user`, `dashboard`, `campaigns`, `platforms`, `content`, `ai`, `research`, and `messaging_automation` (`backend/app/main/settings.py:33-49`).

# Repository Map

**VERIFIED.** Important top-level paths are:

- `backend/app/main/`: Django project settings and root URLs.
- `backend/app/user/`: custom phone-number authentication and user APIs.
- `backend/app/dashboard/`: authenticated server-rendered dashboard pages and page routes.
- `backend/app/campaigns/`: campaign, goal, form-schema, and campaign-social-account domain.
- `backend/app/content/`: central content models, current APIs, legacy views, templates, and schema seeding command.
- `backend/app/ai/`: providers, prompts, orchestration, pipelines, interview/job/knowledge models, and landing/chat endpoints.
- `backend/app/research/`: research-source/job models, search service, and research endpoints.
- `backend/app/platforms/`: platform and social-account models plus platform listing/stub account-connection code.
- `backend/app/messaging_automation/`: active Telegram verification, publishing, and publish-log code.
- `backend/app/messaging_automation___older/`: a separate legacy messaging/Selenium/Bale implementation. It is not listed in `INSTALLED_APPS` (`backend/app/main/settings.py:33-49`), so it is not an active Django app under these settings.
- `backend/app/templates/` and `backend/app/static/assets/`: server-rendered UI and imperative JavaScript/CSS.
- `selenium_service/` and `browser_profiles/`: standalone Selenium-related source/runtime profile artifacts. Their Compose/runtime wiring is **UNKNOWN** because no Compose service references them (`docker-compose.yml:1-180`).
- `n8n/data/`: persisted n8n state, including `database.sqlite` and configuration (`n8n/data/config`).
- `volume/postgres/`: local PostgreSQL volume artifacts; they are runtime data, not schema source of truth.
- `docs/v2-analysis/02-independent-v2-architecture.md`: a pre-existing V2 document. It was not treated as proof of implemented behavior.

# Backend

**VERIFIED.** Root route groups are `/auth/`, `/dashboard/`, `/campaign/`, `/platform/`, `/content/`, `/research/`, and `/messaging/`, plus landing and landing chat routes (`backend/app/main/urls.py:10-27`).

**VERIFIED.** Backend APIs use a mixture of Django function views, Django REST Framework `APIView`s, hand-parsed JSON, and limited serializers. For example, current AI/content routing imports functions and API views from `content.views.ai_chat` (`backend/app/content/urls.py:3-42`); Telegram channel APIs use DRF permission classes (`backend/app/messaging_automation/views/channel_management.py:12-280`); user serializers are in `backend/app/user/serializers.py`.

**VERIFIED.** Major API domains include:

- Authentication: registration, login, logout, user lookup/listing in `backend/app/user/urls.py:4-15` and `backend/app/user/views/`.
- Campaign CRUD, goals, and dynamic form schemas in `backend/app/campaigns/urls.py:11-27`.
- Current content/chat API: session start/send/history/new conversation, image generation, content CRUD, keyword CRUD, outline/final generation, and research-source attachment in `backend/app/content/urls.py:46-200`.
- Research query/selection/fetch/finalize endpoints in `backend/app/research/urls.py:7-12`.
- Telegram verification, channel listing/deletion, publish, and logs in `backend/app/messaging_automation/urls.py:12-54`.
- Platform listing in `backend/app/platforms/urls.py:4-8`; account-connection functions exist in `backend/app/platforms/views/account_connection.py:6-30` but are stubs and are not evidenced as routed.

**VERIFIED.** The content app contains both current `ai_chat.py`-based endpoints and older standalone views such as `contentItem_manager.py`, `generate_outline.py`, `generate_final_content.py`, and `content_workflow.py`. The active router only exposes the `ai_chat.py` route set (`backend/app/content/urls.py:3-200`), while legacy browser scripts still target older endpoint names (`backend/app/static/assets/scripts/create_content_api.js:101,193,284,336,510,538`).

# Frontend

**VERIFIED.** The UI is Django-template based, Persian/RTL-oriented, and uses vanilla JavaScript. The shared dashboard shell/navigation is `backend/app/templates/dashboard/base.html:25-178`; all dashboard page views are decorated with `@login_required` in `backend/app/dashboard/views.py:9-131`.

**VERIFIED.** The main rendered pages include:

- Authentication: `templates/user/login.html`, `templates/user/register.html`.
- Dashboard/campaigns: `templates/dashboard/dashboard.html`, `campaign_list.html`, `create_campaign.html`, `campaign_content_items.html`.
- Content: `templates/dashboard/content_list.html`, `create_content_ai.html`, and `create_content.html`.
- Messaging: `templates/messaging/dashboard.html`, `accounts.html`, `bulk_send.html`, `auto_reply.html`; active Telegram channel management is `templates/messaging_automation/telegram_channels.html`.

**VERIFIED.** The primary “create content” dashboard view renders the AI-chat template, not the older eight-step template (`backend/app/dashboard/views.py:49-55`; `backend/app/dashboard/urls.py:99-103`). No render reference to `templates/dashboard/create_content.html` was found. Therefore, the older eight-step UI is **INFERRED** to be orphaned/unreachable from current page routing.

**VERIFIED.** Browser state is local and imperative: `window.ContentFlowState` and `window.globalStore` are created in `backend/app/static/assets/scripts/create_content_api.js:9-20,206-211`; AI chat stores state in an instance and periodically saves it in `localStorage` (`backend/app/static/assets/scripts/ai_chat.js:107-126,945-975`); theme state also uses `localStorage` (`base.js:40-52`). No React, Redux, Zustand, React Query, or frontend package/build configuration was found.

**VERIFIED.** Frontend/API drift exists. Examples: `create_content_api.js` posts `/content/api/v1/create/` but current routing exposes `/content/api/v1/content/` (`create_content_api.js:101`; `content/urls.py:91-96`); AI chat requests `/content/api/v1/ai/generate-image/` but routing exposes `/content/api/v1/ai/chat/generate-image/` (`ai_chat.js:130`; `content/urls.py:66-71`).

# Database

**VERIFIED.** PostgreSQL is the configured primary database (`backend/app/main/settings.py:89-98`). Django migrations exist under each active app's `migrations/` directory.

**VERIFIED.** The principal ownership chain is `CustomUser -> Campaign -> ContentItem`: `Campaign.user` is defined in `backend/app/campaigns/models/Campaign.py:20-27`; `ContentItem.campaign` is defined in `backend/app/content/models/ContentItem.py:32-37`.

**VERIFIED.** Key models and relationships:

- `CustomUser`: phone-number username, name, plan, staff/active flags (`backend/app/user/models/CustomUser.py:23-38`).
- `CampaignGoal`, `Campaign`, `CampaignFormSchema`, `CampaignForm`, and `CampaignSocialAccount`: campaign configuration and platform association (`backend/app/campaigns/models/`).
- `Platform` and user-linked `SocialAccount` (`backend/app/platforms/models/Platform.py`; `SocialAccount.py:5-11`). `SocialAccount.metadata` is JSON and the field is named `user_id` despite being a foreign key.
- `ContentItem`: campaign-linked content with title, keywords, description, platform/language, JSON `information` and `metadata`, workflow status, research source JSON, and publication fields (`backend/app/content/models/ContentItem.py:5-128`).
- Content children: `Keyword`, `ResearchSource`, `GeneratedContent`, `Outline`/`OutlineSection`, `ContentForm`, `CreateContentStep`, `AIChatSession`, and `AIMessage` (`backend/app/content/models/__init__.py:1-9`; individual model files).
- AI: `AIJob`, `AIInterviewSession`, `AIInterviewMessage`, `AIInterviewState`, `KnowledgeSource`, and `DocumentEmbedding` (`backend/app/ai/models/`). `DocumentEmbedding` stores embeddings in a JSON field, rather than a vector database field (`DocumentEmbedding.py:4-8`).
- Telegram: user-owned `TelegramChannel`, `ChannelVerification`, and `TelegramPublishLog` (`backend/app/messaging_automation/models/`).

**VERIFIED.** `GeneratedContent` supports a version/approval representation (`backend/app/content/models/GeneratedContent.py:4-20`), but current generation stores generated text in `ContentItem.information` (`backend/app/content/views/ai_chat.py:1084-1093`). Thus, a durable versioned content-history path is present in schema but is not evidenced as used by the active generation flow.

# AI System

**VERIFIED.** Two OpenAI-compatible clients target `https://api.gapgpt.app/v1`: `AITextService` supports text chat and history (`backend/app/ai/services/ai_text_service.py:10-112`), while `AIClient` supports chat, image generation, transcription, and text-to-speech (`backend/app/ai/clients/ai_client.py:5-89`).

**VERIFIED.** `AIClient.generate_image` can persist base64 responses into `MEDIA_ROOT/ai_images` and return a media URL (`backend/app/ai/clients/ai_client.py:31-61`). Sample generated media exists under `backend/app/media/ai_images/`.

**VERIFIED.** Prompts exist for interview, generation, keyword, outline, research, SEO, and summary behavior under `backend/app/ai/prompts/`. The substantial current conversation controller is `ConversationOrchestrator` (`backend/app/ai/orchestration/conversation_orchestrator.py:21-1907`), with stages from greeting through platform/goal/details/research/generation/completion (`:23-33`).

**VERIFIED.** AI-related model scaffolding for knowledge/memory exists: `KnowledgeSource` is user-owned with a source type (`backend/app/ai/models/KnowledgeSource.py:5-9`), and chunks/JSON embeddings are represented by `DocumentEmbedding` (`DocumentEmbedding.py:4-8`). No active ingestion, chunking, retrieval, semantic search, or RAG invocation path was evidenced in the current routed APIs. Workspace memory/RAG is therefore **UNKNOWN as a working capability**.

**VERIFIED.** Runtime method contracts conflict: `AITextService` supplies `chat()` and `chat_with_history()` only (`ai_text_service.py:27-112`), while active/legacy generation code calls missing `generate_text()`/`generate()` methods (`backend/app/content/views/ai_chat.py:905,1082`; `generate_final_content.py:74`; `generate_keyword.py:82`). These paths are **INFERRED** likely to raise `AttributeError` if executed as inspected.

# Content Generation

**VERIFIED.** The current chat workflow can create content, collect platform/goal/details, optionally research, generate content, and optionally publish. Its state machine is in `backend/app/ai/orchestration/conversation_orchestrator.py:23-33,130-1907`; its HTTP surface is in `backend/app/content/views/ai_chat.py` and `backend/app/content/urls.py:52-188`.

**VERIFIED.** A separate legacy/stepper workflow has campaign, basic-info, dynamic-form, keyword, AI-research, knowledge-base, confirmation, outline, and final-content UI stages (`backend/app/templates/dashboard/create_content.html:12-278`; `backend/app/static/assets/scripts/create_content_stepper.js:18-844`). Its expected endpoints do not match the active router, as documented in the Frontend section.

**VERIFIED.** Research implementation is mixed. `WebSearchService` can query SerpAPI with a 10-second timeout (`backend/app/research/services/web_search_service.py:5-53`), but research fetching states that it simulates scraping with AI (`backend/app/research/views/fetch.py:16-18`). Direct use of `WebSearchService` by the routed research views was not found.

**VERIFIED.** Existing content history is limited and fragmented: `ContentItem` has timestamps and JSON payloads (`ContentItem.py:74-82,122-128`), chat sessions/messages are persisted (`backend/app/content/models/ai_chat.py`), `GeneratedContent` has schema support for versions (`GeneratedContent.py:4-20`), and Telegram publish logs persist outcomes (`telegram_publish_log.py:6-38`). A unified content-history timeline, imported external history, or analytics/intelligence model is **UNKNOWN/not evidenced**.

**VERIFIED.** Existing brainstorming-like behavior is the interview/chat orchestration and prompt set, not a distinct brainstorming domain model or route (`ai/orchestration/conversation_orchestrator.py`; `ai/prompts/interview_prompts.py`). Existing content-planning-like behavior is campaign configuration plus content items and their statuses, not an explicit Content Map/plan model (`campaigns/models/`; `content/models/ContentItem.py`).

# Publishing & Automation

**VERIFIED.** Active publishing is Telegram-only. Users verify a channel by posting a generated token, scanning bot updates, then creating/updating a `TelegramChannel` (`backend/app/messaging_automation/views/channel_management.py:12-140`).

**VERIFIED.** `TelegramPublisher` sends generated text, image, or video synchronously using `TelegramAPI`, writes a `TelegramPublishLog`, and updates the `ContentItem` publication fields (`backend/app/messaging_automation/services/telegram_publisher.py:13-68`). `TelegramAPI` uses synchronous `requests` calls and defines no explicit timeout (`telegram_api.py:10-38`).

**VERIFIED.** A content record has `auto_publish`, `publish_immediately`, `scheduled_at`, `published_at`, and `publish_status` fields (`backend/app/content/models/ContentItem.py:95-120`). No active scheduler/worker that executes `scheduled_at` was found.

**VERIFIED.** The orchestrator's automatic-publish behavior selects the first active verified user channel rather than proving a campaign-specific channel selection (`backend/app/ai/orchestration/conversation_orchestrator.py:1843-1879`).

**VERIFIED.** Legacy bulk-send/auto-reply UI and a legacy Selenium/Bale automation subtree exist (`backend/app/templates/messaging/`; `backend/app/messaging_automation___older/`). That legacy code starts daemon threads in-process (`messaging_automation___older/workers/campaign_worker.py:19-27`) but is outside the installed app list. Whether it is deployed separately is **UNKNOWN**.

# Integrations

**VERIFIED.** Implemented external service calls are:

- GapGPT-compatible OpenAI API for text, images, transcription, and speech (`backend/app/ai/services/ai_text_service.py:10-56`; `ai/clients/ai_client.py:8-89`).
- Telegram Bot API for channel verification and publication (`backend/app/messaging_automation/services/telegram_api.py:4-38`; `views/channel_management.py:55-170`).
- SerpAPI search service (`backend/app/research/services/web_search_service.py:5-53`).

**VERIFIED.** Platform and social-account schema exists, and platform names are mapped in the conversation orchestrator (`backend/app/platforms/models/`; `backend/app/ai/orchestration/conversation_orchestrator.py:35-61`), but platform account connection code is stubbed and not routed (`backend/app/platforms/views/account_connection.py:6-30`). Therefore, connected-platform import/readback for prior content is **UNKNOWN/not implemented in inspected active code**.

**VERIFIED.** Selenium and Chromium dependencies/settings exist (`backend/app/requirements.txt:9-13`; `backend/app/main/settings.py:183`), as does standalone `selenium_service/`, but no active service in Compose provides the configured `selenium` host (`docker-compose.yml:1-180`).

# Existing Background Processing

**VERIFIED.** Celery, Redis, and `django-celery-beat` are listed in `backend/app/requirements.txt:15-17`, and Celery broker/serializer/time-zone settings exist in `backend/app/main/settings.py:201-209`.

**VERIFIED.** No Celery application module, task module/decorator, task dispatch, beat schedule, Redis Compose service, Celery worker, or beat service was found. The configured broker points to `127.0.0.1:6379` (`settings.py:201`), while Compose defines no Redis service (`docker-compose.yml:1-180`). Hence an operational queue/scheduler is **not evidenced**.

**VERIFIED.** `AIJob` tracks job status and parent-child job relationships (`backend/app/ai/models/AIJob.py:5-57`), and `ai_job_service.py` updates model state (`backend/app/ai/services/ai_job_service.py:19-89`); no job executor linkage was found.

# Workspace / Permissions

**VERIFIED.** Authentication uses a custom `CustomUser` authenticated by phone number (`backend/app/user/models/CustomUser.py:23-38`; `backend/app/user/CustomAuthBackend.py:7-13`) and Django login/session middleware (`backend/app/main/settings.py:51-57,100-103`; `backend/app/user/views/login_view.py`). JWT or token authentication configuration was not found.

**VERIFIED.** There is no `Workspace`, organization, membership, role, invitation, or workspace selector model/UI in the inspected project. Ownership is user/campaign based, not workspace based. `CustomUser.plan` is a plain string field (`CustomUser.py:23-38`); plan enforcement/quotas are **UNKNOWN/not evidenced**.

**VERIFIED.** Authorization is inconsistent. Modern `ai_chat.py` paths frequently filter by `campaign__user=request.user` (`backend/app/content/views/ai_chat.py:464-579,638-867`), but campaign update/delete/detail fetch by primary key without user filtering (`backend/app/campaigns/views/campaign_manager.py:99-105,132-137`; `campaign_detail.py:12-29`). Research endpoints have no visible authentication decorator/permission class (`backend/app/research/views/queries.py:10-55`; `selection.py:8-16`; `fetch.py:9-58`; `finalize.py:8-31`).

**VERIFIED.** The multi-channel publish endpoint checks requested channels belong to the caller but loads `ContentItem` globally by ID (`backend/app/messaging_automation/views/channel_management.py:230-250`). This is an object-authorization boundary risk.

# Existing Tests

**VERIFIED.** First-party app `tests.py` files are empty generated stubs, including `backend/app/content/tests.py:1-3`, `ai/tests.py:1-3`, `campaigns/tests.py:1-3`, `dashboard/tests.py:1-3`, `messaging_automation/tests.py:1-3`, `platforms/tests.py:1-3`, and `research/tests.py:1-3`.

**VERIFIED.** No first-party frontend unit, integration, contract, or browser/E2E test configuration was found. Vendored Chart.js contains upstream tests in `backend/app/static/assets/Chart.js-master/test/`, which do not evidence application coverage.

**UNKNOWN.** No test command was executed in this read-only audit; actual pass/fail state and numerical coverage are unknown. No coverage configuration or CI workflow was found.

# Technical Debt

**VERIFIED.** Duplicate/competing implementations exist: old content CRUD/workflow views alongside current chat APIs (`backend/app/content/views/` versus `content/urls.py:3-200`); two outline generators (`content/views/generate_outline.py` and `content/views/ai_chat.py:961-1022`); active and uninstalled legacy messaging automation; and UI assets that target non-current endpoints (`static/assets/scripts/create_content_api.js`).

**VERIFIED.** Persisted-state vocabularies conflict. `ContentItem.status` choices omit `error` (`backend/app/content/models/ContentItem.py:7-19`), but the orchestrator sets it (`ai/orchestration/conversation_orchestrator.py:1524-1528`). `PUBLISH_STATUS_CHOICES` declares `failed` (`ContentItem.py:20-26`), but publisher writes `publish_failed` (`telegram_publisher.py:49-54`). Keyword source choices differ from values written by current views (`content/models/Keyword.py:7-20`; `content/views/ai_chat.py:443-448,920-925`).

**VERIFIED.** Error handling is mostly local `try/except`, `print`, and API responses containing raw exception text, for example `backend/app/content/views/ai_chat.py:159-167`, `campaigns/views/campaign_manager.py:79-84`, and `messaging_automation/views/channel_management.py:59-62`.

**VERIFIED.** Logging configuration explicitly configures only `messaging_automation` console logging (`backend/app/main/settings.py:185-197`). Structured logging, correlation IDs, central exception reporting, health/readiness endpoints, metrics, and tracing are not evidenced.

**VERIFIED.** Some client rendering inserts server/AI values with `innerHTML`, including research/final content and channel data (`backend/app/static/assets/scripts/create_content_stepper.js:322-329,383-407,703-736`; `templates/messaging_automation/telegram_channels.html:819-860`). Server sanitization of those values is **UNKNOWN**.

**VERIFIED.** Repository/configuration hygiene is fragile: `.env` is tracked and not ignored (`.gitignore:1-20`), development secrets are hard-coded (`settings.py:23,179-180`), dependencies are largely unpinned (`backend/app/requirements.txt:2-20`), and `content/migrations/0019_alter_contentitem_status.py` is currently untracked according to `git status` observed during audit.

# Candidate Processes for n8n

The following candidates identify existing operational processes that are orchestration-oriented. They are not a future architecture design.

**VERIFIED candidate: scheduled publishing.** `ContentItem.scheduled_at` exists without an observed executor (`backend/app/content/models/ContentItem.py:107-120`; `docker-compose.yml:1-180`). A scheduler-triggered publish process is a candidate.

**VERIFIED candidate: Telegram publication delivery.** Publication is a synchronous request-cycle operation that invokes an external API and records outcomes (`backend/app/messaging_automation/services/telegram_publisher.py:13-68`; `telegram_api.py:10-38`). It is a candidate for external workflow orchestration/retries.

**VERIFIED candidate: platform import/synchronization.** Platform/social-account schemas and connection stubs exist (`backend/app/platforms/models/`; `platforms/views/account_connection.py:6-30`), but no active importer exists. Any future periodic import is a candidate process, not an existing implementation.

**VERIFIED candidate: research/search acquisition.** SerpAPI querying and simulated fetch exist as external-call steps (`backend/app/research/services/web_search_service.py:5-53`; `research/views/fetch.py:9-58`). They are candidates for a workflow with retries/rate control.

**VERIFIED candidate: legacy messaging campaign execution.** The old implementation starts in-process threads (`backend/app/messaging_automation___older/workers/campaign_worker.py:19-27`), making it an orchestration candidate if the legacy feature is retained. Its active deployment status is **UNKNOWN**.

# Components That Must Remain in Core Backend

These are current responsibilities with Django-owned state or authorization. This is an evidence-based boundary observation, not a V2 design.

**VERIFIED.** Identity/session authentication and authorization policy are core-backend responsibilities because the custom user model and backend are Django-managed (`backend/app/user/models/CustomUser.py:23-38`; `user/CustomAuthBackend.py:7-13`; `main/settings.py:100-103`).

**VERIFIED.** The canonical relational data model and ownership checks belong in Django: campaigns/content/user/channel/publish-log models are ORM entities (`backend/app/campaigns/models/`, `content/models/`, `messaging_automation/models/`).

**VERIFIED.** API validation, object-level authorization, and durable write-side state transitions must remain governed by the backend because current endpoints expose these operations (`backend/app/content/urls.py:91-198`; `messaging_automation/urls.py:12-54`).

**VERIFIED.** AI conversation state and content records are currently persisted in Django models and orchestrated from Django (`backend/app/content/models/ai_chat.py`; `ai/orchestration/conversation_orchestrator.py:103-124`). Whether all orchestration should remain there is a future design decision and is **UNKNOWN**.

# Risks

**VERIFIED: secret exposure.** Plaintext secrets/tokens are present in tracked configuration/source: `.env:2-22`, `backend/app/main/settings.py:23,179-180`, `backend/app/utils/test.py:44`, and `n8n/data/config:1-3`. Validity of each credential is **UNKNOWN**.

**VERIFIED: production safety.** `DEBUG=True`, wildcard hosts, and wildcard CORS combined with credentials are configured (`backend/app/main/settings.py:26-28,159-176`). The web container runs Django's development server (`docker-compose.yml:72-88`).

**VERIFIED: authorization/data isolation.** Several resource fetches are globally addressed by primary key without user ownership filtering, as cited in Workspace / Permissions. User APIs also expose all users through an authenticated endpoint with a serializer containing `password` (`backend/app/user/views/users_api.py:10-19`; `user/serializers.py:5-10`).

**VERIFIED: reliability.** There is no evidenced durable worker/scheduler despite status/scheduling fields and Celery configuration (`ContentItem.py:107-120`; `main/settings.py:201-209`; `docker-compose.yml:1-180`). Telegram HTTP calls have no timeout (`telegram_api.py:10-38`).

**VERIFIED: deployment.** Nginx's mounted virtual-host file is empty (`nginx/default.conf:1`; `docker-compose.yml:154-159`), `STATIC_ROOT` is referenced but not set (`backend/app/main/urls.py:29`; `main/settings.py:137-142`), and Compose suppresses `collectstatic` failure (`docker-compose.yml:83-87`).

**VERIFIED: untested behavior.** First-party tests are stubs and no CI configuration was found, as documented under Existing Tests.

# Unknowns / Missing Evidence

- **UNKNOWN.** Contents, activation state, triggers, credentials, and execution history of persisted n8n workflows in `n8n/data/database.sqlite`; only the service declaration and persisted database file were verified.
- **UNKNOWN.** Any infrastructure outside this repository: managed Redis, production reverse proxy/TLS, secrets manager, monitoring, CI/CD, backups, and disaster recovery.
- **UNKNOWN.** Production deployment topology, domains, environment overrides, database migration state, and real data volume.
- **UNKNOWN.** Whether any current external platform integration beyond Telegram is operational. Schema/stubs and platform name mappings are not evidence of connected accounts or imports.
- **UNKNOWN.** Whether AI keys, Telegram token, SerpAPI key, or committed database/n8n credentials are still valid; they are treated as exposed because they are present in repository material.
- **UNKNOWN.** Actual endpoint behavior under authentication, concurrent load, provider failures, and scheduled times, because this audit did not execute application requests or tests.
