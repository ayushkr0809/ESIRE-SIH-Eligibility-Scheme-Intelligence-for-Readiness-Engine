from __future__ import annotations

from typing import Any

from app.config import get_settings

settings = get_settings()
graph_mode = "memory"
_driver = None

_nodes: dict[str, dict[str, Any]] = {}
_edges: list[tuple[str, str, str, dict[str, Any]]] = []


def _node_key(label: str, node_id: str) -> str:
    return f"{label}:{node_id}"


def init_neo4j() -> str:
    global _driver, graph_mode
    try:
        from neo4j import GraphDatabase

        driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
        driver.verify_connectivity()
        _driver = driver
        graph_mode = "neo4j"
        return graph_mode
    except Exception:
        if not settings.allow_inmemory_fallback:
            raise
        graph_mode = "memory"
        return graph_mode


def reset_memory() -> None:
    _nodes.clear()
    _edges.clear()


def merge_node(label: str, node_id: str, props: dict[str, Any] | None = None) -> None:
    properties = {"id": node_id, **(props or {})}
    if _driver is not None:
        query = f"MERGE (n:{label} {{id: $id}}) SET n += $props"
        with _driver.session() as session:
            session.run(query, id=node_id, props=properties)
        return
    _nodes[_node_key(label, node_id)] = {"label": label, **properties}


def merge_rel(from_label: str, from_id: str, rel: str, to_label: str, to_id: str, props: dict[str, Any] | None = None) -> None:
    if _driver is not None:
        query = (
            f"MERGE (a:{from_label} {{id: $from_id}}) "
            f"MERGE (b:{to_label} {{id: $to_id}}) "
            f"MERGE (a)-[r:{rel}]->(b) SET r += $props"
        )
        with _driver.session() as session:
            session.run(query, from_id=from_id, to_id=to_id, props=props or {})
        return
    merge_node(from_label, from_id)
    merge_node(to_label, to_id)
    _edges.append((_node_key(from_label, from_id), rel, _node_key(to_label, to_id), props or {}))


def related_scheme_ids(profile: dict[str, Any]) -> list[str]:
    groups = []
    if profile.get("occupation_type"):
        groups.append(str(profile["occupation_type"]))
    if profile.get("category"):
        groups.append(str(profile["category"]))
    if profile.get("gender") == "female":
        groups.append("woman")
    if profile.get("is_entrepreneur"):
        groups.append("entrepreneur")
    groups.append("citizen")
    locations = ["India"]
    if profile.get("state"):
        locations.append(str(profile["state"]))

    if _driver is not None:
        query = """
        MATCH (s:Scheme)
        OPTIONAL MATCH (s)-[:TARGETS_GROUP]->(g:Group)
        OPTIONAL MATCH (s)-[:AVAILABLE_IN]->(l:Location)
        WITH s, collect(DISTINCT g.id) AS groups, collect(DISTINCT l.id) AS locations
        WHERE any(x IN groups WHERE x IN $groups)
           OR any(x IN locations WHERE x IN $locations)
           OR size(groups) = 0
        RETURN DISTINCT s.id AS id
        """
        with _driver.session() as session:
            result = session.run(query, groups=groups, locations=locations)
            return [record["id"] for record in result]

    scheme_ids = set()
    for start, rel, end, _ in _edges:
        if rel == "TARGETS_GROUP" and start.startswith("Scheme:"):
            group_id = end.split(":", 1)[1]
            if group_id in groups:
                scheme_ids.add(start.split(":", 1)[1])
        if rel == "AVAILABLE_IN" and start.startswith("Scheme:"):
            loc_id = end.split(":", 1)[1]
            if loc_id in locations:
                scheme_ids.add(start.split(":", 1)[1])
    return list(scheme_ids)
