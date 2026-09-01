# Findings — CV_KKEEY

Ref: `main` @ `e41c841`  
Sichtbarkeit: public (GitHub Pages + CNAME)  
Rolle: öffentlicher Lebenslauf, kein Server-Backend

## Secrets / AI

- Keine Laufzeit-API, keine Gemini/LiveKit-Endpunkte.
- Risiko = Contents des statischen Trees + Workflow-Token.

## Supply Chain

- `pages.yml`: `checkout@v4`, `configure-pages@v5`, `deploy-pages@v4` — Tags.
- `sync-project-status.yml`: `checkout@v4`, `setup-python@v5`, danach **Bot-Push auf `main`** mit `contents: write`.
- Sync behandelt 404 auf private Repos inzwischen soft (Stand main). Gut.

Bot-Push auf `main` ist ok solange Solo und kein Required-Review. Wird gefährlich in dem Moment, in dem man Required Reviews aktiviert — genau deshalb bleiben die optional.

## Governance

- Kein SECURITY.md / CODEOWNERS / Dependabot / Gitleaks.

## Bewertung

Low–Medium. Öffentliche Surface, aber statisch. Baseline-Dateien nachziehen, Actions später pinnen. Kein Auth-Umbau nötig.
