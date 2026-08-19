#!/usr/bin/env python3
"""Generate litmus.json from the litmus/ test tree.

The litmus tests live in litmus/{strictly-weaker,incomparable}/<A-vs-B>/, with
one or more test files plus a README.md per pair. They are not deployed as raw
files; instead this script bakes their contents into a single JSON the site
fetches alongside models.json. Run via `make litmus` (also a dependency of
`make build`). The output is committed so a consumer of this repo has the
built artifact without having to run the generator.

The kater queries in litmus/kater/queries/ are baked in the same way, under a
separate "kater" list: they are proofs, not witnesses, and the site labels them
as such. A kater-only edge (a compilation edge, say, which has no witness
directory) still gets an entry, with an empty "tests".

Output shape, keyed by "<from>|<to>" (matching models.json edge endpoints):

    { "SC|TSO": {
        "relationship": "strictly-weaker",
        "summary": "<first prose paragraph of the pair's README.md>",
        "tests": [ { "name": "SB", "file": "SB.litmus", "lang": "smrd",
                     "code": "<verbatim file contents>" } ],
        "kater": [ { "name": "strictly-weaker-SC-vs-TSO", "file": "...kat",
                     "lang": "none", "summary": "<the query's header comment>",
                     "code": "<verbatim file contents>" } ] } }
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LITMUS_DIR = ROOT / "litmus"
MODELS_JSON = ROOT / "models.json"
OUT_JSON = ROOT / "litmus.json"

# Relationship sub-trees that contain per-pair test directories.
RELATIONSHIPS = ["strictly-weaker", "incomparable"]

# The kater queries: one per edge with provenance "kater", named for it.
KATER_DIR = LITMUS_DIR / "kater" / "queries"
KATER_TYPES = ["strictly-weaker", "incomparable", "equivalent", "compilation"]

# File extension -> Prism language. ".lit" is sMRD/MoRDor and ".litmus" is
# herd7 assembly; both use the bundled `smrd` grammar (its own alias is
# `litmus`). ".cat" has no grammar -> plain. Unknown extensions -> plain.
TEST_EXTS = {
    ".lit": "smrd",
    ".litmus": "smrd",
    ".java": "java",
    ".ml": "ocaml",
    ".cat": "none",
}


def model_ids():
    data = json.loads(MODELS_JSON.read_text())
    return {m["id"] for m in data["models"]}


def split_pair(dirname):
    """'SC-vs-x86-TSO' -> ('SC', 'x86-TSO'). All pair dirs use a '-vs-' marker."""
    if "-vs-" not in dirname:
        return None
    a, b = dirname.split("-vs-", 1)
    return a, b


def test_name(filename):
    """Strip one trailing known extension; keep any middle variant suffix."""
    for ext in TEST_EXTS:
        if filename.endswith(ext):
            return filename[: -len(ext)]
    return filename


def header_summary(kat_path):
    """The prose of a query's leading `//` comment block, minus the filing line.

    Every query opens with a comment naming the edge it backs and the claim it
    states; that is exactly the one-line summary the viewer wants, and keeping it
    in the file rather than in a sidecar means it cannot drift from the query.
    """
    lines = []
    for line in kat_path.read_text().splitlines():
        st = line.strip()
        if not st.startswith("//"):
            break
        lines.append(st.lstrip("/").strip())
    text = " ".join(l for l in lines if l)
    return re.sub(r"\s+", " ", text).strip()


def readme_summary(readme_path):
    """First prose paragraph: skip the H1 heading and fenced code blocks,
    collapse whitespace, and strip basic markdown emphasis markers."""
    if not readme_path.exists():
        return ""
    text = readme_path.read_text()
    blocks = re.split(r"\n\s*\n", text.strip())
    for block in blocks:
        b = block.strip()
        if not b or b[0] in "#>" or b.startswith("```"):
            continue
        b = re.sub(r"\s+", " ", b)            # collapse internal newlines/runs
        b = re.sub(r"[`*_]", "", b)           # drop emphasis / inline-code marks
        return b.strip()
    return ""


def kater_queries(ids, warnings):
    """litmus/kater/queries/<type>-<from>-vs-<to>.kat -> {"<from>|<to>": [entry]}.

    The file name is the edge, so the mapping needs no separate index — and a
    query that names a model or a relationship the data does not have shows up
    here as a warning rather than as a silently unlinked file.
    """
    out = {}
    if not KATER_DIR.is_dir():
        return out
    for f in sorted(KATER_DIR.glob("*.kat")):
        stem = f.stem
        rel = next((r for r in KATER_TYPES if stem.startswith(r + "-")), None)
        if not rel:
            warnings.append(f"kater query with no known edge type: {f.name}")
            continue
        pair = split_pair(stem[len(rel) + 1:])
        if not pair:
            warnings.append(f"kater query name has no '-vs-': {f.name}")
            continue
        frm, to = pair
        for endpoint in (frm, to):
            if endpoint not in ids:
                warnings.append(f"unknown model id '{endpoint}' in kater/{f.name}")
        out.setdefault(f"{frm}|{to}", []).append({
            "name": stem,
            "file": f.name,
            "lang": "none",
            "relationship": rel,
            "summary": header_summary(f),
            "code": f.read_text(),
        })
    return out


def main():
    ids = model_ids()
    out = {}
    warnings = []

    for rel in RELATIONSHIPS:
        rel_dir = LITMUS_DIR / rel
        if not rel_dir.is_dir():
            continue
        for pair_dir in sorted(p for p in rel_dir.iterdir() if p.is_dir()):
            pair = split_pair(pair_dir.name)
            if not pair:
                warnings.append(f"skip (no '-vs-'): {rel}/{pair_dir.name}")
                continue
            frm, to = pair
            for endpoint in (frm, to):
                if endpoint not in ids:
                    warnings.append(
                        f"unknown model id '{endpoint}' in {rel}/{pair_dir.name}"
                    )

            tests = []
            for f in sorted(pair_dir.iterdir()):
                if not f.is_file() or f.name == "README.md":
                    continue
                ext = f.suffix
                if ext not in TEST_EXTS:
                    warnings.append(f"unhandled extension: {rel}/{pair_dir.name}/{f.name}")
                    continue
                tests.append({
                    "name": test_name(f.name),
                    "file": f.name,
                    "lang": TEST_EXTS[ext],
                    "code": f.read_text(),
                })

            if not tests:
                warnings.append(f"no test files: {rel}/{pair_dir.name}")
                continue

            out[f"{frm}|{to}"] = {
                "relationship": rel,
                "summary": readme_summary(pair_dir / "README.md"),
                "tests": tests,
            }

    # kater queries: attached to the pair they prove, or standing on their own
    # for an edge with no witness directory (every compilation edge, and any
    # ordering edge whose witness is still owed).
    for key, queries in kater_queries(ids, warnings).items():
        if key in out:
            out[key]["kater"] = queries
        else:
            out[key] = {
                "relationship": queries[0]["relationship"],
                "summary": "",
                "tests": [],
                "kater": queries,
            }

    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)}: {len(out)} pairs, "
          f"{sum(len(v['tests']) for v in out.values())} tests, "
          f"{sum(len(v.get('kater', [])) for v in out.values())} kater queries")
    for w in warnings:
        print(f"  warning: {w}", file=sys.stderr)


if __name__ == "__main__":
    main()
