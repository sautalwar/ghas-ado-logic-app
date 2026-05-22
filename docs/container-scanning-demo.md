# Container Scanning Demo

This repo now includes a demo container image and a GitHub Actions workflow that publishes container findings into **Security → Code scanning alerts**.

## What container scanning is

Container scanning looks for known vulnerabilities and risky configuration inside the image you plan to ship:
- **OS packages** in the base image
- **Application libraries** installed into the image
- **Dockerfile misconfigurations** such as insecure defaults

For this demo, the `Dockerfile` intentionally uses an older base image and outdated Python packages so Trivy can produce alerts that are easy to show live.

## Demo assets in this repo

- `Dockerfile` — builds the demo image
- `container-demo/requirements.txt` — intentionally outdated packages for visible findings
- `.github/workflows/container-scan.yml` — builds and scans the image with Trivy
- `.github/dependabot.yml` — watches the Docker base image for updates

## How the workflow works

The workflow runs on:
- pushes to `main` or `master`
- pull requests targeting `main` or `master`
- manual runs through **Actions → Container scanning → Run workflow**

It performs two scans:

1. **Image scan**
   - Builds the Docker image locally in GitHub Actions
   - Runs Trivy against OS and library packages
   - Uploads SARIF results with `github/codeql-action/upload-sarif@v3`

2. **Dockerfile config scan**
   - Runs Trivy config checks against `Dockerfile`
   - Uploads SARIF results to GitHub Security as a separate category

## How to trigger the demo

### Option 1: Push the current setup
1. Commit and push these changes
2. Open **Actions** in GitHub
3. Select **Container scanning**
4. Open the latest workflow run

### Option 2: Create a pull request demo
1. Create a new branch
2. Change `container-demo/requirements.txt` or `Dockerfile`
3. Open a pull request into `master`
4. Show the workflow run and resulting alerts

### Option 3: Manual run
1. Open **Actions**
2. Choose **Container scanning**
3. Click **Run workflow**

## Where to see results

After the workflow finishes:
1. Open the repository in GitHub
2. Go to **Security**
3. Select **Code scanning alerts**
4. Filter by categories such as `container-image` or `dockerfile-misconfig`

This is the cleanest demo path because it shows container findings in the same Security experience used for other GHAS scans.

## Dependabot for base image updates

Dependabot is configured to monitor the root `Dockerfile`. When the base image tag changes upstream, GitHub can open a pull request suggesting an updated image.

## Suggested live demo script

1. Show the `Dockerfile` and point out the intentionally outdated packages
2. Push a small change or manually run the workflow
3. Open the Actions run and show the image build + Trivy steps
4. Open **Security → Code scanning alerts** and review the findings
5. Explain that the same repository can feed alerts into the existing ADO automation story

## How this ties back to ADO and the Logic App

The container findings live in GitHub's Security experience alongside other code scanning results. For the broader demo story:
- GitHub surfaces the vulnerability details
- Security findings can be triaged from the GitHub Security tab
- The existing GHAzDO/ADO automation pattern remains the downstream work-management story for teams that want central tracking in Azure DevOps

If you want to make the end-to-end story explicit in the demo, use container alerts in GitHub as the detection layer and then explain that the Logic App pattern is the automation layer for routing actionable work into ADO.
