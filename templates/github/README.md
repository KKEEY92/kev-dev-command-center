# Template — auf jedes neue KKI-Repo kopieren

Quelle der Wahrheit: dieses Verzeichnis plus `governance/STANDARD.md`.

Kopieren nach `.github/` des Zielrepos:

- `CODEOWNERS`
- `pull_request_template.md`
- `dependabot.yml`
- `workflows/gitleaks.yml`
- `workflows/action-pin-check.yml`

Zusätzlich Repo-Root: `SECURITY.md`.

Danach in der GitHub-UI (kein Agent):

1. Settings → Code security → Dependabot alerts an
2. Secret scanning + Push protection an, falls sichtbar
3. Ruleset anlegen: **Evaluate**, Bypass = `KKEEY92` always-allow
4. Nicht aktivieren: Required Reviews, Signed Commits

CodeQL nur auf **public** Repos zuverlässig kostenlos.
