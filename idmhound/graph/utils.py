# -*- coding:utf -*-
import re

def group_member_lookup(users: list, computers: list, groups: list):
    for group in groups:
        group.resolve_member_dn(users+computers)


def to_json(data: list, object_type) -> dict:
    data = [entry.to_json() for entry in data]
    return {"data": data, "meta": {
        "methods": 0,
        "type": object_type,
        "count": len(data), "version": 5
    }}

def identify_realm_sid(data: list, realm: str) -> str:

    for entry in data:
        if re.match(f"cn={realm},cn=ad,cn=etc,dc=lab,dc=lo", entry.entry_dn):
            sid = str(entry["ipaNTSecurityIdentifier"])
            return sid
    else:
        raise ValueError("Cannot identify realm SID.")

