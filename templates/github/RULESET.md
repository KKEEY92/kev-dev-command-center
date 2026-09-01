# Ruleset — manuell in der UI

Kein API-Zugriff aus diesem Agent-Kontext. Vorlage zum Abtippen:

Name: `kki-main-evaluate`
Enforcement: **Evaluate** (nicht Active)
Target: default branch

Bypass:
- Role: Repository admin — Always allow
- Actor: `KKEEY92` — Always allow

Rules, die Evaluate sichtbar machen darf:
- Restrict updates that create files matching `.env` (wenn die UI das hergibt)
- Require workflows to pass: `Gitleaks` (erst wenn der Check auf main existiert)

Nicht setzen in Phase 1:
- Require a pull request before merging
- Require signed commits
- Block force pushes nur dann, wenn du selbst nie rebasest

Phase 3 (Active) erst nach zwei ruhigen Evaluate-Wochen auf dem Pilot.
