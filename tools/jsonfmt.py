#!/usr/bin/env python3
"""JSON serialisation in this repository's house style.

`json.dumps(indent=2)` puts every scalar in an array on its own line, which
turns `"authors": ["Owens", "Sarkar", "Sewell"]` into four lines and a property
vector into thirty. The dataset was hand-written in a more compact style, and
generating it should not lose that: the files stay readable, and a diff still
shows one line per thing that changed.

Two rules, which between them reproduce the style models.json was written in:

  * an array of scalars is written on one line;
  * an object all of whose values are scalars is written on one line, unless it
    is an element of an array — the entries in a list (a model, an edge) are the
    unit a reader reads, so they keep one field per line.

Everything else is block-formatted with a two-space indent, and so is the
document root: a whole file on one line is nobody's idea of readable, however
few fields the thing has.
"""
import json

SCALARS = (str, int, float, bool, type(None))


def _scalar(v):
    return isinstance(v, SCALARS)


def _inline(value):
    return json.dumps(value, ensure_ascii=False, separators=(", ", ": "))


def _render(value, depth, in_list):
    pad, inner = "  " * depth, "  " * (depth + 1)

    if isinstance(value, list):
        if not value:
            return "[]"
        if all(_scalar(v) for v in value):
            return _inline(value)
        items = [inner + _render(v, depth + 1, True) for v in value]
        return "[\n" + ",\n".join(items) + "\n" + pad + "]"

    if isinstance(value, dict):
        if not value:
            return "{}"
        if not in_list and all(_scalar(v) for v in value.values()):
            return _inline(value)
        items = [f"{inner}{json.dumps(k, ensure_ascii=False)}: "
                 f"{_render(v, depth + 1, False)}" for k, v in value.items()]
        return "{\n" + ",\n".join(items) + "\n" + pad + "}"

    return _inline(value)


def dumps(value):
    """Serialise `value`, newline-terminated, in the style described above."""
    return _render(value, 0, True) + "\n"
