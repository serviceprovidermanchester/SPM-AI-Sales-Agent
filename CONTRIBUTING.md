# Contributing

This is a portfolio demonstration maintained for educational use and review. Improvements and bug reports are welcome in a fork or pull request.

## Development setup
Follow `docs/QUICKSTART.md` and install `requirements-dev.txt`. Run `python -m pytest -q` before proposing changes. Avoid adding sensitive data or live credentials to test fixtures.

## Change guidance
Keep modules small and use Pydantic for input validation, parameterized SQL queries and explicit authentication for protected endpoints. Add or update docs when public behavior changes. AI and marketing automation features must remain opt-in, reviewable and consent-aware.

## Code of conduct
Discuss technical questions respectfully and avoid publishing private user data in bug reports.
