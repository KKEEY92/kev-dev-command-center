import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const GITHUB_TOKEN = Deno.env.get("GITHUB_TOKEN")!;
const GITHUB_OWNER = Deno.env.get("GITHUB_OWNER")!;
const SUPABASE_URL = Deno.env.get("SUPABASE_URL")!;
const SUPABASE_SERVICE_ROLE_KEY = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

const supabase = createClient(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY);

async function ghFetch(path: string) {
  const res = await fetch(`https://api.github.com${path}`, {
    headers: {
      Authorization: `Bearer ${GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
    },
  });
  if (!res.ok) {
    throw new Error(`GitHub API ${path} -> ${res.status} ${await res.text()}`);
  }
  return res.json();
}

async function listRepos(): Promise<string[]> {
  const repos: string[] = [];
  let page = 1;
  while (true) {
    const batch = await ghFetch(
      `/users/${GITHUB_OWNER}/repos?per_page=100&page=${page}&type=owner`
    );
    if (!Array.isArray(batch) || batch.length === 0) break;
    repos.push(...batch.map((r: any) => r.name));
    if (batch.length < 100) break;
    page++;
  }
  return repos;
}

async function listOpenPRs(repo: string) {
  return ghFetch(`/repos/${GITHUB_OWNER}/${repo}/pulls?state=open&per_page=100`);
}

Deno.serve(async () => {
  const started = Date.now();
  const summary = { reposScanned: 0, prsSeen: 0, changes: 0, errors: [] as string[] };

  try {
    const repos = await listRepos();
    summary.reposScanned = repos.length;

    const { data: existing, error: existingErr } = await supabase
      .from("pr_snapshot")
      .select("repo_name,pr_number,title,state,draft,updated_at");
    if (existingErr) throw existingErr;

    const existingMap = new Map(
      (existing || []).map((row) => [`${row.repo_name}#${row.pr_number}`, row])
    );
    const seenKeys = new Set<string>();

    for (const repo of repos) {
      let prs: any[] = [];
      try {
        prs = await listOpenPRs(repo);
      } catch (e) {
        summary.errors.push(`${repo}: ${e.message}`);
        continue;
      }
      summary.prsSeen += prs.length;

      for (const pr of prs) {
        const key = `${repo}#${pr.number}`;
        seenKeys.add(key);
        const prev = existingMap.get(key);

        const { error: upsertErr } = await supabase.from("pr_snapshot").upsert(
          {
            repo_name: repo,
            pr_number: pr.number,
            title: pr.title,
            url: pr.html_url,
            state: pr.merged_at ? "merged" : pr.state,
            draft: !!pr.draft,
            author: pr.user?.login ?? null,
            created_at: pr.created_at,
            updated_at: pr.updated_at,
            last_seen_at: new Date().toISOString(),
          },
          { onConflict: "repo_name,pr_number" }
        );
        if (upsertErr) summary.errors.push(`upsert ${key}: ${upsertErr.message}`);

        if (!prev) {
          summary.changes++;
          await supabase.from("activity_log").insert({
            repo_name: repo,
            entity_type: "pull_request",
            entity_number: pr.number,
            action: "opened",
            actor: pr.user?.login ?? null,
            title: pr.title,
            url: pr.html_url,
            detail: { draft: pr.draft, base: pr.base?.ref, head: pr.head?.ref },
          });
        } else if (prev.updated_at !== pr.updated_at) {
          summary.changes++;
          await supabase.from("activity_log").insert({
            repo_name: repo,
            entity_type: "pull_request",
            entity_number: pr.number,
            action: "updated",
            actor: pr.user?.login ?? null,
            title: pr.title,
            url: pr.html_url,
            detail: { previous_title: prev.title, previous_state: prev.state },
          });
        }
      }
    }

    for (const [key, row] of existingMap) {
      if (seenKeys.has(key)) continue;
      let mergedInfo: any = null;
      try {
        mergedInfo = await ghFetch(`/repos/${GITHUB_OWNER}/${row.repo_name}/pulls/${row.pr_number}`);
      } catch (_e) {
        // Repo/PR evtl. geloescht - ueberspringen
      }
      const action = mergedInfo?.merged_at ? "merged" : "closed";
      summary.changes++;
      await supabase.from("activity_log").insert({
        repo_name: row.repo_name,
        entity_type: "pull_request",
        entity_number: row.pr_number,
        action,
        actor: mergedInfo?.merged_by?.login ?? null,
        title: row.title,
        url: mergedInfo?.html_url ?? null,
        detail: {},
      });
      await supabase
        .from("pr_snapshot")
        .delete()
        .eq("repo_name", row.repo_name)
        .eq("pr_number", row.pr_number);
    }
  } catch (e) {
    summary.errors.push(e.message ?? String(e));
  }

  return new Response(
    JSON.stringify({ ...summary, durationMs: Date.now() - started }),
    { headers: { "Content-Type": "application/json" } }
  );
});
