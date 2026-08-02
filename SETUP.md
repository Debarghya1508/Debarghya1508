# Setup

This turns into your live GitHub profile page the moment it lives in a repo
named **exactly** your username.

## 1. Create the special repo
Go to https://github.com/new and create a **public** repo named:

```
Debarghya1508
```

(same spelling/case as your username `Debarghya1508`). GitHub auto-detects
this repo and shows its `README.md` on your profile page.

## 2. Push these files
From this folder:

```bash
cd repo
git init
git add .
git commit -m "init: self-typing ascii portrait + live stats"
git branch -M main
git remote add origin https://github.com/Debarghya1508/Debarghya1508.git
git push -u origin main
```

## 3. Let the Action run once
No secrets to add — the workflow uses the `GITHUB_TOKEN` that Actions
provides automatically. After the push:

- Go to the **Actions** tab of the new repo
- You'll see "Update profile stats" running (triggered by the push)
- It finishes in under a minute and commits `assets/stats.svg` with your
  real numbers

If it doesn't fire automatically, click **Run workflow** on the
"Update profile stats" workflow to trigger it manually.

## 4. Check repo Action permissions (only if the commit step fails)
Settings → Actions → General → Workflow permissions → select
**"Read and write permissions"**, then save. This is usually on by default
for new repos.

## Updating the portrait later
Swap in a new photo and regenerate:

```bash
python3 scripts/make_portrait.py path/to/new-photo.jpg assets/ascii.svg
git add assets/ascii.svg
git commit -m "update portrait"
git push
```

Tune `COLS`, `RAMP`, `ROW_DELAY`, or `TYPE_DUR` at the top of
`scripts/make_portrait.py` to change resolution, contrast, or typing speed.

## What updates on its own
`scripts/update_stats.py` runs daily via `.github/workflows/update.yml`,
pulls fresh numbers from the GitHub GraphQL API (contributions, commits,
PRs, issues, stars, followers), and only commits `assets/stats.svg` when
something actually changed.
