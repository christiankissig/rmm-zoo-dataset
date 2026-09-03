#!/usr/bin/env python3
"""Assemble models.json from the per-entity sources under src/.

models.json is the artifact the site fetches — one JSON with the whole zoo in
it. It is no longer the thing you edit. The dataset lives in src/ as one file
per entity, so that changing a model touches that model's file and changing an
edge touches that edge's file, and two contributors working on different corners
of the zoo do not collide in a 4000-line file:

    src/dataset.json          the prose header and the block comments
    src/properties.json       the property table's schema + per-column provenance
    src/references.json       the bibliography, keyed by citation id
    src/models/<id>.json      one model: its entry, property vector, provenance,
                              per-cell citations, cat- and kat-specifiability
    src/models/_order.txt     the curated strength order the models list is in
    src/edges/<from>-vs-<to>.json   one edge

Everything a model asserts is in its own file, including the blocks that
models.json publishes as separate id-keyed maps (modelProperties, catSupport,
...): those maps are assembled here, in model order, from the per-model files.
The pair-named edge files follow the litmus/ tree's `<A>-vs-<B>` convention, so
an edge, its witness directory and its kater query are all found under the same
name.

Run via `make models` (and `make check`, which re-runs this in --check mode and
fails if the committed models.json is stale). Like litmus.json, the output is
committed: a consumer of this repo gets the built dataset without running the
build.

This script checks SHAPE only — that files are where they say they are, and
carry the fields they must. What the data MEANS (the DAG, contradictions,
witness coverage) is tools/check-consistency.py's business.

Usage: gen-models.py [--check]
  --check   do not write; exit non-zero if models.json differs from the sources.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from jsonfmt import dumps  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
OUT = ROOT / "models.json"

# The version and date are stamped in at build time from the git tag; nothing in
# the source tree carries them (tools/version.py, tools/render.py).
PLACEHOLDERS = {"version": "@VERSION@", "date": "@DATE@"}

# A model's descriptive entry, in the order it is published. "formalism" is the
# one optional field; the rest are required of every model.
MODEL_FIELDS = ["id", "name", "abbrev", "year", "authors", "description",
                "references", "tags", "formalism", "hardware", "languages"]
MODEL_OPTIONAL = {"formalism"}
# The rest of a model's file: per-model key -> the id-keyed block it feeds in
# models.json. All optional here; check-consistency.py is what insists a model
# has a property vector and a cat-specifiability entry.
MODEL_BLOCKS = {
    "properties": "modelProperties",
    "propertyProvenance": "modelPropertyProvenance",
    "propertyCitations": "modelPropertyCitations",
    "catSupport": "catSupport",
    "katSupport": "katSupport",
}

EDGE_FIELDS = ["from", "to", "type", "provenance", "evidence",
               "fragment_restricted", "note"]
EDGE_OPTIONAL = {"fragment_restricted"}

# The two hand-written shared files, and the fields they own. Both are published
# verbatim; the leading "_" ones are the prose models.json carries about itself.
DATASET_FIELDS = ["_comment", "_modelPropertyCitationsComment",
                  "_catSupportComment", "_katSupportComment"]
PROPERTY_FIELDS = ["_propertySchemaComment", "propertySchema",
                   "_propertyProvenanceComment", "propertyProvenance"]

errors = []
warnings = []


def err(msg):
    errors.append(msg)


def load(path):
    """Parse a source file, reporting a bad path or bad JSON as a shape error."""
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        err(f"missing source file: {path.relative_to(ROOT)}")
    except json.JSONDecodeError as e:
        err(f"{path.relative_to(ROOT)}: invalid JSON: {e}")
    return None


def check_fields(where, obj, fields, optional):
    """Every declared field present (bar the optional ones), and no others.

    Rejecting unknown keys is the point: a typo'd "formalisms" would otherwise
    be silently dropped from the published dataset with nothing to notice it.
    """
    if not isinstance(obj, dict):
        err(f"{where}: expected a JSON object, got {type(obj).__name__}")
        return
    for f in fields:
        if f not in obj and f not in optional:
            err(f"{where}: missing required field '{f}'")
    for k in obj:
        if k not in fields:
            err(f"{where}: unknown field '{k}' (expected one of {', '.join(fields)})")


def ordered(obj, fields):
    """The object's fields in published order, skipping absent optional ones."""
    return {f: obj[f] for f in fields if f in obj}


def read_order():
    """The curated strength order: one model id per line, '#' comments allowed.

    models.json's own header says the models are ordered by strength, so that
    order is data, not an artefact of how the file was typed — it lives here
    rather than being implied by a directory listing.
    """
    path = SRC / "models" / "_order.txt"
    if not path.exists():
        err(f"missing source file: {path.relative_to(ROOT)}")
        return []
    order, seen = [], set()
    for n, line in enumerate(path.read_text().splitlines(), 1):
        mid = line.split("#", 1)[0].strip()
        if not mid:
            continue
        if mid in seen:
            err(f"models/_order.txt:{n}: '{mid}' listed twice")
            continue
        seen.add(mid)
        order.append(mid)
    return order


