#!/usr/bin/env python3
"""
update_stats.py
----------------
Pulls live stats straight from the GitHub GraphQL API and draws them into a
self-typing SVG terminal card. No third-party stats widget is used, so
nothing here can rate-limit or go dark - only GitHub's own API is called,
and it's called by a workflow that runs inside your own repo.

Env vars required:
    GH_TOKEN   - a token with at least public read access (the default
                 GITHUB_TOKEN provided to Actions is enough)
    GH_LOGIN   - your GitHub username
"""

import os
import sys
import datetime
import urllib.request
import json

FONT_SIZE = 13
CHAR_W = FONT_SIZE * 0.6
LINE_H = FONT_SIZE * 1.7
ROW_DELAY = 0.28
TYPE_DUR = 0.45

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    followers { totalCount }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes { stargazerCount }
    }
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { totalContributions }
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
    }
    createdAt
  }
}
"""


def gh_graphql(token: str, login: str) -> dict:
    now = datetime.datetime.utcnow()
    frm = now.replace(month=1, day=1, hour=0, minute=0, second=0)
    body = json.dumps({
        "query": QUERY,
        "variables": {
            "login": login,
            "from": frm.isoformat() + "Z",
            "to": now.isoformat() + "Z",
        },
    }).encode()

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": login,
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def build_lines(data: dict, login: str) -> list[str]:
    user = data["data"]["user"]
    followers = user["followers"]["totalCount"]
    repos = user["repositories"]
    total_repos = repos["totalCount"]
    total_stars = sum(r["stargazerCount"] for r in repos["nodes"])
    cc = user["contributionsCollection"]
    contribs_this_year = cc["contributionCalendar"]["totalContributions"]
    commits = cc["totalCommitContributions"]
    prs = cc["totalPullRequestContributions"]
    issues = cc["totalIssueContributions"]
    joined = user["createdAt"][:10]
    today = datetime.date.today().isoformat()

    return [
        f"guest@github:~$ whoami",
        f"{login}",
        f"guest@github:~$ stats --live",
        f"contributions ({datetime.date.today().year}) : {contribs_this_year}",
        f"commits this year          : {commits}",
        f"pull requests this year    : {prs}",
        f"issues opened this year    : {issues}",
        f"public repositories        : {total_repos}",
        f"total stars earned         : {total_stars}",
        f"followers                  : {followers}",
        f"member since               : {joined}",
        f"last synced                : {today}",
    ]


def escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_svg(lines: list[str]) -> str:
    max_len = max((len(l) for l in lines), default=0)
    width = round(max_len * CHAR_W) + 40
    height = round(len(lines) * LINE_H) + 30

    text_elems = []
    for i, line in enumerate(lines):
        y = 22 + i * LINE_H
        start = i * ROW_DELAY
        text_elems.append(
            f'''  <text x="16" y="{y:.1f}" class="row" opacity="0">{escape(line)}'''
            f'''<animate attributeName="opacity" from="0" to="1" '''
            f'''begin="{start:.3f}s" dur="{TYPE_DUR}s" fill="freeze" /></text>'''
        )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}"
     viewBox="0 0 {width} {height}"
     font-family="'JetBrains Mono','Cascadia Code','Fira Code',ui-monospace,'Courier New',monospace">
  <style>
    .bg {{ fill: #0d1117; stroke: #30363d; stroke-width: 1; }}
    .row {{ font-size: {FONT_SIZE}px; fill: #58a6ff; }}
    .row:nth-child(2) {{ fill: #7ee787; }}
  </style>
  <rect class="bg" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" rx="8" />
{chr(10).join(text_elems)}
</svg>
'''


def main():
    token = os.environ.get("GH_TOKEN")
    login = os.environ.get("GH_LOGIN")
    out_path = sys.argv[1] if len(sys.argv) > 1 else "assets/stats.svg"

    if not token or not login:
        print("GH_TOKEN and GH_LOGIN env vars are required", file=sys.stderr)
        sys.exit(1)

    data = gh_graphql(token, login)
    if "errors" in data:
        print(json.dumps(data["errors"], indent=2), file=sys.stderr)
        sys.exit(1)

    lines = build_lines(data, login)
    svg = build_svg(lines)
    with open(out_path, "w") as f:
        f.write(svg)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
