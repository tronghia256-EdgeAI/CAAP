# Repository working agreement

Nghĩa has authorized committing and pushing completed work to GitHub after each
task that changes this repository. This preference applies to future sessions.

- Finish the requested changes and run checks appropriate to the change before
  committing. Include completed code, documentation, tests, and saved review
  decisions belonging to the authorized task.
- Review the diff, create a descriptive commit, and push normally to the current
  branch's configured remote. On `main`, use `origin/main` if no upstream is set.
- Confirm that the push succeeded and report the commit and working tree status.
  Aim for a clean working tree without discarding or overwriting user edits.
- Respect `.gitignore`: keep local footage, annotations, generated GT artifacts,
  model weights, credentials, and other ignored files out of commits.
- Preserve unrelated or incomplete changes. Never force-push, reset, or delete
  files merely to make the working tree clean. Resolve remote divergence without
  losing either side's changes; report a real blocker if one prevents the push.
- Do not create empty commits for read-only tasks or when nothing has changed.

This is authorization for the assistant's completed repository tasks; it does not
make launching the GT viewer or each review click trigger a Git commit.

# Persistent paper scope

Nghĩa decided on 2026-10-12 to remove accident severity (`minor`/`severe`)
from this paper. Read `docs/PAPER_SCOPE.md` when planning paper, GT or accident
evaluation work. Do not reintroduce severity labeling, classifier training,
severity metrics or severity claims unless Nghĩa explicitly changes this decision.
Keep the detector's `Accident` class. Any accident evaluation within scope is
binary event detection/alerting, conditional on suitable video GT and a verified
implementation; existing severity code does not establish binary alert results.

## Current workspace map

Read `docs/CURRENT_STATE.md` for the current evidence and open decisions.
`archive/` contains historical drafts, plans and exploratory results, not
current instructions or approval to resume their deadlines, claims or scope.
