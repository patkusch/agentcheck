# agentcheck

[![ci](https://github.com/patkusch/agentcheck/actions/workflows/ci.yml/badge.svg)](https://github.com/patkusch/agentcheck/actions/workflows/ci.yml)

One plain-English page about how safe a repo is to hand to a coding agent.

Before you let an AI coding agent work in a project, three things are worth a look. What the agent is allowed to do without asking, and whether a password got saved into that list. Whether any agent "skill" in the project is doing something sneaky. And whether the instruction files you wrote for the agent are still true. I wrote one small tool for each: [leash](https://github.com/patkusch/leash), [skillgate](https://github.com/patkusch/skillgate) and [mandata](https://github.com/patkusch/mandata). agentcheck runs all three on a repo and puts what they find in one list, most urgent first.

It does no checking of its own. It runs on your computer, reads files, and sends nothing anywhere.

## What it looks like

```
agentcheck: ./examples/risky

14 things to fix first, and 11 to check.

Checked with leash 0.4.2, skillgate 0.1.0, mandata 0.1.0.

FIX THESE FIRST (14)
  1. [leash] .claude/settings.local.json
     a password or key set as an environment variable is written into a 'don't ask again' rule: Pl4n… (17 characters)
     To fix: Delete the rule from the allow list and run the command without the password in it next time (use a variable, a prompt or a credentials file). Then rotate the secret: treat it as already seen.
  2. [leash] .claude/settings.local.json
     a password passed to sshpass is written into a 'don't ask again' rule: Pl4n… (17 characters)
     To fix: same as 1.
  3. [leash] .claude/settings.local.json
     your 'don't ask again' file is committed to a repo (leash could not tell if it is public)
     To fix: Run `git rm --cached .claude/settings.local.json`, add it to .gitignore (`leash --gitignore` does that), commit, and rotate anything secret.
  4. [leash] .claude/settings.local.json
     may read files matching `~/.aws/**`, without asking
     To fix: Remove it, and add `Read(~/.aws/**)` to the deny list so the agent always has to ask.
  ...

WHAT EACH TOOL SAW
  leash      read 1 permission file: 3 critical, 3 high, 4 medium
  skillgate  checked 1 skill: 1 blocked
  mandata    read 1 instruction file: 2 wrong now, 1 probably stale

WHAT THIS PAGE DOES NOT TELL YOU
  An empty list does not mean the repo is safe. It means these tools found nothing.
  They read files. They do not run your code, look at your dependencies, scan your servers or judge advice such as "write clean code".
```

"Fix these first" means something is wrong or dangerous now. "Check these" means it is probably a problem and only you can tell. Small things are counted but hidden until you add `--all`.

## What a clean page means

Less than it looks like. "Nothing to fix first" means these three tools found nothing. They read files. They do not run your code, look at your dependencies, scan your servers, or judge advice such as "write clean code". The page says so at the bottom every time.

If a tool is not installed, or breaks, the page says that too. If none of them could run, agentcheck exits with 2, so an empty page can never pass as a clean one.

## Use it

You need Python 3.9 or newer.

```bash
pip install git+https://github.com/patkusch/agentcheck
pip install git+https://github.com/patkusch/leash git+https://github.com/patkusch/skillgate git+https://github.com/patkusch/mandata

agentcheck                  # the project in this folder
agentcheck path/to/repo     # another one
agentcheck --all            # also show the small notes
agentcheck --json           # the same result as data
agentcheck --skip leash     # leave a tool out (or --only leash,mandata)
```

It exits with 0 when there is nothing to fix first, 1 when there is, and 2 when it could not run. `--fail-on check` also fails on the "check these" items, and `--fail-on never` never fails.

To run it on every push, add a step to your CI:

```yaml
- run: pip install git+https://github.com/patkusch/agentcheck git+https://github.com/patkusch/leash git+https://github.com/patkusch/skillgate git+https://github.com/patkusch/mandata
- run: agentcheck
```

leash is told not to read your home folder or ask GitHub anything, so a run only looks at the project you point it at.

## Tests

68 tests, no network. Most use stand-ins for the three tools. The tests that run the real tools on the two projects in `examples/` (one healthy, one with planted problems) run in CI, which installs all three. `python -m unittest discover -s tests`.

## Licence

MIT. See [LICENSE](LICENSE).

---

[Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)
