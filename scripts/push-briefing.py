#!/usr/bin/env python3
"""push-briefing.py - Push a briefing file to GitHub via the Contents API.

Setup (one-time):
  Save a fine-grained PAT (Contents: Read+Write on bwkim1025/study) to
  ./.github-token at the repo root. The file is gitignored.

Usage:
  python3 scripts/push-briefing.py briefings/2026-05-10-day2.md
  python3 scripts/push-briefing.py <path> "custom commit message"

Exit: 0 ok, 1 usage, 2 auth/HTTP error.
"""
import sys, os, base64, json, subprocess
import urllib.request, urllib.error

REPO = "bwkim1025/study"
TOKEN_FILE = ".github-token"
BRANCH = "main"


def load_token():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.abspath(os.path.join(here, ".."))
    p = os.path.join(repo_root, TOKEN_FILE)
    if not os.path.exists(p):
        sys.stderr.write("FAIL: no token at " + p + "\n")
        sys.stderr.write("      Save a GitHub PAT (Contents: R+W) to .github-token\n")
        sys.exit(2)
    with open(p, "r", encoding="ascii") as f:
        t = f.read().strip()
    if not t:
        sys.stderr.write("FAIL: token file is empty\n")
        sys.exit(2)
    return t


def http_json(method, url, headers, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    h = dict(headers)
    if body is not None:
        h["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    with urllib.request.urlopen(req) as resp:
        return json.load(resp)


def get_sha(url, headers):
    try:
        return http_json("GET", url, headers).get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def sync_local():
    """fetch + reset --hard, but only if no other tracked changes (safety)."""
    try:
        subprocess.run(["git", "fetch", "origin", BRANCH],
                       check=True, capture_output=True)
        u = subprocess.run(["git", "diff", "--quiet"], capture_output=True)
        s = subprocess.run(["git", "diff", "--cached", "--quiet"], capture_output=True)
        if u.returncode != 0 or s.returncode != 0:
            sys.stderr.write(
                "local: other tracked changes present - skipping reset.\n"
                "       Run: git fetch && git reset --hard origin/main\n")
            return
        subprocess.run(["git", "reset", "--hard", "origin/" + BRANCH],
                       check=True, capture_output=True)
        print("local: synced with origin/main")
    except Exception as e:
        msg = getattr(e, "stderr", None)
        msg = msg.decode("utf-8", "replace") if msg else str(e)
        sys.stderr.write("local: sync skipped (" + msg.strip()[:120] + ")\n")


def main():
    if len(sys.argv) < 2:
        sys.stderr.write("Usage: push-briefing.py <relative-path> [commit-message]\n")
        return 1
    rel = sys.argv[1].replace("\\", "/")
    if not os.path.exists(rel):
        sys.stderr.write("FAIL: file not found: " + rel + "\n")
        return 1
    if len(sys.argv) >= 3:
        msg = sys.argv[2]
    else:
        stem = os.path.splitext(os.path.basename(rel))[0]
        msg = "Study briefing " + stem

    token = load_token()
    with open(rel, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")

    url = "https://api.github.com/repos/" + REPO + "/contents/" + rel
    h = {
        "Authorization": "Bearer " + token,
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "study-briefing-push/1.0",
    }

    try:
        sha = get_sha(url, h)
    except urllib.error.HTTPError as e:
        sys.stderr.write("FAIL: lookup HTTP " + str(e.code) + " - "
                         + e.read().decode("utf-8", "replace")[:200] + "\n")
        return 2

    payload = {"message": msg, "content": b64, "branch": BRANCH}
    if sha:
        payload["sha"] = sha

    try:
        result = http_json("PUT", url, h, payload)
    except urllib.error.HTTPError as e:
        sys.stderr.write("FAIL: PUT HTTP " + str(e.code) + " - "
                         + e.read().decode("utf-8", "replace")[:300] + "\n")
        return 2

    csha = ((result.get("commit") or {}).get("sha") or "")[:7]
    action = "updated" if sha else "created"
    print("OK: " + action + " " + rel + " -> commit " + csha)
    print("    https://github.com/" + REPO + "/blob/" + BRANCH + "/" + rel)
    sync_local()
    return 0


if __name__ == "__main__":
    sys.exit(main())
