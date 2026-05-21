# Container Scanning Demo

This repo now includes a realistic **legacy PHP container** plus GitHub Actions workflows that publish findings into **Security → Code scanning alerts**.

## What container scanning is

Container scanning looks for known vulnerabilities and risky configuration inside the image you plan to ship:
- **OS packages** in the base image
- **Application libraries** installed into the image
- **Dockerfile misconfigurations** such as insecure defaults

For this demo, the image intentionally uses **`php:7.4-apache`** and outdated Composer packages so Trivy produces findings that are easy to show live.

## Demo assets in this repo

- `Dockerfile` — legacy PHP 7.4 Apache image
- `container-demo/index.php` — simple PHP application
- `container-demo/composer.json` — intentionally outdated Composer dependencies
- `container-demo/config-example.php` — demo config file for secret scanning walkthroughs
- `.github/workflows/container-scan.yml` — standard GitHub-hosted image + Dockerfile scanning
- `.github/workflows/external-vm-scan.yml` — simulates an external VM scanning pattern
- `scripts/external-scan.sh` — VM-friendly Trivy + SARIF upload script
- `.github/dependabot.yml` — watches both Docker and Composer dependencies

## How the main workflow works

The `Container scanning` workflow runs on:
- pushes to `main` or `master`
- pull requests targeting `main` or `master`
- manual runs through **Actions → Container scanning → Run workflow**

It performs two scans:

1. **Image scan**
   - Builds the PHP image locally in GitHub Actions
   - Runs Trivy against OS and library packages
   - Uploads SARIF results with `github/codeql-action/upload-sarif@v3`

2. **Dockerfile config scan**
   - Runs Trivy config checks against `Dockerfile`
   - Uploads SARIF results to GitHub Security as a separate category

## External VM scanning pattern

The customer mental model is also supported:

1. Build or pull the image on an external VM
2. Run `scripts/external-scan.sh` with Trivy CLI on that VM
3. Produce SARIF locally
4. Upload the SARIF back to GitHub code scanning

The `External VM scanning pattern` workflow simulates this by:
- building the image
- exporting it as a tarball
- loading and running it in a second job that acts like the VM
- scanning the running container via Trivy CLI
- uploading SARIF to GitHub Security

## How to trigger the demo

### Option 1: Standard GitHub-hosted scan
1. Commit and push these changes
2. Open **Actions**
3. Select **Container scanning**
4. Open the latest workflow run

### Option 2: External VM pattern
1. Open **Actions**
2. Select **External VM scanning pattern**
3. Run the workflow manually, or trigger it with a change to `Dockerfile` or `container-demo/`
4. Show that the second job acts like an off-platform scanner that still lands findings in GitHub Security

### Option 3: Pull request demo
1. Create a new branch
2. Change `container-demo/composer.json` or `Dockerfile`
3. Open a pull request into `master`
4. Show the workflow run and resulting alerts

## Where to see results

After a workflow finishes:
1. Open the repository in GitHub
2. Go to **Security**
3. Select **Code scanning alerts**
4. Filter by categories such as `container-image`, `dockerfile-misconfig`, or `external-vm-container`

This is the cleanest demo path because container findings show up in the same GHAS Security experience used for other scans.

## Dependabot coverage

Dependabot is configured to monitor:
- the root `Dockerfile` for base image updates
- `container-demo/composer.json` for PHP library updates

That gives you a remediation story immediately after showing the scan findings.

## Suggested live demo script

1. Show the `Dockerfile` and point out `php:7.4-apache`
2. Open `container-demo/composer.json` and highlight the intentionally outdated PHP packages
3. Run either **Container scanning** or **External VM scanning pattern**
4. Open **Security → Code scanning alerts** and review findings from the container image
5. Explain that GitHub remains the detection layer while the existing ADO automation can still be the downstream work-management layer

## How this ties back to ADO and the Logic App

The container findings live in GitHub's Security experience alongside other code scanning results. For the broader demo story:
- GitHub surfaces the vulnerability details
- Security findings can be triaged from the GitHub Security tab
- The existing GHAzDO/ADO automation pattern remains the downstream work-management story for teams that want central tracking in Azure DevOps

If you want to make the end-to-end story explicit in the demo, use container alerts in GitHub as the detection layer and then explain that the Logic App pattern is the automation layer for routing actionable work into ADO.
