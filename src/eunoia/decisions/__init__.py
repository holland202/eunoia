"""Decision and its record: every dependency is an explicit, content-addressed node (E8)."""
from __future__ import annotations

from typing import Any

from .._canon import content_id

SCHEMA = "eunoia.decision/0"
ROOT = "@decision"


class Decision:
    """ALLOW / DEFER / REFUSE with ordered reasons and a deterministic record. Executes nothing (E6)."""

    __slots__ = ("decision", "reasons", "record")

    def __init__(self, decision: str, reasons: tuple[str, ...], record: dict[str, Any]) -> None:
        object.__setattr__(self, "decision", decision)
        object.__setattr__(self, "reasons", reasons)
        object.__setattr__(self, "record", record)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Decision is immutable")

    @property
    def id(self) -> str:
        return self.record["id"]

    def __repr__(self) -> str:
        return f"Decision({self.decision}, {list(self.reasons)})"


def _add_evidence(e, nodes: dict, edges: list) -> None:
    if e.id in nodes:
        return
    nodes[e.id] = e.to_dict()
    if e.observation is not None:
        nodes[e.observation.id] = e.observation.to_dict()
        edges.append([e.id, "DERIVED_FROM", e.observation.id])
    for p in e.derived_from:
        edges.append([e.id, "DERIVED_FROM", p.id])
        _add_evidence(p, nodes, edges)


def build_record(*, verdict, reasons, action, at, claim, authorization, results, valid_evidence,
                 independent_roots) -> dict[str, Any]:
    nodes: dict[str, Any] = {}
    edges: list[list[str]] = []
    if claim is not None:
        nodes[claim.id] = claim.to_dict()
        edges.append([ROOT, "DEPENDS_ON", claim.id])
        for e in claim.evidence:
            edges.append([claim.id, "DEPENDS_ON", e.id])
            _add_evidence(e, nodes, edges)
    if authorization is not None:
        nodes[authorization.id] = authorization.to_dict()
        edges.append([ROOT, "AUTHORIZED_BY", authorization.id])
        if claim is not None and authorization.claim_id == claim.id:
            edges.append([authorization.id, "DEPENDS_ON", claim.id])
    for r in results:
        nodes[r.id] = r.to_dict()
        edges.append([ROOT, "DEPENDS_ON", r.id])
        edges.append([r.id, "ATTESTS", r.claim_id])
    record = {
        "schema": SCHEMA,
        "decision": verdict,
        "reasons": list(reasons),
        "action": action if isinstance(action, str) else repr(action),
        "at": at if isinstance(at, int) and not isinstance(at, bool) else repr(at),
        "valid_evidence": sorted(valid_evidence),
        "independent_roots": independent_roots,
        "nodes": nodes,
        "edges": sorted(edges),
    }
    record["id"] = content_id(record)
    return record


def check_record(record: dict[str, Any]) -> list[str]:
    """Problems found in a decision record, recomputed from the record alone: every node's id from
    its content, every edge endpoint defined, no cycle, and the record's own id. Same author as
    build_record, so this is a consistency check, not independent verification."""
    problems = []
    nodes = record.get("nodes", {})
    for nid, content in nodes.items():
        if content_id(content) != nid:
            problems.append(f"node {nid[:12]} content does not hash to its id")
    adj: dict[str, list[str]] = {}
    for src, rel, dst in record.get("edges", []):
        for end in (src, dst):
            if end != ROOT and end not in nodes:
                problems.append(f"edge {rel} references undefined {end[:12]}")
        adj.setdefault(src, []).append(dst)
    state: dict[str, int] = {}

    def cyclic(n: str) -> bool:
        state[n] = 1
        for m in adj.get(n, []):
            if state.get(m) == 1 or (state.get(m) is None and cyclic(m)):
                return True
        state[n] = 2
        return False

    if any(state.get(n) is None and cyclic(n) for n in list(adj)):
        problems.append("dependency graph has a cycle")
    body = {k: v for k, v in record.items() if k != "id"}
    if content_id(body) != record.get("id"):
        problems.append("record id does not match its content")
    return problems
