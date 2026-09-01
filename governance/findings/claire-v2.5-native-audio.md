# Findings — claire-v2.5-native-audio

Ref: `main` @ `146b6f9`  
Sichtbarkeit: **public**  
Rolle: Gemini Native Audio Agent + LiveKit + Dashboard

## C-01 LiveKit-Token ohne Auth — Critical

`backend/token_server.py`

- `GET /token?room=&identity=` stellt JWT mit `room_join` + publish/subscribe aus.
- Kein Shared Secret, keine Session.
- `app.run(host="0.0.0.0", port=3001)`.
- Keys aus Env (`LIVEKIT_API_KEY` / `SECRET`) — gut. Bindung + fehlende Auth — schlecht, sobald der Port nicht nur loopback ist.

Lokal auf dem Mac hinter der Firewall akzeptabel. Cloud Run / Port-Forward / LAN = jeder holt sich ein Token.

## C-02 Dashboard ohne Auth — Critical

`backend/dashboard.py` (FastAPI), u. a.:

- GET/POST `/api/config`, `/api/memory*`, `/api/obsidian/file` (Read+Write, Path-Prefix-Check vorhanden)
- POST `/api/context/sync` — Gemini schreibt Memory + Vault
- WS `/ws` — Gemini LiveConnect, PCM ohne Quota
- POST `/api/autofix`, `/api/audio/test-gemini`

Keine `Depends`/`Security`. Keys nur als Env (`GOOGLE_API_KEY` / `GEMINI_API_KEY`, `ELEVENLABS_API_KEY`).

Path-Check gegen Vault-Root ist da, ersetzt aber keine Auth.

## C-03 Kosten / Quota — High

`/ws` und `/api/context/sync` / `/api/audio/test-gemini` ohne Rate-Limit, Concurrency-Limit, Payload-Limit. Ein offener Port = offene Gemini-Rechnung.

## C-04 log_server — High

`backend/log_server.py`: SSE `/logs` streamt `docker compose logs`. `host=0.0.0.0`, CORS `*`. Kein Auth. Leak von Runtime-Logs (potenziell Env-Fehlertexte).

## C-05 Governance — Medium

- Kein `.github/`-Governance-Satz.
- Dependabot-Alerts-API: disabled.
- Code-Suche nach `AIza` leer — kein Beweis für „keine historischen Leaks“.

## Nicht in diesem PR

Keine Code-Änderung an claire. Eigener PR nach GO, sonst zerlegt man Voice-Dev.
