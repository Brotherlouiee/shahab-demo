# Quality gates — US-03.T05

Run the complete local quality gate before opening a PR:

```bash
python -m pip install -e ".[test,quality]"
npm ci
npm run quality
```

`quality` runs formatting verification, Python lint, Python type checking, all backend unit/API tests, canonical/data-architecture validators, secret scan and the existing Vite production build. The GitHub Actions workflow runs the same command on every pull request and each push to `main`.

The secret scan is intentionally conservative: it detects credential-shaped literal assignments, not every sensitive word. It is a defense-in-depth gate and never replaces secret-manager use, code review or the future SAST/SCA gates. Documented test placeholders are the only allowed literals.

Use `npm run format:python` only after reviewing its diff; CI always runs `format:check` and never rewrites files.
