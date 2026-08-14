#!/usr/bin/env python3
"""Stamp the version into the published artifacts.

The versioned files in this repository are templates: `models.json` carries
`@VERSION@`/`@DATE@` rather than a literal version, and the citation metadata
lives in `CITATION.cff.in`. This script resolves the version once (see
`tools/version.py` — the git tag is the source of truth) and writes the stamped
copies into the build directory. Nothing versioned is committed with a literal
version in it, so the tag, the dataset and the citation file cannot disagree.

`CITATION.cff` is therefore a build artifact, not a repository file: it is
published with the dataset and served from the site (`/data/CITATION.cff`), so
the citation a reader picks up always matches the dataset they just fetched.

Usage: render.py <outdir> [--require-release]
  --require-release  fail unless the version is a plain X.Y.Z from a clean tagged
                     commit (used by `make deploy`, so the live site is never
                     stamped with a dev version).
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from version import is_release, resolve  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
# source template -> published name
TEMPLATES = {
    "models.json": "models.json",
    "CITATION.cff.in": "CITATION.cff",
}
# Copied through untouched: generated, and carries no version of its own.
VERBATIM = ["litmus.json"]
TOKEN_RE = re.compile(r"@[A-Z_]+@")


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = {a for a in sys.argv[1:] if a.startswith("--")}
    if len(args) != 1:
        sys.exit("usage: render.py <outdir> [--require-release]")
    out = Path(args[0])

    version, date, source = resolve()
    if "--require-release" in flags and not is_release(version):
        sys.exit(f"render: refusing to publish dev version {version!r} ({source}).\n"
                 f"        Tag the release commit (see RELEASING.md), or set "
                 f"ALLOW_DEV=1 to publish anyway.")

    out.mkdir(parents=True, exist_ok=True)
    subs = {"@VERSION@": version, "@DATE@": date}
    for src, dest in TEMPLATES.items():
        text = (ROOT / src).read_text()
        for token, value in subs.items():
            text = text.replace(token, value)
        leftover = sorted(set(TOKEN_RE.findall(text)))
        if leftover:
            sys.exit(f"render: {src} has unsubstituted token(s): {', '.join(leftover)}")
        (out / dest).write_text(text)
    for name in VERBATIM:
        (out / name).write_text((ROOT / name).read_text())

    print(f"render: v{version} ({date}) from {source} -> {out}/: "
          f"{' '.join(sorted(p.name for p in out.iterdir()))}")


if __name__ == "__main__":
    main()
