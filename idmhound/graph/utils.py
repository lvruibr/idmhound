# -*- coding:utf -*-

import re
import json


def member_lookup(principals: list, subjects: list):
    """Convert the DN of an account to its SID for graphing.
    :param principals: principals to resolve the DN.
    :param subjects: subjects whose DN should be resolved."""

    for subject in subjects:
        subject.resolve_member_dn(principals)


def to_json(data: list, object_type) -> dict:
    """Convert objects to legacy JSON file format.
    :param data: list of objects to convert.
    :param object_type: type of the objects to convert.
    :return: legacy JSON containing the converted objects."""

    data = [entry.to_json() for entry in data]
    return {"data": data, "meta": {
        "methods": 0,
        "type": object_type,
        "count": len(data), "version": 5
    }}


def to_opengraph(nodes: list, edges: list) -> dict:
    """Convert objects to Opengraph file format.
    :param nodes: nodes to convert.
    :param edges: edges to convert.
    :return: Opengraph JSON containing the converted objects."""

    formatted_nodes = [node.to_json() for node in nodes]
    formatted_edges = []
    for edge in edges:
        formatted_edges.extend(edge.to_json())
    return {"metadata": {"source_kind": "IDMHound"}, "graph": {"nodes": formatted_nodes, "edges": formatted_edges}}


def to_opengraph_hbac(data: list) -> dict:
    """Convert HBAC to Opengraph file format.
    :param data: list of HBAC.
    :return: Opengraph JSON containing the converted HBAC."""

    opengraph = []
    for entry in data:
        opengraph.extend(entry.to_json())
    return {"graph": {"nodes": [], "edges": opengraph}}


def identify_realm_sid(data: list, realm: str) -> str:
    """Identify the SID of the realm.
    :param data: list of LDAP entry to parse.
    :param realm: name of the realm.
    :return: SID of the realm."""

    for entry in data:
        if re.match(f"cn={realm},cn=ad,cn=etc,dc=lab,dc=lo", entry.entry_dn):
            sid = str(entry["ipaNTSecurityIdentifier"])
            return sid
    else:
        raise ValueError("Cannot identify realm SID.")


def legacy_save(domains, users, groups, computers, hbac):
    """Save data in the legacy file format.
    :param domains: domains in legacy JSON format.
    :param users: users in legacy JSON format.
    :param groups: groups in legacy JSON format.
    :param computers: computers in legacy JSON format.
    :param hbac: HBAC in Opengraph format."""

    with open("domains.json", "w") as output:
        output.write(json.dumps(to_json(domains, "domains")))
    with open("users.json", "w") as output:
        output.write(json.dumps(to_json(users, "users")))
    with open("groups.json", "w") as output:
        output.write(json.dumps(to_json(groups, "groups")))
    with open("computers.json", "w") as output:
        output.write(json.dumps(to_json(computers, "computers")))
    with open("hbac.json", "w") as output:
        output.write(json.dumps(to_opengraph_hbac(hbac)))
