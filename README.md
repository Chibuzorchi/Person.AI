# Person.ai QA Engineering — Test Strategy, Artifacts, and Answers

## Repository Index (answers per question)
- Question 1 — Slack Integration Mock/Sandbox: `question-1-slack-integration-mock.md`
- Question 2 — QuickBooks & Salesforce Test Data Seeding: `question-2-test-data-seeding.md`
- Question 3 — End-to-End Brief Generation Test: `question-3-end-to-end-testing.md`
- Question 4 — Health, Metrics, and Audit Verification: `question-4-health-metrics-audit.md`
- Question 5 — Bubble Front-end Testing Strategy: `question-5-bubble-frontend-testing.md`

## What’s implemented (aligned with Person.ai’s stack)
- Slack integration is tested end-to-end against a safe mock that simulates real Slack behavior (messages, OAuth expiry, rate limits, webhooks, and events) so we never hit production.
- QuickBooks and Salesforce have realistic, relationship‑preserving fake datasets (customers, invoices with line items, accounts, contacts, opportunities) generated via factories and seeded into a mock API/DB for deterministic regression.
- Daily brief E2E covers Gmail → Content Engine → Media Engine (audio) → Delivery Gateway (Slack/Email/SMS) with assertions for both text and audio delivery and CI artifacts for evidence.
- Monitoring suite validates `/health`, `/metrics` (Prometheus counters/gauges/histograms), and `/audit` (who/what/when), with automated checks wired for CI gates.
- Bubble front‑end workflows are automated as black‑box tests (Playwright/Cypress style selectors), with API validation and visual regression to catch UI drift.

## How (high‑level approach)
1) Slack (no real API): stub endpoints, simulate OAuth expiry and rate limits, replay events; verify UI → API → mock Slack flow.
2) Data seeding: generate lifelike QuickBooks/Salesforce data with Faker; preserve relationships; version datasets for stable regressions.
3) Daily brief E2E: mock Gmail, verify narrative output, validate audio generation, confirm Slack delivery (text + audio).
4) Observability: assert ready `/health`, validate Prometheus metrics, and confirm complete `/audit` trails; run frequently in CI.
5) Bubble UI: automate critical journeys with stable selectors and add visual baselines to prevent regressions.

## Where to look
- Each markdown file above contains runnable examples, mock server setups, and CI workflows tailored to Person.ai’s integration surface.
- Use these as drop‑in blueprints for staging environments and CI pipelines.

## How to demo quickly
- Slack mock: run the mock and tests in `question-1-slack-integration-mock.md`.
- Data seeding: execute the seeder and mocks in `question-2-test-data-seeding.md`.
- E2E brief: follow `question-3-end-to-end-testing.md` to run the full pipeline test.
- Observability: run checks from `question-4-health-metrics-audit.md`.
- Bubble flows: run UI/visual tests per `question-5-bubble-frontend-testing.md`.
