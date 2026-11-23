# Contributing to agentcheck

Thanks for helping. Small fixes and clearer wording are both welcome.

## Run the tests

You need Python 3.9 or newer.

```bash
python -m unittest discover -s tests
```

Most tests use stand-ins for leash, skillgate and mandata, so they need none of them. To run the tests that use the real tools, install them first:

```bash
pip install git+https://github.com/patkusch/leash git+https://github.com/patkusch/skillgate git+https://github.com/patkusch/mandata
```

Every test should pass before you start and after you finish.

## Send a change

- Keep each pull request to one change, and say what it fixes and why.
- Add a test with your change where you can. A test that fails without your change is the best proof it works.
- agentcheck does no checking of its own. If a finding is wrong, the fix belongs in the tool that made it (leash, skillgate or mandata). Open the issue there, or here if you are not sure which.
- Do not put real passwords, keys or private data in test files or examples. Use made-up ones.

## Report a problem

Open an issue and fill in the form. If it is a security problem, follow [SECURITY.md](SECURITY.md) and report it privately instead.
