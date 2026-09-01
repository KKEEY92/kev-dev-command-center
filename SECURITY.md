# Security Policy

## Melden

Verdacht auf Leak oder aktive Schwachstelle: direkt an Kevin Kuck (`KKEEY92`), nicht als öffentliches Issue mit Klartext-Secret.

Rotierte Credentials nie in Tickets pasten.

## Was dieses Repo schützt

- Governance-Template und Rollout-Scripts
- Keine Produktions-AI-Endpunkte

Secrets liegen in GitHub Actions Secrets, nicht im Tree.

## Mindeststandard (KKI Solo)

Dokumentiert in [`governance/STANDARD.md`](governance/STANDARD.md).

Kurz:

- Gitleaks auf Push/PR
- Dependabot an
- Secret Scanning + Push Protection in der UI, wenn verfügbar
- Rulesets zuerst Evaluate, Owner Bypass always-allow
- Required Reviews und Signed Commits bleiben optional

## Agenten

Agent-Pushes sind erlaubt. Verboten ist das Committen von Keys, `.env`-Werten, PEM/JWT-Secrets.
