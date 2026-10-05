#!/usr/bin/env python3
"""SUB-2 detector: report `return` statements under a src/ tree whose value is, or is a tuple starting with,
the string "ALLOW", "DEFER" or "REFUSE". A tripwire for one way of writing a decision rule, not a proof that
a package holds no policy (docs/SUB2_PREREG.md).

  python tools/sub2_no_rules.py [SRC_DIR]     prints one line per hit and a count; exit 1 if any hit
"""
import ast
import pathlib
import sys

OUTCOMES = {"ALLOW", "DEFER", "REFUSE"}


def hits(src_dir):
    out = []
    for path in sorted(pathlib.Path(src_dir).rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Return) or node.value is None:
                continue
            v = node.value
            first = v.elts[0] if isinstance(v, ast.Tuple) and v.elts else v
            if isinstance(first, ast.Constant) and first.value in OUTCOMES:
                out.append((path.relative_to(src_dir).as_posix(), node.lineno, first.value))
    return out


if __name__ == "__main__":
    d = sys.argv[1] if len(sys.argv) > 1 else str(pathlib.Path(__file__).resolve().parents[1] / "src")
    h = hits(d)
    for f, line, val in h:
        print(f"{f}:{line} returns {val}")
    print(f"{len(h)} decision-rule returns under {d}")
    sys.exit(1 if h else 0)
