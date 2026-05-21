#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: create-secret-scanning-pattern.sh --repo <owner/repo> [--token <token>]

Creates a repo-level demo custom pattern that matches:
  LEARFIELD-DEMO-[A-Z0-9]{16}
EOF
}

repo=""
token_value="${GITHUB_TOKEN:-${GH_TOKEN:-}}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="$2"
      shift 2
      ;;
    --token)
      token_value="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if [[ -z "$repo" ]]; then
  echo "Missing required argument: --repo" >&2
  exit 1
fi

if [[ -z "$token_value" ]]; then
  echo "Provide --token or set GITHUB_TOKEN/GH_TOKEN." >&2
  exit 1
fi

payload=$(cat <<'JSON'
{
  "name": "learfield-demo-token",
  "pattern": "LEARFIELD-DEMO-[A-Z0-9]{16}",
  "title": "Learfield Demo Token",
  "description": "Demo-only custom pattern for secret scanning walkthroughs.",
  "severity": "high"
}
JSON
)

printf '%s' "$payload" | GH_TOKEN="$token_value" gh api \
  --method POST \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${repo}/secret-scanning/secret-scanning-custom-patterns" \
  --input -

echo "Created or submitted the Learfield demo custom pattern for ${repo}."
