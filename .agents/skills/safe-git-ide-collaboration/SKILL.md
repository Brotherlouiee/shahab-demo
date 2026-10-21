---
name: safe-git-ide-collaboration
description: Safely coordinate code changes between a user's local IDE, Git branches, GitHub pull requests, and Codex. Use whenever the user wants Codex to review, implement, or continue a change that they are developing locally, asks about pulling/pushing/branching/merging, or needs a safe handoff of frontend or backend work.
---

# همکاری ایمن Git و IDE

## Overview

Prevent lost work, accidental overwrites, mixed changes, secret leaks, and ambiguous ownership while a user and Codex collaborate on one codebase.

## Determine the work mode first

Ask or infer exactly one of these modes before suggesting a mutation:

1. **User-owned branch / review only:** Inspect, explain, and propose precise edits; do not modify or push the user's branch.
2. **Codex-owned branch / implementation:** Create or use a branch explicitly handed to Codex; implement, test, commit, and push the agreed changes.
3. **Shared branch / turn-taking:** Allow only one editor at a time. Before either party continues, require a clean working tree and pull the other party's pushed commits.

If ownership is not stated, default to review only and ask one short question. Never silently edit a branch that the user may still be changing.

## Branch and scope rules

1. Start each independent concern on a descriptive branch from the current `main`, for example `feat/ui-results-polish` or `fix/recommendation-empty-state`.
2. Keep one coherent concern per branch and Pull Request. Do not mix UI polish, recommendation logic, deployment, data migrations, or unrelated cleanup.
3. Never work directly on `main` except to update it and create a new branch.
4. Before creating a branch, update local `main` with `git pull origin main` and confirm it is clean.
5. Before switching branches, committing, pulling, rebasing, or merging, inspect `git status`.
6. Do not use destructive recovery commands such as `git reset --hard`, forced push, or discarding files unless the user explicitly authorizes the exact target and impact.

## Safe local workflow

Give commands one at a time, in Persian, with real branch and file names when known. Explain each command in a single plain-language sentence.

For a clean local repository:

```bash
git switch main
git pull origin main
git switch -c feat/<short-change-name>
```

During implementation, run the relevant local test or development command. Before a commit, inspect both the file list and content:

```bash
git status
git diff
```

Stage only intended files, then make a focused commit and publish the branch:

```bash
git add path/to/changed-file
git commit -m "feat(ui): describe the focused change"
git push -u origin feat/<short-change-name>
```

Open a Pull Request from that branch to `main`. State the change, tests run, visible verification (including screenshots for UI changes), risks, and anything deliberately out of scope.

## Shared-branch handoff

Before the user continues after Codex pushes work, require:

```bash
git status
git pull origin <current-branch>
```

Proceed only if `git status` is clean. If it is not clean, do not guess: have the user either commit their intentional work or show the status/diff before deciding. If `pull` reports a conflict, stop and explain that both sides changed overlapping lines; resolve with the user rather than overwriting either version.

## Pull Requests, review, and merge

Treat a branch and its Pull Request as the unit of review. Check tests, diffs, UI evidence, documentation, and scope before recommending merge. Never call CI success a deployed or end-to-end verified result; report deployment and real-URL testing separately.

After merge, update the local main branch before starting a different task:

```bash
git switch main
git pull origin main
```

## Security and recovery

- Never commit `.env`, credentials, private keys, database URLs, access tokens, or production exports. Use ignored local environment files and deployment secret settings.
- Never transfer a project by ZIP or pasting whole files into chat when Git is available. Transfer changes through the branch and Pull Request.
- Treat untracked files and unexpected diff entries as suspicious until explained.
- If the user has edits in an old non-Git folder, do not copy them into a fresh clone wholesale. First compare them file-by-file against the current branch and migrate only the intentional changes into a dedicated branch.
- If the repository is not connected yet, first verify `git --version`, clone the repository, sign in to GitHub in the IDE, and verify `git remote -v`, `git branch --show-current`, and `git status`.
