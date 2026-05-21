# Markdown Security Scanning Demo

This repo now includes a markdown-focused security review workflow for repos that store prompts, Copilot instructions, agent definitions, and other operational markdown.

## Why this matters

Markdown is often treated as harmless documentation, but customer repos increasingly keep sensitive content in markdown files:
- prompt instructions for AI agents
- agent charter files and orchestration guidance
- operational runbooks with copied tokens or connection strings
- skills and setup docs that may accidentally embed secrets

That means markdown deserves its own security review path.

## Demo assets in this repo

- `.github/workflows/markdown-security-scan.yml` — workflow that runs the scanner and uploads SARIF
- `scripts/scan-markdown-security.py` — scanning logic
- `.github/agents/squad.agent.md` — example agent instruction file
- `.github/skills/e2e-ghasdo-demo/SKILL.md` — example skill instruction file
- `.squad/agents/**/*.md` — additional instruction-heavy markdown content

## What the scanner flags

### 1. Potential secrets in markdown
The script looks for patterns such as:
- AWS-style access keys
- GitHub PATs and tokens
- Azure connection strings
- generic `token=`, `password=`, or `secret=` assignments

### 2. AI instruction files
It flags files for review when the path looks like:
- `copilot-instructions.md`
- `.github/agents/*.md`
- `.github/skills/**/SKILL.md`
- `.squad/**/*.md`
- `*.agent.md`

These findings are informational or warning-level signals that say, in effect: **"this file should receive a security review because it can influence AI behavior."**

### 3. Prompt injection risk phrases
The scanner also looks for instruction-heavy text such as:
- `You are`
- `Your charter`
- `Ignore previous instructions`
- `Do not`
- `Always`
- `Must`

A match is not automatically malicious. It simply creates a review trail in GitHub Security.

## How the workflow runs

The workflow triggers on:
- pushes to `main` or `master`
- pull requests targeting `main` or `master`
- manual runs from the Actions tab

It then:
1. checks out the repository
2. runs `python scripts/scan-markdown-security.py`
3. generates a SARIF file
4. uploads SARIF to **Security → Code scanning alerts**

## How to demo it

1. Open `.github/agents/squad.agent.md` or another instruction-heavy markdown file.
2. Explain that prompt files can carry operational or security risk even when they are not source code.
3. Run **Markdown security scan** from GitHub Actions.
4. Open **Security → Code scanning alerts**.
5. Filter on category `markdown-security-review`.
6. Show both:
   - informational review findings for instruction files
   - higher-severity findings if a markdown file contains a secret-like string

## Extend the pattern

The scanner is intentionally simple and demo-friendly. In a production rollout you could extend it to:
- enforce allowlists for known-safe docs
- create GitHub issues for review findings
- require CODEOWNERS approval on agent and instruction files
- feed SARIF alerts into the same downstream Azure DevOps process used for other GHAS findings
