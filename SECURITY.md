# Security

## Reporting a problem

If you find a security problem, please do not open a public issue. Use
**Security → Report a vulnerability** on this repository so it can be fixed
before the details are public.

## How this project is protected

- **No secrets in the repository.** API keys are read from the environment or
  a local secrets file that `.gitignore` excludes. Every push and pull request
  is scanned for leaked keys, including the full commit history.
- **Dependencies are watched.** Dependabot opens pull requests for outdated
  packages and GitHub Actions.
- **Code scanning.** CodeQL checks the code for common security bugs.
- **Locked-down CI.** Workflows run with read-only permissions and every
  third-party action is pinned to an exact commit, so a hijacked tag cannot
  change what runs.
- **Cost limits.** Question and answer length are capped, and the owner's API
  key (if one is configured) is rate-limited across all visitors.
- **Untrusted model output.** Scores from the model are validated and the final
  decision is calculated locally. User text is wrapped in tags and treated as
  data, which reduces prompt injection.
