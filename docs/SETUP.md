# Setup Guide

## Prerequisites

1. **Frodo CLI** (v2+): Install with `npm install -g @rockcarver/frodo-cli`
2. **GitHub repository** with Actions enabled
3. **ForgeRock/PingOne AIC** tenants (dev, staging, production)
4. **Service account** in each tenant

## Service Account Setup

Create a dedicated service account in each ForgeRock tenant instead of using personal admin credentials.

### PingOne Advanced Identity Cloud

1. Go to **Identities → Managed Objects → Alpha_User** (or your realm's user store)
2. Create a new user for CI/CD: `cicd-service@corp.example.com`
3. Assign the minimum required roles:
   - `Journey Administrator` — for journey export/import
   - `Script Administrator` — for script export/import
   - `OAuth2 Administrator` — for OAuth client export/import
4. Note the password — store it in GitHub Secrets

### GitHub Secrets Configuration

Go to your repository → **Settings** → **Secrets and variables** → **Actions**.

Add the following secrets for each environment:

| Secret | Value Example |
|--------|--------------|
| `FRODO_DEV_HOST` | `https://openam-dev.example.forgeblocks.com/am` |
| `FRODO_DEV_USER` | `cicd-service@corp.example.com` |
| `FRODO_DEV_PASSWORD` | `<password>` |
| `FRODO_STAGING_HOST` | `https://openam-staging.example.forgeblocks.com/am` |
| `FRODO_STAGING_USER` | `cicd-service@corp.example.com` |
| `FRODO_STAGING_PASSWORD` | `<password>` |
| `FRODO_PROD_HOST` | `https://openam.example.forgeblocks.com/am` |
| `FRODO_PROD_USER` | `cicd-service@corp.example.com` |
| `FRODO_PROD_PASSWORD` | `<password>` |

## GitHub Environments

Create protection rules for your environments:

1. Go to **Settings → Environments**
2. Create `staging`:
   - No approval required (auto-deploy on PR merge to main)
   - Environment secrets: `FRODO_STAGING_*`
3. Create `production`:
   - **Required reviewers**: Add at least one team member
   - Deployment branch rule: `main` only
   - Environment secrets: `FRODO_PROD_*`

## Initial Setup Steps

```bash
# 1. Install Frodo CLI locally
npm install -g @rockcarver/frodo-cli

# 2. Test connection to your dev tenant
export FRODO_HOST="https://openam-dev.example.forgeblocks.com/am"
export FRODO_USER="cicd-service@corp.example.com"
export FRODO_PASSWORD="your-password"

./tests/test_frodo_connection.sh

# 3. Do your first manual export to populate the exports/ directory
mkdir -p exports/{journeys,scripts,oauth,esv}
frodo journey export --all --directory exports/journeys
frodo script export --all --directory exports/scripts
frodo oauth client export --all --directory exports/oauth

# 4. Validate the exported JSON
python3 tests/validate_json.py exports/

# 5. Commit the initial exports
git add exports/
git commit -m "chore: initial config export"
git push
```

## Credential Rotation

Rotate service account passwords when:
- A team member leaves
- Credentials are accidentally exposed
- As part of your regular security rotation schedule

After rotating:
1. Update the GitHub Secret with the new password
2. Test the connection: trigger the `export-config.yml` workflow manually

## Related Resources

- [Full Tutorial on iamdevbox.com](https://iamdevbox.com/posts/frodo-cli-for-cicd-automating-journey-export-import-in-github-actions/)
- [Frodo CLI Documentation](https://github.com/rockcarver/frodo-cli)
- [GitHub Environments Docs](https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment)