def read_models():
    """{id: file contents} for src/models/*.json, filename == id."""
    out = {}
    for path in sorted((SRC / "models").glob("*.json")):
        m = load(path)
        if m is None:
            continue
        where = f"models/{path.name}"
        check_fields(where, m, MODEL_FIELDS + list(MODEL_BLOCKS),
                     MODEL_OPTIONAL | set(MODEL_BLOCKS))
        if m.get("id") != path.stem:
            err(f"{where}: id {m.get('id')!r} does not match the filename "
                f"(a model file is named for its id)")
            continue
        out[path.stem] = m
    return out


def read_edges():
    """Edge files in filename order, which is the order they are published in.

    Unlike the models, the edge list has no meaning in its order, so the
    directory listing is the order — no index to keep in step.
    """
    out = []
    for path in sorted((SRC / "edges").glob("*.json")):
        e = load(path)
        if e is None:
            continue
        where = f"edges/{path.name}"
        check_fields(where, e, EDGE_FIELDS, EDGE_OPTIONAL)
        if {"from", "to"} <= set(e):
            expected = f"{e['from']}-vs-{e['to']}.json"
            if path.name != expected:
                err(f"{where}: edge {e['from']} -> {e['to']} belongs in {expected}")
                continue
        out.append(e)
    return out


def build():
    dataset = load(SRC / "dataset.json") or {}
    check_fields("dataset.json", dataset, DATASET_FIELDS, set())
    props = load(SRC / "properties.json") or {}
    check_fields("properties.json", props, PROPERTY_FIELDS, set())
    references = load(SRC / "references.json") or {}

    models = read_models()
    edges = read_edges()
    order = read_order()

    for mid in order:
        if mid not in models:
            err(f"models/_order.txt: '{mid}' has no src/models/{mid}.json")
    # A model whose file exists but which nobody placed still ships — at the end
    # of the list, where its absence from the strength order is obvious — rather
    # than being dropped or blocking the build.
    unplaced = sorted(set(models) - set(order))
    for mid in unplaced:
        warnings.append(f"{mid} is not in models/_order.txt; appended at the end")
    ids = [mid for mid in order if mid in models] + unplaced

    for e in edges:
        for ep in (e.get("from"), e.get("to")):
            if ep is not None and ep not in models:
                err(f"edges/{e.get('from')}-vs-{e.get('to')}.json: endpoint "
                    f"'{ep}' has no src/models/{ep}.json")
    seen_pairs = {}
    for e in edges:
        pair = frozenset((e.get("from"), e.get("to")))
        if pair in seen_pairs:
            err(f"two edges relate the same pair: {seen_pairs[pair]} and "
                f"{e.get('from')}-vs-{e.get('to')} (one edge per pair)")
        seen_pairs[pair] = f"{e.get('from')}-vs-{e.get('to')}"

    # The id-keyed blocks, gathered from the per-model files in model order.
    blocks = {name: {} for name in MODEL_BLOCKS.values()}
    for mid in ids:
        for key, block in MODEL_BLOCKS.items():
            if key in models[mid]:
                blocks[block][mid] = models[mid][key]

    return {
        "_comment": dataset.get("_comment"),
        **PLACEHOLDERS,
        "models": [ordered(models[mid], MODEL_FIELDS) for mid in ids],
        "edges": [ordered(e, EDGE_FIELDS) for e in edges],
        "references": references,
        "_propertySchemaComment": props.get("_propertySchemaComment"),
        "propertySchema": props.get("propertySchema"),
        "modelProperties": blocks["modelProperties"],
        "modelPropertyProvenance": blocks["modelPropertyProvenance"],
        "_propertyProvenanceComment": props.get("_propertyProvenanceComment"),
        "propertyProvenance": props.get("propertyProvenance"),
        "_modelPropertyCitationsComment": dataset.get("_modelPropertyCitationsComment"),
        "modelPropertyCitations": blocks["modelPropertyCitations"],
        "_catSupportComment": dataset.get("_catSupportComment"),
        "catSupport": blocks["catSupport"],
        "_katSupportComment": dataset.get("_katSupportComment"),
        "katSupport": blocks["katSupport"],
    }


def main():
    check_only = "--check" in sys.argv[1:]
    data = build()
    for w in warnings:
        print(f"gen-models: warning: {w}", file=sys.stderr)
    if errors:
        for e in errors:
            print(f"gen-models: error: {e}", file=sys.stderr)
        sys.exit(f"gen-models: {len(errors)} error(s) in src/; models.json not written")

    text = dumps(data)

    if check_only:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            sys.exit(f"gen-models: {OUT.name} is stale — it does not match src/.\n"
                     f"            Run `make models` and commit the result.")
        print(f"gen-models: {OUT.name} is up to date with src/")
    else:
        OUT.write_text(text)
        print(f"gen-models: wrote {OUT.relative_to(ROOT)}: {len(data['models'])} models, "
              f"{len(data['edges'])} edges, {len(data['references'])} references")


if __name__ == "__main__":
    main()
