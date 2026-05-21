---
name: "container-scanning-demo"
description: "Set up a demo-ready GitHub container scanning workflow with a vulnerable sample image, Trivy SARIF uploads, and Dependabot coverage."
domain: "security"
confidence: "high"
source: "earned"
tools:
  - name: "docker"
    description: "Build and smoke-test the demo image when a local Docker engine is available."
    when: "Use after creating the Dockerfile and demo assets."
  - name: "gh"
    description: "Push the demo branch and inspect workflow runs in GitHub."
    when: "Use after workflow files are committed."
---

## Context
Use this skill when a repository needs a clean, easy-to-demo example of GitHub-based container scanning without standing up a full application. It fits especially well when the goal is to show findings in the GitHub Security tab and connect them to downstream work-management tooling.

## Patterns
- Create a minimal `Dockerfile` at the repo root so GitHub Actions can build the image without extra setup.
- Add a tiny support folder such as `container-demo/` with intentionally outdated packages to guarantee visible findings.
- Use Trivy twice: once for the built image (`vuln-type: os,library`) and once for Dockerfile config scanning (`scan-type: config`).
- Upload SARIF with `github/codeql-action/upload-sarif@v3` so alerts appear in **Security → Code scanning alerts**.
- Keep demo workflows non-blocking (`exit-code: "0"`) unless the purpose is policy enforcement.
- Add `.github/dependabot.yml` with the `docker` ecosystem pointed at `/` so base image updates are covered.
- Include a markdown walkthrough that explains trigger paths, where results appear, and how the demo relates to the broader security workflow.

## Examples
- `Dockerfile`
- `container-demo/requirements.txt`
- `.github/workflows/container-scan.yml`
- `.github/dependabot.yml`
- `docs/container-scanning-demo.md`

## Anti-Patterns
- Do not rely on console-only scan output if the goal is a GitHub Security tab demo.
- Do not make the first demo workflow fail unless a red pipeline is part of the story.
- Do not use a large application stack when a tiny intentionally vulnerable image is enough to demonstrate the scanning flow.
