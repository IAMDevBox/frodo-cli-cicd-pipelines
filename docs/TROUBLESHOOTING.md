# Troubleshooting Guide

## Authentication Failures

**Symptom**: `frodo journey list` returns 401 or connection refused.

**Fix**:
1. Verify your tenant URL — must end with `/am` for ForgeRock AM / PingOne AIC
2. Check the service account hasn't been locked (too many failed logins)
3. Ensure you're using the service account email, not username
4. Test locally first:
   ```bash
   FRODO_HOST="https://openam-dev.example.forgeblocks.com/am" \
   FRODO_USER="cicd-service@example.com" \
   FRODO_PASSWORD="password" \
   frodo journey list
   ```

## Rate Limiting During Import

**Symptom**: Import fails partway through with 429 or connection errors.

**Fix**: Add delay between imports for large configs:
```bash
for file in exports/journeys/*.json; do
  frodo journey import --file "$file"
  sleep 2
done
```

## Import Order Failures

**Symptom**: Journey import fails because a referenced script doesn't exist.

**Fix**: Always import in this order:
1. Scripts first
2. Email templates
3. Journeys
4. OAuth clients

All workflows in this repo already enforce this order.

## JSON Validation Failures

**Symptom**: `validate_json.py` reports parse errors.

**Fix**: Run locally to see which file is malformed:
```bash
python3 tests/validate_json.py exports/
```

Then check the specific file:
```bash
python3 -m json.tool exports/journeys/Login.journey.json
```

If the file looks corrupt, re-export from your dev tenant.

## GitHub Actions Secret Not Found

**Symptom**: Workflow fails with `FRODO_HOST is empty`.

**Fix**:
1. Check secret names exactly match — they're case-sensitive
2. Secrets must be in the repository (not just the environment) for `schedule` triggers
3. For environment-specific secrets, the job must reference the environment

## Frodo CLI Not Found

**Symptom**: `frodo: command not found` in workflow.

**Fix**: The npm install step is caching Frodo. If cache is stale:
```yaml
- name: Install Frodo CLI
  run: npm install -g @rockcarver/frodo-cli@latest
```

## Enable Debug Logging

For verbose Frodo output in local debugging:
```bash
DEBUG=frodo:* frodo journey list --verbose
```

In GitHub Actions, add to the step env:
```yaml
env:
  DEBUG: frodo:*
```

## Related Resources

- [Full Tutorial](https://iamdevbox.com/posts/frodo-cli-for-cicd-automating-journey-export-import-in-github-actions/)
- [Frodo CLI Issues](https://github.com/rockcarver/frodo-cli/issues)
