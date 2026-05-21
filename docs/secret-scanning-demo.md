# Secret Scanning Demo

GitHub secret scanning is a **repository setting**, not a workflow file, so this demo documents the enablement path and provides safe demo artifacts for the customer walkthrough.

## What this demo covers

- how to enable secret scanning and push protection
- how supported partner patterns differ from custom patterns
- how to demo an alert safely without using a real credential
- how secret scanning fits into the broader GHAzDO-to-ADO story

## Demo assets in this repo

- `container-demo/config-example.php` — safe demo config with a fake token for custom-pattern testing
- `scripts/create-secret-scanning-pattern.sh` — optional helper to create a repo-level custom pattern through the GitHub API
- `docs/secret-scanning-demo.md` — this walkthrough

## Enable GitHub secret scanning

1. Open the repository in GitHub.
2. Go to **Settings → Advanced Security**.
3. Under **Secret Protection**, enable:
   - **Secret scanning**
   - **Push protection**
4. Confirm that alerts will be shown in **Security → Secret scanning**.

## Safe demo pattern for this repo

The file `container-demo/config-example.php` contains this fake token:

`LEARFIELD-DEMO-7G9K2P4R6T8V0X1Z`

It is intentionally fake and only exists for a demo. By default GitHub will not know this token type, so create a custom pattern first.

## Create a custom pattern

### Option 1: GitHub UI
1. Open **Settings → Advanced Security**.
2. Under **Secret Protection**, click **Custom patterns → New pattern**.
3. Use a pattern similar to:

```regex
LEARFIELD-DEMO-[A-Z0-9]{16}
```

4. Name it something like **Learfield Demo Token**.
5. Run the dry run to verify `container-demo/config-example.php` is matched.
6. Publish the pattern.
7. Optionally enable push protection for the pattern after validating the dry run.

### Option 2: GitHub API helper

If you prefer automation, run:

```bash
bash scripts/create-secret-scanning-pattern.sh --repo sautalwar/ghas-ado-logic-app
```

The helper uses `gh api` to create the same custom pattern at the repository level.

## What the customer should see

After secret scanning is enabled and the custom pattern is published:
1. GitHub scans the full repository history and the latest commit.
2. `container-demo/config-example.php` should produce a **Secret scanning alert**.
3. The alert appears in **Security → Secret scanning** with the file path and matched pattern.
4. From there the team can revoke, rotate, or dismiss as appropriate.

## Supported secrets vs. custom secrets

- **Supported secrets**: AWS, Azure, GitHub, npm, Stripe, and many other providers are detected automatically.
- **Custom patterns**: best for internal tokens, copied demo strings, and org-specific formats that GitHub does not recognize out of the box.

For this repo, the custom pattern is the safer demo choice because it avoids putting a real-looking vendor credential in source control.

## Suggested live demo flow

1. Show `container-demo/config-example.php` and point out the clearly fake token.
2. Open **Settings → Advanced Security** and confirm secret scanning is enabled.
3. Show the custom pattern or create it live.
4. Navigate to **Security → Secret scanning** and open the resulting alert.
5. Explain how the alert lifecycle maps to triage and downstream Azure DevOps work management.

## ADO/GHAzDO tie-in

Secret scanning is the detection layer in GitHub. Once the customer sees the alert in GitHub Security, you can connect the story back to the existing Azure DevOps automation pattern:
- GitHub detects and surfaces the secret exposure
- Teams triage in GitHub Security
- The broader ADO integration pattern remains the downstream tracking and workflow story
