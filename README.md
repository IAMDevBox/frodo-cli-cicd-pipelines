# frodo-cli-cicd-pipelines

Production-ready GitHub Actions CI/CD pipelines for automating ForgeRock/PingOne AIC configuration management using [Frodo CLI](https://github.com/rockcarver/frodo-cli).

> **Full tutorial**: [Frodo CLI for CI/CD: Automating Journey Export and Import in GitHub Actions](https://iamdevbox.com/posts/frodo-cli-for-cicd-automating-journey-export-import-in-github-actions/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines)

## What This Repo Provides

Four ready-to-use GitHub Actions workflows for managing ForgeRock Identity Cloud configurations:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `export-config.yml` | Daily cron + manual | Auto-export journeys, scripts, OAuth clients to Git |
| `deploy-staging.yml` | PR merge to main | Deploy config changes to staging tenant |
| `deploy-prod.yml` | GitHub Release | Deploy to production with approval gate |
| `multi-env-deploy.yml` | Manual dispatch | Deploy to multiple tenants in parallel |

Plus:
- Import order validation (scripts → email templates → journeys → OAuth clients)
- Pre-deployment backup + automatic rollback on failure
- JSON syntax validation on PRs
- Frodo CLI npm caching for faster runs
- GitHub Environments with required reviewer approvals

## Repository Structure

```
frodo-cli-cicd-pipelines/
├── workflows/                         # Copy to .github/workflows/ in your repo
│   ├── export-config.yml              # Daily automated backup
│   ├── deploy-staging.yml             # Deploy to staging on PR merge
│   ├── deploy-prod.yml                # Deploy to production (release-triggered)
│   └── multi-env-deploy.yml           # Multi-tenant parallel deploy
├── exports/
│   ├── journeys/                      # Exported journey JSON files
│   │   ├── Login.journey.json
│   │   └── Registration.journey.json
│   ├── scripts/                       # Exported script JSON files
│   │   └── CustomValidation.script.json
│   ├── oauth/                         # Exported OAuth client configs
│   │   └── my-spa-client.oauth2.json
│   └── esv/
│       └── variables.json             # ESV variables (NOT secrets)
├── tests/
│   ├── validate_json.py               # JSON structure validator
│   └── test_frodo_connection.sh       # Connection health check script
├── docs/
│   ├── SETUP.md                       # Detailed setup guide
│   └── TROUBLESHOOTING.md             # Common issues and fixes
├── .gitignore
└── README.md
```

## Quick Start

### 1. Clone This Repo

Use it as a starting point for your ForgeRock config repository:

```bash
git clone https://github.com/IAMDevBox/frodo-cli-cicd-pipelines.git my-forgerock-config
cd my-forgerock-config

# Activate the GitHub Actions workflows
mkdir -p .github/workflows
cp workflows/*.yml .github/workflows/
```

### 2. Configure GitHub Secrets

Go to **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|--------|------------|
| `FRODO_DEV_HOST` | Dev tenant URL: `https://openam-dev.example.forgeblocks.com/am` |
| `FRODO_DEV_USER` | Dev service account email |
| `FRODO_DEV_PASSWORD` | Dev service account password |
| `FRODO_STAGING_HOST` | Staging tenant URL |
| `FRODO_STAGING_USER` | Staging service account email |
| `FRODO_STAGING_PASSWORD` | Staging service account password |
| `FRODO_PROD_HOST` | Production tenant URL |
| `FRODO_PROD_USER` | Production service account email |
| `FRODO_PROD_PASSWORD` | Production service account password |

> **Security note**: Never use personal admin accounts. Create dedicated service accounts with minimum required permissions. See [docs/SETUP.md](docs/SETUP.md) for service account configuration.

### 3. Configure GitHub Environments

Create three environments in **Settings → Environments**:
- `staging` — no approval required (auto-deploy on PR merge)
- `production` — require at least 1 reviewer approval

### 4. Test Your Connection

```bash
# Install Frodo CLI locally
npm install -g @rockcarver/frodo-cli

# Test connection to your dev tenant
export FRODO_HOST="https://openam-dev.example.forgeblocks.com/am"
export FRODO_USER="your-service-account@example.com"
export FRODO_PASSWORD="your-password"

frodo journey list
```

### 5. Run Your First Export

Trigger the export workflow manually:

```
GitHub Actions → Export ForgeRock Configuration → Run workflow
```

This creates JSON files in `exports/` which you commit back to the repo.

## Workflows in Detail

### Export Config (Daily Backup)

`.github/workflows/export-config.yml`

Runs daily at 2 AM UTC and on manual trigger. Exports:
- All journeys → `exports/journeys/`
- All scripts → `exports/scripts/`
- All OAuth 2.0 clients → `exports/oauth/`
- ESV variables (not secrets) → `exports/esv/`

Commits changes with message: `chore: daily config export YYYY-MM-DD`

### Deploy to Staging

`.github/workflows/deploy-staging.yml`

Triggered when a PR merges to `main` with changes in `exports/`. Includes:
1. JSON syntax validation
2. Backup of current staging config
3. Import in correct order (scripts → email templates → journeys → OAuth)
4. Automatic rollback if any step fails
5. Creates a GitHub issue for production deployment approval

### Deploy to Production

`.github/workflows/deploy-prod.yml`

Triggered on GitHub Release publication. Features:
- Requires `production` environment approval (manual reviewer sign-off)
- Optional `workflow_dispatch` with confirmation input (`type "deploy"`)
- Full pre-deployment backup
- Ordered import with error detection
- Deployment summary in GitHub Actions step summary

### Multi-Environment Deploy

`.github/workflows/multi-env-deploy.yml`

Manual dispatch workflow for deploying to multiple tenants in parallel using GitHub Actions matrix strategy. Useful for:
- Mass updates across dev/staging/QA tenants
- Tenant onboarding automation
- Configuration synchronization

## Import Order

Always import in this order to avoid dependency failures:

```
1. Scripts          (referenced by journey nodes)
2. Email Templates  (referenced by journey email nodes)
3. Journeys         (depend on scripts and templates)
4. OAuth Clients    (may reference journeys via redirect URIs)
```

The `deploy-staging.yml` and `deploy-prod.yml` workflows enforce this order automatically.

## Security Best Practices

- **Never export ESV secrets to Git** — only export ESV variables
- **Use `.gitignore`** to exclude `*.secret.json` and `TokenCache.json`
- **Service accounts only** — do not use personal admin credentials in CI/CD
- **Environment protection rules** — require approval for production deployments
- **Rotate credentials** after any team member leaves
- **Audit via Git history** — every config change is traceable

## Troubleshooting

See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) for common issues.

Quick checks:

```bash
# Test Frodo connection
./tests/test_frodo_connection.sh

# Validate all JSON files
python3 tests/validate_json.py exports/

# Enable debug logging
DEBUG=frodo:* frodo journey list --verbose
```

## Related Resources

- **Full Tutorial**: [Frodo CLI for CI/CD: Automating Journey Export and Import in GitHub Actions](https://iamdevbox.com/posts/frodo-cli-for-cicd-automating-journey-export-import-in-github-actions/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines)
- **Frodo CLI Series**: [Complete Frodo CLI Guide](https://iamdevbox.com/posts/frodo-cli-complete-guide-installation-setup-and-multi-tenant-management/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines)
- **Script Management**: [Frodo Script Bulk Export/Import](https://iamdevbox.com/posts/frodo-script-management-bulk-export-import-and-version-control-for-am-scripts/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines)
- **ESV Automation**: [Frodo ESV Management](https://iamdevbox.com/posts/frodo-esv-management-environment-secrets-and-variables-automation/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines)
- **Official Frodo CLI**: [github.com/rockcarver/frodo-cli](https://github.com/rockcarver/frodo-cli)

## License

MIT — use freely in your own ForgeRock automation projects.

---

*Built by [IAMDevBox.com](https://iamdevbox.com/?utm_source=github&utm_medium=companion-repo&utm_campaign=frodo-cli-cicd-pipelines) — IAM tutorials, tools, and automation for identity developers.*
