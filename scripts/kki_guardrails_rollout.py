#!/usr/bin/env python3
"""
KKI Guardrails Rollout
=======================
Rollt den KKI Multi-Agent-Workflow-Standard (README-Hinweis + AGENTS.md +
AGENT_LOG.md) additiv ueber alle Repos von KKEEY92 aus.

Carsten-Regeln (hart):
- READ-FIRST: Jede Datei wird vor dem Schreiben gelesen/geprueft.
- Nur additiv: Bestehende AGENTS.md-Dateien werden NIE ueberschrieben.
- Kein Force-Push, kein Force-Delete, keine Loeschungen.
- Idempotent: Wiederholte Laeufe aendern nichts, wenn der Standard schon
  vorhanden ist (Text-Marker-Check).
- Nur Repos von KKEEY92 selbst (kein Fork, kein Archiv).

Benoetigt: Umgebungsvariable GH_TOKEN (Fine-grained PAT mit
Contents: Read & Write auf alle Ziel-Repos, oder ein classic PAT mit
`repo`-Scope). Wird als GitHub Actions Secret bereitgestellt.
Ohne Token: Warning, Exit 0 — kein roter Scheduled-Run.
"""

import base64
import json
import os
import sys
import time
from pathlib import Path

import requests

API = "https://api.github.com"
OWNER = "KKEEY92"
MARKER = "KKI Multi-Agent-Workflow"

