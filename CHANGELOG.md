# Changelog

All notable changes to this project are listed here, newest first.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- First version. It runs [leash](https://github.com/patkusch/leash) (agent permissions), [skillgate](https://github.com/patkusch/skillgate) (agent skills) and [mandata](https://github.com/patkusch/mandata) (instruction files) on a repo and prints one page: what to fix first, what to check, what each tool saw, and what the page cannot tell you.
- It runs whichever of the three are installed and says which were not, with the command to install them. If no tool could run, it exits with 2 rather than looking clean.
- Advice that repeats word for word is given once and then pointed back to.
- `--json`, `--all` (show the small notes), `--only` and `--skip` (choose tools), and `--fail-on fix|check|never` (choose when the exit code is 1).
