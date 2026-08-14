#!/usr/bin/env python3
"""Single source of the dataset's version and release date: the git tag.

Everything that carries a version — `models.json`'s `version`/`date`, the served
`CITATION.cff` — is a template stamped at build time from this one resolver
(`tools/render.py`), so a release is cut by tagging alone and the copies cannot
drift out of agreement the way three hand-edited files could.

Resolution order:

  1. $VERSION / $DATE          explicit override, for CI or a build outside a
                               checkout (a source tarball has no git history)
  2. the tag on HEAD           `vX.Y.Z` -> `X.Y.Z`, dated by HEAD's commit date
  3. anything else             a dev version: `<last tag>-dev.<n>+g<sha>`, or
                               `0.0.0-dev` with no tags at all

A dirty working tree is always a dev version, even on a tagged commit: what is
in the tree is not what the tag names. `make deploy` publishes release versions
only (override with ALLOW_DEV=1), so a dev build cannot reach the live site.

CLI: prints "<version> <date>", or just one with --version / --date.
"""

import os
import re
import subprocess
import sys
from datetime import date as _date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# A release is plain semver; dev versions carry a pre-release/build suffix, which
# is what is_release() keys on.
RELEASE_RE = re.compile(r"\d+\.\d+\.\d+")
VERSION_RE = re.compile(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.]+)?(?:\+[0-9A-Za-z.]+)?")
DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
# `git describe` on an untagged commit: <tag>-<commits since>-g<sha>[-dirty]
DESCRIBE_RE = re.compile(r"v?(\d+\.\d+\.\d+)-(\d+)-g([0-9a-f]+)(-dirty)?\Z")


def _git(*args):
    """Run a git command in the repo; None if git is absent or the command fails."""
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *args],
                           capture_output=True, text=True)
    except OSError:
        return None
    return r.stdout.strip() if r.returncode == 0 else None


def is_release(version):
    return bool(RELEASE_RE.fullmatch(version))


def resolve():
    """Return (version, date, source) — source is a human-readable provenance."""
    env_version = os.environ.get("VERSION", "").strip()
    env_date = os.environ.get("DATE", "").strip()

    if env_version:
        version, source = env_version, "$VERSION"
    else:
        dirty = bool(_git("status", "--porcelain"))
        tag = _git("describe", "--exact-match", "--tags", "HEAD")
        if tag and not dirty:
            version, source = tag.lstrip("v"), f"git tag {tag}"
        else:
            desc = _git("describe", "--tags", "--always") or ""
            m = DESCRIBE_RE.match(desc)
            if m:
                version = f"{m.group(1)}-dev.{m.group(2)}+g{m.group(3)}"
            elif tag:  # tagged but dirty: name the tag it departs from
                version = f"{tag.lstrip('v')}-dev+dirty"
            else:
                version = f"0.0.0-dev+g{desc}" if desc else "0.0.0-dev"
            if dirty:
                version += ".dirty"
            source = "git describe (untagged/dirty working tree)"

    date = env_date or _git("log", "-1", "--format=%cs") or _date.today().isoformat()
    if env_date:
        source += " + $DATE"

    if not VERSION_RE.fullmatch(version):
        sys.exit(f"version: resolved version {version!r} is not semver ({source})")
    if not DATE_RE.fullmatch(date):
        sys.exit(f"version: resolved date {date!r} is not YYYY-MM-DD")
    return version, date, source


if __name__ == "__main__":
    v, d, _ = resolve()
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    print(v if arg == "--version" else d if arg == "--date" else f"{v} {d}")
