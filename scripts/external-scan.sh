#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  external-scan.sh --image <image-ref> --sarif <output.sarif> [options]
  external-scan.sh --container <container-name> --sarif <output.sarif> [options]
  external-scan.sh --image-tar <image.tar> --sarif <output.sarif> [options]

Options:
  --repo <owner/repo>          Repository to upload into.
  --ref <git-ref>              Full git ref, e.g. refs/heads/master.
  --sha <commit-sha>           Commit SHA for the SARIF upload.
  --token <github-token>       GitHub token with security_events or repo scope.
  --tool-name <name>           Tool name shown in GitHub. Default: trivy-external-vm
  --checkout-uri <uri>         Checkout URI for SARIF payload. Default: file:///workspace
  --upload-method <gh|curl>    Upload method. Default: gh
  --skip-upload                Generate SARIF but do not call the GitHub API.
EOF
}

image_ref=""
container_name=""
image_tar=""
sarif_file=""
repo="${GITHUB_REPOSITORY:-}"
ref_value="${GITHUB_REF:-}"
sha_value="${GITHUB_SHA:-}"
token_value="${GITHUB_TOKEN:-${GH_TOKEN:-}}"
tool_name="trivy-external-vm"
checkout_uri="file:///workspace"
upload_method="gh"
skip_upload="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image)
      image_ref="$2"
      shift 2
      ;;
    --container)
      container_name="$2"
      shift 2
      ;;
    --image-tar)
      image_tar="$2"
      shift 2
      ;;
    --sarif)
      sarif_file="$2"
      shift 2
      ;;
    --repo)
      repo="$2"
      shift 2
      ;;
    --ref)
      ref_value="$2"
      shift 2
      ;;
    --sha)
      sha_value="$2"
      shift 2
      ;;
    --token)
      token_value="$2"
      shift 2
      ;;
    --tool-name)
      tool_name="$2"
      shift 2
      ;;
    --checkout-uri)
      checkout_uri="$2"
      shift 2
      ;;
    --upload-method)
      upload_method="$2"
      shift 2
      ;;
    --skip-upload)
      skip_upload="true"
      shift
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

if [[ -z "$sarif_file" ]]; then
  echo "Missing required argument: --sarif" >&2
  exit 1
fi

if ! command -v trivy >/dev/null 2>&1; then
  echo "Trivy CLI is required on the external VM." >&2
  exit 1
fi

if [[ -n "$container_name" ]]; then
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker CLI is required when scanning a running container." >&2
    exit 1
  fi
  image_ref="$(docker inspect --format='{{.Image}}' "$container_name")"
fi

if [[ -z "$image_ref" && -z "$image_tar" ]]; then
  echo "Provide one of --image, --container, or --image-tar." >&2
  exit 1
fi

if [[ -n "$image_tar" ]]; then
  trivy image --input "$image_tar" --format sarif --output "$sarif_file" --severity MEDIUM,HIGH,CRITICAL --ignore-unfixed
else
  trivy image "$image_ref" --format sarif --output "$sarif_file" --severity MEDIUM,HIGH,CRITICAL --ignore-unfixed
fi

echo "SARIF written to $sarif_file"

if [[ "$skip_upload" == "true" ]]; then
  echo "Skipping GitHub upload because --skip-upload was supplied."
  exit 0
fi

if [[ -z "$repo" || -z "$ref_value" || -z "$sha_value" ]]; then
  echo "Upload requires --repo, --ref, and --sha (or matching GITHUB_* environment variables)." >&2
  exit 1
fi

if [[ -z "$token_value" ]]; then
  echo "Upload requires --token or GITHUB_TOKEN/GH_TOKEN." >&2
  exit 1
fi

payload_file="${sarif_file}.payload.json"
python3 - "$sarif_file" "$sha_value" "$ref_value" "$checkout_uri" "$tool_name" > "$payload_file" <<'PY'
import base64
import gzip
import json
import sys

sarif_path, sha_value, ref_value, checkout_uri, tool_name = sys.argv[1:]
with open(sarif_path, 'rb') as handle:
    encoded = base64.b64encode(gzip.compress(handle.read())).decode('ascii')

payload = {
    'commit_sha': sha_value,
    'ref': ref_value,
    'sarif': encoded,
    'checkout_uri': checkout_uri,
    'tool_name': tool_name,
}
print(json.dumps(payload))
PY

if [[ "$upload_method" == "gh" ]]; then
  GH_TOKEN="$token_value" gh api \
    --method POST \
    -H "Accept: application/vnd.github+json" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    "/repos/${repo}/code-scanning/sarifs" \
    --input "$payload_file"
else
  curl -sSfL \
    -X POST \
    -H "Accept: application/vnd.github+json" \
    -H "Authorization: Bearer ${token_value}" \
    -H "X-GitHub-Api-Version: 2022-11-28" \
    -H "Content-Type: application/json" \
    "https://api.github.com/repos/${repo}/code-scanning/sarifs" \
    --data-binary @"$payload_file"
fi

rm -f "$payload_file"
echo "Uploaded SARIF to GitHub code scanning for ${repo}."
