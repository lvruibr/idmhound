# -*- coding:utf -*-

import re
import json
def member_lookup(principals: list, subjects: list):
    for subject in subjects:
        subject.resolve_member_dn(principals)




def to_json(data: list, object_type) -> dict:
    data = [entry.to_json() for entry in data]
    return {"data": data, "meta": {
        "methods": 0,
        "type": object_type,
        "count": len(data), "version": 5
    }}

def to_opengraph(data: list) -> dict:
    opengraph = []
    for entry in data:
        opengraph.extend(entry.to_json())
    return {"graph": {"nodes": [],"edges": opengraph}}


def identify_realm_sid(data: list, realm: str) -> str:

    for entry in data:
        if re.match(f"cn={realm},cn=ad,cn=etc,dc=lab,dc=lo", entry.entry_dn):
            sid = str(entry["ipaNTSecurityIdentifier"])
            return sid
    else:
        raise ValueError("Cannot identify realm SID.")

def legacy_save(domains, users, groups, computers):

    with open("domains.json", "w") as output:
        output.write(json.dumps(to_json(domains, "domains")))
    with open("users.json", "w") as output:
        output.write(json.dumps(to_json(users, "users")))
    with open("groups.json", "w") as output:
        output.write(json.dumps(to_json(groups, "groups")))
    with open("computers.json", "w") as output:
        output.write(json.dumps(to_json(computers, "computers")))