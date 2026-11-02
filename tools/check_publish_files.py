#!/usr/bin/env python3
"""Check repository uploads and built pages for local-only material."""
import argparse
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PRIVATE_PARTS = {"PubPaperPDFs", ".local-only", ".claude", ".vscode", "__pycache__", ".ipynb_checkpoints"}
PRIVATE_NAMES = {"AGENTS.md", "CLAUDE.md", ".DS_Store"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site", type=Path, help="Check the generated artifact instead of Git upload candidates")
    args = parser.parse_args()
    # Only course PDFs explicitly linked by the teaching page may be published.
    course_pdfs = set(re.findall(r"url:\s*(/teaching/[^\s]+\.pdf)", (ROOT / "_data/teaching.yml").read_text()))
    if args.site:
        base = args.site.resolve()
        candidates = [p.relative_to(base) for p in base.rglob("*") if p.is_file()]
    else:
        base = ROOT
        names = subprocess.check_output(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"], cwd=ROOT)
        candidates = [Path(p.decode()) for p in names.split(b"\0") if p]
    rejected = []
    for path in sorted(set(candidates)):
        if not (base / path).exists():
            continue
        private = bool(PRIVATE_PARTS.intersection(path.parts)) or path.name in PRIVATE_NAMES
        private |= path.name == ".env" or path.name.startswith(".env.") and path.name != ".env.example"
        private |= path.suffix.lower() in {".ipynb", ".pyc", ".pyo"}
        private |= path.suffix.lower() == ".pdf" and "/" + path.as_posix() not in course_pdfs
        if private:
            rejected.append(path.as_posix())
    if rejected:
        raise SystemExit("Local-only files found:\n" + "\n".join(rejected))
    print(f"Upload boundary check passed ({len(candidates)} files; {len(course_pdfs)} approved teaching PDFs).")


if __name__ == "__main__":
    main()
