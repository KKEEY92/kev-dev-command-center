# Risk Assessment — Pilot 2026-09-01

Methode: Code-Review über GitHub-API + Dateilesen. Kein dynamischer Scan, kein GHAS-Vollbild. SharePoint-Assessments waren nicht lesbar; dieses Dokument ersetzt sie für den Pilot.

## Risiko-Matrix

| ID | Repo | Finding | Schwere | Reachability |
|---|---|---|---|---|
| C-01 | claire-v2.5 | LiveKit-Token ohne Auth, Bind `0.0.0.0:3001` | Critical | Hoch, sobald Port/Cloud erreichbar |
| C-02 | claire-v2.5 | Dashboard-API ohne Auth (Memory, Obsidian R/W, Gemini WS) | Critical | Hoch bei exponiertem Host |
| C-03 | claire-v2.5 | `/api/context/sync` + `/ws` ohne Quota/Rate-Limit | High | Kosten + DoS |
| C-04 | claire-v2.5 | `log_server` SSE + `docker compose logs` auf `0.0.0.0` | High | Info-Leak |
| C-05 | claire-v2.5 | Keine `.github`-Governance, Dependabot disabled | Medium | Prozess |
| K-01 | command-center | Actions nur tag-gepinnt (`@v4`/`@v5`) | Medium | Supply Chain |
| K-02 | command-center | Keine SECURITY.md / CODEOWNERS / Dependabot / Gitleaks | Medium | Prozess |
| K-03 | command-center | Guardrails-Rollout braucht PAT; Secret oft leer | Low | Ops |
| V-01 | CV_KKEEY | Actions tag-gepinnt, Push auf `main` aus Workflow | Medium | Supply Chain / Bot-Push |
| V-02 | CV_KKEEY | Keine SECURITY.md / CODEOWNERS / Secret-Scan | Low | Prozess |
| V-03 | CV_KKEEY | Statische Pages, keine Server-AI-Endpunkte | Info | Gering |

## Was nicht belegt ist

- Kein öffentlicher `AIza…`-Treffer in der Code-Suche (Index kann lücken).
- Secret-Scanning-API auf claire: keine offenen Alerts sichtbar.
- Dependabot-Alerts claire: Feature disabled, kein Aussagewert.
- Branch Protection / Push Protection: nur in der UI prüfbar.

## Größter Hebel (nicht Branch-Regeln)

1. Token-Server und Dashboard nicht ohne Auth an ein nicht-lokales Interface binden.
2. Gemini-Calls hinter Auth + Quota.
3. Actions SHA-pinnen, beginnend bei neuen Workflows.
4. Echte Keys rotieren, falls sie je in Issues/Logs/Cloud-Run standen.
