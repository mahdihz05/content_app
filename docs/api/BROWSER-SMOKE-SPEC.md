# Phase 0 Browser Smoke Specification

Run `RUN_BROWSER_SMOKE=1 python manage.py test dashboard.browser_tests --noinput` with PostgreSQL and headless Chromium available.

## Required Scenarios

1. Public landing/login/register pages return HTML; protected dashboard pages redirect anonymous sessions.
2. Registration creates a session; logout ends it; login restores it.
3. Campaign list/create pages load goals, platforms, and goal schemas and create an owned campaign.
4. `/dashboard/content/create/` renders, sends a mocked chat message, and persists session/content/message state.
5. Current image/history path mismatches are captured as known baseline failures, not silently accepted routes.
6. Content list and campaign-content pages record their current missing API requests and fallback behavior.
7. `/dashboard/telegram/channels/` renders; mocked verification creates an owned verified channel.
8. Mocked Telegram publishing writes a log and publication fields; foreign content/channel IDs are denied except for the documented multi-publish defect.
9. Compatibility dashboard aliases render their documented current templates.
10. Messaging pages record current API 404s; page HTTP 200 alone is not treated as success.

Provider calls must be mocked. The run must fail on an unlisted same-origin 404, browser console exception, secret in captured output, or cross-user data disclosure.
