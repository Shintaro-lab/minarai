---
name: safe-push
description: Run pre-push safety checks on a git repository (missed commits, secrets/credentials, PII or local-machine path leaks, unexpectedly large files including in git history, .gitignore effectiveness against build artifacts like venv/node_modules/__pycache__, and the test suite), then push to the remote automatically only if everything is clean. Use this whenever the user asks to push code, especially to a public repository, or asks to "check before pushing", "push safely", or expresses worry about leaking secrets, committing large files, or forgetting to gitignore something like a virtualenv or node_modules. Also trigger on Japanese phrasing like "pushして良いか確認して", "念のためチェックしてからpush", "情報漏洩がないか確認してpush". Prefer this skill over a plain `git push` whenever the target remote is public or the user signals any safety concern about what's about to become visible.
---

# Safe Push

Push is hard to take back once something sensitive or huge has reached a public
remote — force-pushing history away doesn't un-leak a secret that was already
fetched. This skill exists to make that irreversible step boring: run the same
checks a careful reviewer would run by hand, and only push once they're clean.

## The rule that shapes everything below

**Findings block the push; open questions don't get silently resolved.**

- If a check in steps 2-5 (secrets, PII/local-path leaks, unexpectedly large
  files, or a tracked build artifact) turns anything up: **stop, do not push**,
  report exactly what was found with file:line where possible, and ask the
  user how to proceed. Never push while one of these is outstanding — these
  are the things that are actually costly to have gotten wrong.
- If the test suite (step 6) fails: **stop, do not push**, report the failure.
- If there are uncommitted or untracked changes (step 1): show the user what
  they are and ask whether to commit them. Don't invent a commit message and
  push on their behalf — they should see what's about to become part of the
  repo's permanent history before it does.
- If none of the above applies — nothing uncommitted needing a decision, no
  findings from steps 2-5, tests green — push immediately without asking
  again. The checks *are* the confirmation; don't make the user approve twice.

Work through the steps in order and stop at the first one that requires the
user's input — no need to keep running later checks once you already know
you're going to pause.

## Step 0: Establish context

```bash
git rev-parse --abbrev-ref HEAD              # current branch
git rev-parse --abbrev-ref --symbolic-full-name @{u}  # upstream, if any
git remote -v
```

