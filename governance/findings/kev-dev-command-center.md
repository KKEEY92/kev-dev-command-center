# Findings — kev-dev-command-center

Ref: `main` @ `a5b1585`  
Sichtbarkeit: public  
Rolle: Governance-Hub, Pages-Dashboard, Guardrails-Rollout

## Secrets

- Keine Keys im sichtbaren Tree gefunden.
- `supabase-schema.sql` ist Schema, kein Service-Key.
- Rollout erwartet Secret `KKI_GUARDRAILS_TOKEN` (PAT). Fehlt das Secret, Job soft-fail — korrekt.

## Auth / AI-Endpunkte

- Keine Laufzeit-API in diesem Repo. Risiko = Workflows + Token-Scope des PAT.

## Supply Chain

- `.github/workflows/pages.yml`: `actions/checkout@v4`, `upload-pages-artifact@v3`, `deploy-pages@v4` — Tags, keine SHAs.
- `.github/workflows/kki-guardrails-rollout.yml`: `checkout@v4`, `setup-python@v5` — Tags.

## Governance vor diesem PR

- Kein `SECURITY.md`, kein `CODEOWNERS`, kein Dependabot, kein Gitleaks, kein CodeQL.
- Branch Protection / Secret Scanning: nicht per API verifizierbar.

## Bewertung

Medium. Gutes Template-Repo, aber selbst ohne Baseline. Dieser PR schließt die Dateilücke. UI-Schalter bleiben bei Kevin.
