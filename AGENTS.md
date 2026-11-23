# Working in agentcheck

One plain-English page about how safe a repo is to hand to a coding agent. It runs leash, skillgate and mandata and puts what they find in one list.

## Run the tests

You need Python 3.9 or newer.

```bash
python -m unittest discover -s tests
```

Every test should pass before you start and after you finish. The tests in `tests/test_real_tools.py` are skipped unless leash, skillgate and mandata are installed.

## Where things are

- `agentcheck/`: the code (the package)
- `tests/`: the tests
- `examples/`: two projects the real-tool tests run on, one healthy and one with planted problems
- `.github/`: CI, issue form, pull request template and Dependabot

## Before you commit

- Make sure the tests pass.
- Put changes people will notice in `CHANGELOG.md`.
- agentcheck does no checking of its own: if a finding is wrong, the fix belongs in leash, skillgate or mandata.
- Do not put real passwords, keys or private data in test files or examples. Use made-up ones.