If there's no upstream configured, ask the user which remote/branch they mean
before doing anything else. If the remote is something other than obviously
public (e.g. you can't tell), it's fine to ask — but don't hold up a push to
an evidently public GitHub/GitLab remote just to double-confirm what the user
already told you.

## Step 1: Uncommitted and untracked changes

```bash
git status --porcelain
```

- Tracked-file changes (`git diff` for staged/unstaged): summarize what
  changed per file, not just filenames — the user needs enough to judge
  whether it belongs in the commit.
- Untracked files: list them. For anything that looks like generated output,
  local test residue, or a runtime artifact rather than source (a good
  example from this project: a `reviews/*.yaml` file created by manually
  clicking around a local review server), call that out specifically and ask
  whether to commit it, delete it, or leave it untracked — don't assume.

Ask the user how to proceed before moving on. Only continue to step 2 once
this is resolved (either committed with their OK, or deliberately left
uncommitted/untracked for this push).

## Step 2: Secrets and credentials

Scan everything that's about to be pushed — already-tracked files plus
anything newly committed in step 1 — for likely secrets:

```bash
git grep -InE "(api[_-]?key|secret|password|passwd|token|aws_access|private[_-]?key)" -- . ':(exclude).git'
git grep -InE "\-\-\-\-\-BEGIN (RSA|EC|OPENSSH|PGP|DSA) PRIVATE KEY\-\-\-\-\-"
```

Read every hit before deciding. Most will be false positives — a variable
named `password` in a schema definition, `token` as a section heading, a test
fixture referencing a well-known dummy path like `/etc/passwd`. The signal to
look for is an actual *value* sitting next to one of these words: something
that looks like a real key, connection string, or credential rather than a
field name or identifier. When a hit is genuinely ambiguous — you can't tell
whether it's a real secret or a placeholder — flag it rather than silently
clearing it; a false alarm costs the user ten seconds, a missed secret costs
a rotation.

## Step 3: PII and local-machine leaks

```bash
git grep -InE "[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
git grep -InE "C:\\\\Users\\\\[A-Za-z0-9._-]+|/home/[A-Za-z0-9._-]+/|/Users/[A-Za-z0-9._-]+/"
```

Also check for the current OS username leaking into tracked content
(`git grep -Iln "$USER"` / `$env:USERNAME` on Windows) — this typically shows
up by accident in generated config, absolute paths baked into a file, or a
committed log/output file.

Flag genuine hits. Don't flag the repo's own legitimate authorship metadata
(a README's contact line the user put there on purpose, `git log` authorship)
— the goal is catching *accidental* leakage, not sanitizing intentional,
already-public information the user placed there themselves.

## Step 4: Unexpectedly large files

Check both what's currently tracked and the full history, since something
huge can be sitting in an old commit that simply hasn't been pushed yet:

```bash
# Tracked files about to be pushed
git ls-files -z | xargs -0 du -h 2>/dev/null | sort -rh | head -20

# Full history — catches large blobs from any commit, not just HEAD
git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' \
  | awk '$1=="blob"{print $3, $4}' | sort -rn | head -20
```

There's no universal size threshold — judge by the project's own norms (a
few KB of source files is normal; anything in the MB+ range for a
source-only repo warrants a look). Flag anything that looks like a
virtualenv, `node_modules`, build output, a dataset, a binary, or a media
file that shouldn't be in version control. If it's already reachable from a
commit that hasn't been pushed yet, note that removing it cleanly may need
history rewriting (`git filter-repo` or similar) rather than just deleting it
in a new commit — deleting it going forward doesn't remove it from the
commits about to be pushed.

## Step 5: .gitignore effectiveness

Detect the project's stack from what's actually in the repo (presence of
`pyproject.toml`/`requirements.txt` → Python, `package.json` → Node, etc.)
and confirm the tracked file list doesn't include the stack's usual
accidental-commit culprits:

```bash
git ls-files | grep -iE "__pycache__|\.egg-info|\.pytest_cache|(^|/)\.venv/|(^|/)venv/|node_modules|(^|/)dist/|(^|/)build/|\.pyc$|\.DS_Store$"
```

If this comes back empty, `.gitignore` is doing its job. If something does
match, that's the finding — not the absence of a rule in `.gitignore` itself
(a repo can have no `.gitignore` at all and still have nothing tracked worth
worrying about, if nothing generated ever got `git add`ed). What matters is
what's actually about to be pushed, not just whether the ignore file looks
complete on paper.

## Step 6: Test suite

Detect and run whatever test command the repo defines (`pytest`,
`npm test`, `go test ./...`, etc. — check for `pyproject.toml`/`pytest.ini`,
`package.json` scripts, or similar before guessing). If there's no
discoverable test suite, skip this step rather than inventing one to run.

A failing suite blocks the push the same way a finding does — report the
failure and stop.

## Step 7: What's about to go public

```bash
git diff <upstream>..HEAD --stat
git log <upstream>..HEAD --oneline
```

Keep this summary handy for the final report regardless of outcome — if
you're stopping to ask the user something, showing them exactly which
commits and files are in question makes their decision faster.

## Reporting

When everything is clean, push and then report concisely: the commit range
pushed, a one-line diffstat summary, and confirmation each check passed.
Don't re-run the checks a second time or ask for confirmation again — a
clean run *is* the green light.

When something blocks the push, lead with what's blocking it (the specific
finding or failure, with file:line where applicable) before anything else —
the user needs that first, not a recap of the steps that passed.
