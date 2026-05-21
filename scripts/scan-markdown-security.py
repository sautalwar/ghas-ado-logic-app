from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List

SECRET_RULES = {
    'md-aws-access-key': {
        'name': 'Potential AWS access key in markdown',
        'description': 'Markdown content appears to contain an AWS-style access key and should be reviewed.',
        'level': 'error',
        'pattern': re.compile(r'AKIA[0-9A-Z]{16}'),
    },
    'md-github-token': {
        'name': 'Potential GitHub token in markdown',
        'description': 'Markdown content appears to contain a GitHub token or PAT.',
        'level': 'error',
        'pattern': re.compile(r'\bgh[pousr]_[A-Za-z0-9_]{20,255}\b'),
    },
    'md-azure-connection-string': {
        'name': 'Potential Azure connection string in markdown',
        'description': 'Markdown content appears to contain an Azure-style connection string.',
        'level': 'error',
        'pattern': re.compile(r'DefaultEndpointsProtocol=.*AccountKey=.*', re.IGNORECASE),
    },
    'md-generic-secret-assignment': {
        'name': 'Potential hard-coded secret in markdown',
        'description': 'Markdown content contains a token/password/secret assignment that should be reviewed.',
        'level': 'warning',
        'pattern': re.compile(r'(?i)\b(api[_-]?key|access[_-]?token|token|secret|password)\b\s*[:=]\s*["\'][A-Za-z0-9_\-+=/]{8,}["\']'),
    },
}

INSTRUCTION_PATH_PATTERNS = [
    re.compile(r'(^|[\\/])copilot-instructions\.md$', re.IGNORECASE),
    re.compile(r'(^|[\\/])\.github[\\/](agents|skills)[\\/].*\.md$', re.IGNORECASE),
    re.compile(r'(^|[\\/])\.squad[\\/].*\.md$', re.IGNORECASE),
    re.compile(r'(^|[\\/]).*\.agent\.md$', re.IGNORECASE),
    re.compile(r'(^|[\\/])SKILL\.md$', re.IGNORECASE),
]

PROMPT_RISK_PATTERNS = [
    re.compile(r'\byou are\b', re.IGNORECASE),
    re.compile(r'\byour charter\b', re.IGNORECASE),
    re.compile(r'\bignore (all )?(previous|prior) instructions\b', re.IGNORECASE),
    re.compile(r'\bsystem prompt\b', re.IGNORECASE),
    re.compile(r'\bdo not\b', re.IGNORECASE),
    re.compile(r'\balways\b', re.IGNORECASE),
    re.compile(r'\bmust\b', re.IGNORECASE),
]

PROMPT_KEYWORDS = ('prompt', 'instruction', 'agent', 'assistant', 'charter', 'role')
IGNORED_DIRECTORIES = {'.git', 'vendor', 'node_modules', '.venv', '__pycache__'}


def iter_markdown_files(root: Path) -> Iterable[Path]:
    for path in root.rglob('*.md'):
        if any(part in IGNORED_DIRECTORIES for part in path.parts):
            continue
        if path.is_file():
            yield path


def first_line_number(text: str, index: int) -> int:
    return text.count('\n', 0, index) + 1


def add_result(results: List[Dict[str, object]], *, rule_id: str, level: str, message: str, path: Path, line_number: int) -> None:
    results.append(
        {
            'ruleId': rule_id,
            'level': level,
            'message': {'text': message},
            'locations': [
                {
                    'physicalLocation': {
                        'artifactLocation': {'uri': path.as_posix()},
                        'region': {'startLine': max(line_number, 1)},
                    }
                }
            ],
        }
    )


def scan_file(root: Path, path: Path, results: List[Dict[str, object]]) -> None:
    text = path.read_text(encoding='utf-8', errors='ignore')
    relative_path = path.relative_to(root)
    normalized_path = relative_path.as_posix()

    for rule_id, rule in SECRET_RULES.items():
        match = rule['pattern'].search(text)
        if match:
            add_result(
                results,
                rule_id=rule_id,
                level=rule['level'],
                message=rule['description'],
                path=relative_path,
                line_number=first_line_number(text, match.start()),
            )

    is_instruction_path = any(pattern.search(normalized_path) for pattern in INSTRUCTION_PATH_PATTERNS)
    prompt_keyword_hits = sum(len(pattern.findall(text)) for pattern in PROMPT_RISK_PATTERNS)
    lower_text = text.lower()
    has_prompt_context = sum(keyword in lower_text for keyword in PROMPT_KEYWORDS) >= 2

    if is_instruction_path:
        add_result(
            results,
            rule_id='md-instruction-file-review',
            level='note',
            message='Instruction-style markdown file detected. Review for prompt injection and sensitive embedded guidance.',
            path=relative_path,
            line_number=1,
        )

    if prompt_keyword_hits >= 3 and (is_instruction_path or has_prompt_context):
        first_match = next((pattern.search(text) for pattern in PROMPT_RISK_PATTERNS if pattern.search(text)), None)
        line_number = first_line_number(text, first_match.start()) if first_match else 1
        add_result(
            results,
            rule_id='md-prompt-risk-review',
            level='warning',
            message='Markdown content contains multiple instruction-like phrases. Review for prompt injection or unsafe AI guidance.',
            path=relative_path,
            line_number=line_number,
        )


def build_sarif(results: List[Dict[str, object]]) -> Dict[str, object]:
    rules = [
        {
            'id': 'md-instruction-file-review',
            'name': 'Instruction markdown requires review',
            'shortDescription': {'text': 'Instruction-style markdown file detected.'},
            'fullDescription': {'text': 'Instruction and agent markdown should be reviewed for prompt injection and embedded secrets.'},
            'properties': {'tags': ['markdown', 'ai', 'review']},
        },
        {
            'id': 'md-prompt-risk-review',
            'name': 'Prompt-like markdown content requires review',
            'shortDescription': {'text': 'Prompt-style phrases were detected in markdown.'},
            'fullDescription': {'text': 'Files containing prompt directives or system-style instructions should be reviewed before reuse.'},
            'properties': {'tags': ['markdown', 'prompt-injection', 'ai']},
        },
    ]

    for rule_id, rule in SECRET_RULES.items():
        rules.append(
            {
                'id': rule_id,
                'name': rule['name'],
                'shortDescription': {'text': rule['name']},
                'fullDescription': {'text': rule['description']},
                'properties': {'tags': ['markdown', 'secret-scanning']},
            }
        )

    return {
        'version': '2.1.0',
        '$schema': 'https://json.schemastore.org/sarif-2.1.0.json',
        'runs': [
            {
                'tool': {
                    'driver': {
                        'name': 'markdown-security-review',
                        'informationUri': 'https://github.com/github/codeql-action',
                        'rules': rules,
                    }
                },
                'results': results,
            }
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description='Scan markdown and instruction files for secret and prompt-review signals.')
    parser.add_argument('--root', default='.', help='Repository root to scan.')
    parser.add_argument('--output', default='markdown-security-results.sarif', help='SARIF output path.')
    args = parser.parse_args()

    root = Path(args.root).resolve()
    output = Path(args.output).resolve()

    results: List[Dict[str, object]] = []
    for file_path in iter_markdown_files(root):
        scan_file(root, file_path, results)

    output.write_text(json.dumps(build_sarif(results), indent=2), encoding='utf-8')
    print(f'Wrote {len(results)} findings to {output}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
