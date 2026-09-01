# KKI Governance-Standard (Solo-Maintainer)

Stand: 2026-09-01  
Gilt verbindlich für neue Repos und den Pilot. Legacy (56 Repos) nur stufenweise.

## Harte Regeln (ohne Self-Lockout)

- Secrets nie im Repo (auch nicht „nur lokal“ committed).
- `.env` steht in `.gitignore`. Nur `.env.example` ohne echte Werte.
- AI-/Token-Endpunkte brauchen Auth, sobald sie nicht exklusiv `127.0.0.1` sind.
- GitHub Actions möglichst SHA-gepinnt. Tags (`@v4`) sind Tech-Debt, kein Blocker am Tag 1.
- `SECURITY.md` und `CODEOWNERS` existieren.
- Dependabot ist an.
- Secret Scanning + Push Protection: in der GitHub-UI aktivieren, sobald der Plan es hergibt.
- Gitleaks läuft auf Push/PR. Fund = Fix oder dokumentiertes False-Positive.

## Weiche Regeln (Evaluate, nicht Active)

- Rulesets zuerst **Evaluate**, Owner in Bypass-Liste (**Always allow**).
- Required Reviews: **optional** solange Solo.
- Signed Commits: **optional** (Agenten signieren nicht).
- Direct Push auf `main`: erlaubt mit Admin-Bypass. Bevorzugt PR, kein Zwang.
- npm/Trivy/CodeQL-Critical: Bericht, kein Push-Block auf Legacy.

## Ruleset-Rollout

```
Phase 1  Evaluate + Monitoring + Owner Bypass. Keine Agent-Blocks.
Phase 2  Findings und False-Positives säubern. Workflows stabil.
Phase 3  Nur alltagstaugliche Guards auf Active. Bypass bleibt solange Solo.
```

## Pilot-Reihenfolge

1. `kev-dev-command-center` — Template
2. `claire-v2.5-native-audio` — AI/Token-Risiko
3. `CV_KKEEY` — öffentliche Surface

Danach erst AuraTone / claire-v2. Nie 56 Repos auf einmal.

## Agent-Vertrag

Kein Agent pusht nach `main` wenn der Diff enthält:

- hardcoded API-Keys, JWT-Secrets, Private Keys
- LiveKit/Gemini/Supabase-Service-Secrets im Klartext
- `.env` mit Werten

Fehlende Branch Protection ist **kein** Push-Blocker. Fehlende Secrets-Hygiene schon.
