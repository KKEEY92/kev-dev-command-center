# Fixliste — priorisiert

Status: offen, bis einzelnes Item per PR geschlossen wird. Kein Big-Bang.

## P0 — diese Woche, nur nach eigenem GO pro Repo

- [ ] claire: `token_server.py` nur auf `127.0.0.1` binden **oder** Shared-Secret / Session vor `/token`.
- [ ] claire: Dashboard-Mutationen (`/api/memory/*`, `/api/obsidian/file`, `/api/context/sync`, `/ws`) hinter Auth.
- [ ] claire: Rate-Limit + Payload-Limit auf `/ws` und `/api/audio/*`.
- [ ] Keys prüfen/rotieren, die je auf Cloud Run oder in Issues lagen (Gemini, LiveKit, ElevenLabs).

## P1 — Pilot-Repos

- [x] command-center: GOVERNANCE-Standard + SECURITY.md + CODEOWNERS + PR-Template + Dependabot.
- [x] command-center: Gitleaks + Action-Pin-Check (Pin-Check fail-open).
- [x] command-center: CodeQL-Workflow (public).
- [ ] GitHub-UI command-center: Secret Scanning, Push Protection, Dependabot alerts.
- [ ] GitHub-UI command-center: Ruleset **Evaluate**, Owner Bypass always-allow.
- [ ] claire + CV_KKEEY: dieselben Baseline-Dateien per eigener PRs kopieren (nicht in diesem PR).

## P2 — 30 Tage

- [ ] Bestehende Workflows auf Commit-SHA pinnen (`pages.yml`, `kki-guardrails-rollout.yml`, CV-Sync).
- [ ] claire: `log_server` nur localhost, CORS einschränken.
- [ ] AuraTone / claire-v2 Audit nach gleichem Raster.
- [ ] Template in `templates/github/` bei neuen Repos nutzen.

## P3 — nicht tun

- Required Reviews auf Solo-`main`.
- Signed-Commit-Pflicht für Agenten.
- Fail-closed npm/Trivy auf 56 Legacy-Repos.
- Rulesets sofort auf Active ohne Evaluate-Phase.