TOKEN = (os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN") or "").strip()


def write_summary(lines):
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        Path(summary_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


if not TOKEN:
    msg = (
        "WARNUNG: Weder GH_TOKEN noch GITHUB_TOKEN gesetzt. "
        "Rollout uebersprungen. Secret KKI_GUARDRAILS_TOKEN in "
        "kev-dev-command-center hinterlegen."
    )
    print(msg, file=sys.stderr)
    write_summary(
        [
            "# KKI Guardrails Rollout -- uebersprungen",
            "",
            "Secret `KKI_GUARDRAILS_TOKEN` fehlt. Job bewusst gruen, "
            "damit der Montagslauf die Inbox nicht zumuellt.",
            "",
            "Setup: GitHub Settings → Tokens (fine-grained) → Contents R/W "
            "auf alle Repos → als Repo-Secret `KKI_GUARDRAILS_TOKEN` speichern.",
        ]
    )
    sys.exit(0)

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

# Repos, die NIE automatisch angefasst werden sollen (z.B. aktive
# Jules-Sessions, Forks, oder Repos mit Sonderregeln). Kann jederzeit
# erweitert werden.
SKIP_REPOS = {
    "LiveKIT_Agents",  # Fork von livekit/agents -- fremdes Upstream-Repo
}

AGENTS_MD_TEMPLATE = """# AGENTS.md -- KKI-Standard fuer AI-Coding-Tools

Dieses Dokument gilt fuer alle KI-Coding-Agenten, die an diesem Repository arbeiten: Claude/Cowork, GitHub Copilot, Google Jules, Gemini/Antigravity.

## Harte Regeln (nicht verhandelbar)

1. **ZERO DESTRUCTION**: Keine Dateien oder Ordner loeschen (kein `rm`, `rmdir`), ausser bei explizitem, isoliertem Befehl von Kevin Kuck.
2. **DRY-RUN FIRST**: Destruktive oder weitreichende Skript-Aenderungen zuerst als Dry-Run/Plan zeigen, bevor sie ausgefuehrt werden.
3. **READ-FIRST**: Vor jeder Aenderung bestehenden Code lesen und verstehen, keine Annahmen ueber Struktur treffen.
4. **BRANCH STATT UMBAU**: Groessere Umbauten ueber einen eigenen Branch, nicht direkt auf den Default-Branch, ausser bei kleinen additiven Fixes (README, Docs).

## Format fuer mehrstufige Plaene

<Role> Praezise Rolle des Agenten </Role>
<Context> Systemumgebung und Zielsetzung </Context>
<Constraints> Harte Regeln fuer diesen Task </Constraints>
<Execution_Steps> Schritt-fuer-Schritt Logik </Execution_Steps>

## Branch-Namenskonvention

`agent/<tool>/<feature>`, kein direkter Push auf den Default-Branch bei groesseren Aenderungen.

## PR-Pflicht

Groessere Aenderungen ueber Pull Request gegen den Default-Branch, Merge nur durch Kevin Kuck.

## Logging

Alle Agenten-Aenderungen werden in AGENT_LOG.md nachvollziehbar dokumentiert.

## Herkunft

Diese Datei wurde automatisch durch den KKI Guardrails Rollout Workflow
(`kki-guardrails-rollout.yml` in kev-dev-command-center) angelegt.
"""

AGENT_LOG_MD_TEMPLATE = """# AGENT_LOG.md -- Nachvollziehbares Log aller AI-Agent-Aenderungen

Append-only. Format: Datum | Tool | Kurzbeschreibung | PR-Link

---

{date} | KKI Guardrails Workflow (Actions) | AGENTS.md + AGENT_LOG.md automatisch angelegt (additiv, direkt auf Default-Branch, keine bestehende Funktionalitaet veraendert). | -
"""

README_BLOCKQUOTE = (
    "\n\n> KKI Multi-Agent-Workflow: Dieses Repo wird nach dem gemeinsamen "
    "AGENTS.md-Standard von mehreren KI-Coding-Agenten (Claude, Copilot, "
    "Jules) additiv weiterentwickelt, mit Nachvollziehbarkeit in "
    "AGENT_LOG.md."
)


def gh_get(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params, timeout=30)
    if r.status_code == 403 and "rate limit" in r.text.lower():
        reset = int(r.headers.get("X-RateLimit-Reset", time.time() + 60))
        wait = max(reset - time.time(), 1)
        print(f"Rate limit erreicht, warte {wait:.0f}s ...")
        time.sleep(wait)
        return gh_get(url, params)
    return r


def gh_put(url, payload):
    r = requests.put(url, headers=HEADERS, data=json.dumps(payload), timeout=30)
    return r


def list_repos():
    repos = []
    page = 1
    while True:
        r = gh_get(
            f"{API}/user/repos",
            params={
                "affiliation": "owner",
                "per_page": 100,
                "page": page,
                "sort": "full_name",
            },
        )
        if r.status_code != 200:
            print(f"FEHLER beim Repo-Listing: {r.status_code} {r.text}", file=sys.stderr)
            sys.exit(1)
        batch = r.json()
        if not batch:
            break
        repos.extend(batch)
        page += 1
    return [
        repo
        for repo in repos
        if repo["owner"]["login"] == OWNER
        and not repo.get("archived", False)
        and not repo.get("fork", False)
        and repo["name"] not in SKIP_REPOS
    ]


def get_file(repo_name, path, branch):
    r = gh_get(f"{API}/repos/{OWNER}/{repo_name}/contents/{path}", params={"ref": branch})
    if r.status_code == 200:
        data = r.json()
        content = base64.b64decode(data["content"]).decode("utf-8", errors="replace")
        return content, data["sha"]
    return None, None


def put_file(repo_name, path, branch, content, sha, message):
    payload = {
        "message": message,
        "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        "branch": branch,
    }
    if sha:
        payload["sha"] = sha
    r = gh_put(f"{API}/repos/{OWNER}/{repo_name}/contents/{path}", payload)
    return r


def process_repo(repo):
    name = repo["name"]
    branch = repo["default_branch"]
    actions_taken = []

    # --- README.md: KKI-Hinweis ergaenzen (nur wenn noch nicht vorhanden) ---
    readme_content, readme_sha = get_file(name, "README.md", branch)
    if readme_content is None:
        # Kein README vorhanden -> minimalen Hinweis anlegen, keine
        # erfundenen Projektbeschreibungen.
        new_content = f"# {name}\n{README_BLOCKQUOTE}\n"
        r = put_file(name, "README.md", branch, new_content, None,
                      "Add KKI multi-agent-workflow note (README created)")
        if r.status_code in (200, 201):
            actions_taken.append("README.md neu angelegt")
        else:
            actions_taken.append(f"README.md FEHLER ({r.status_code})")
    elif MARKER not in readme_content:
        lines = readme_content.splitlines()
        if lines:
            # Direkt nach der ersten Zeile (i.d.R. Titel/H1) einfuegen --
            # sichere, generische Heuristik, die bestehendes Layout nicht
            # zerstoert.
            new_lines = [lines[0], README_BLOCKQUOTE.strip("\n")] + lines[1:]
            new_content = "\n".join(new_lines) + "\n"
        else:
            new_content = README_BLOCKQUOTE.strip("\n") + "\n"
        r = put_file(name, "README.md", branch, new_content, readme_sha,
                      "Add KKI multi-agent-workflow note to README")
        if r.status_code in (200, 201):
            actions_taken.append("README.md ergaenzt")
        else:
            actions_taken.append(f"README.md FEHLER ({r.status_code})")
    else:
        actions_taken.append("README.md bereits aktuell")

    # --- AGENTS.md: nur anlegen, NIE ueberschreiben ---
    agents_content, _ = get_file(name, "AGENTS.md", branch)
    if agents_content is None:
        r = put_file(name, "AGENTS.md", branch, AGENTS_MD_TEMPLATE, None,
                      "Add KKI AGENTS.md guardrails standard")
        if r.status_code in (200, 201):
            actions_taken.append("AGENTS.md neu angelegt")
        else:
            actions_taken.append(f"AGENTS.md FEHLER ({r.status_code})")
    else:
        actions_taken.append("AGENTS.md bereits vorhanden (unangetastet)")

    # --- AGENT_LOG.md: nur anlegen, NIE ueberschreiben (Append passiert
    # durch die Agenten selbst, nicht durch diesen Workflow) ---
    log_content, _ = get_file(name, "AGENT_LOG.md", branch)
    if log_content is None:
        today = time.strftime("%Y-%m-%d")
        r = put_file(name, "AGENT_LOG.md", branch,
                      AGENT_LOG_MD_TEMPLATE.format(date=today), None,
                      "Add AGENT_LOG.md for KKI guardrails tracking")
        if r.status_code in (200, 201):
            actions_taken.append("AGENT_LOG.md neu angelegt")
        else:
            actions_taken.append(f"AGENT_LOG.md FEHLER ({r.status_code})")
    else:
        actions_taken.append("AGENT_LOG.md bereits vorhanden (unangetastet)")

    return actions_taken


def main():
    repos = list_repos()
    print(f"{len(repos)} Repos gefunden (nach Filter: kein Fork, kein Archiv, nicht in SKIP_REPOS).\n")

    summary_lines = ["# KKI Guardrails Rollout -- Ergebnis\n"]
    summary_lines.append(f"Lauf: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}\n")
    summary_lines.append(f"Repos geprueft: {len(repos)}\n")
    summary_lines.append("| Repo | Aktionen |")
    summary_lines.append("|------|----------|")

    for repo in repos:
        name = repo["name"]
        print(f"--- {name} ---")
        try:
            actions = process_repo(repo)
        except Exception as exc:  # noqa: BLE001 -- ein Repo-Fehler darf den Lauf nicht stoppen
            actions = [f"UNERWARTETER FEHLER: {exc}"]
        for a in actions:
            print(f"  - {a}")
        summary_lines.append(f"| {name} | {'; '.join(actions)} |")
        time.sleep(0.5)  # sanft mit der Rate-Limit umgehen

    write_summary(summary_lines)
    print("\nFertig.")


if __name__ == "__main__":
    main()
