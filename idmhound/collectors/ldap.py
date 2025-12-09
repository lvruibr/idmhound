# -*- coding:utf-8 -*-

import re
from idmhound.graph.nodes import *
from ldap3 import Server, Connection, ALL, SUBTREE


def collect(server: str, username: str, password: str, base: str) -> list:

    server = Server(server, get_info=ALL)
    conn = Connection(server, user=username, password=password)
    conn.bind()

    conn.search(search_base=base, search_filter="(objectClass=*)", search_scope=SUBTREE, attributes=["*"])
    data = conn.entries
    conn.unbind()

    return data

def parse(raw, realm, sid):
    ldap_realm = "".join([",dc=" + dc for dc in realm.split(".")])
    domains, users, groups, computers = [], [], [], []
    num_objects = len(raw) + 1000
    for index, entry in enumerate(raw):
        dn = entry.entry_dn
        realm_object = None
        if re.match(f"cn=.+,cn=ad,cn=etc,dc=lab,dc=lo", dn):
            realm_object = Domain(dn, entry["cn"], entry["ipaNTDomainGUID"], entry["ipaNTFlatName"], entry["ipaNTSecurityIdentifier"])
            domains.append(realm_object)
        elif re.match(f"uid=.+,cn=users,cn=accounts{ldap_realm}", dn):
            realm_object = User(dn, entry["cn"], entry["gecos"], entry["homeDirectory"], entry["ipaUniqueID"],
                                entry["ipaNTSecurityIdentifier"], entry["krbCanonicalName"], entry["krbPrincipalName"],
                                entry["loginShell"], entry["sn"], entry["uid"], entry["uidNumber"])
            users.append(realm_object)
        elif re.match(f"cn=.+,cn=groups,cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["cn","ipaUniqueID", "ipaNTSecurityIdentifier", "member"]):
            realm_object = Group(dn, entry["cn"], entry["ipaUniqueID"], entry["ipaNTSecurityIdentifier"], entry["member"])
            groups.append(realm_object)
        elif re.match(f"cn=.+,cn=(hostgroups|groups),cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["cn", "ipaUniqueID", "member"]):
            realm_object = Group(dn, entry["cn"], entry["ipaUniqueID"], sid+"-"+str(num_objects+index), entry["member"])
            groups.append(realm_object)
        elif re.match(f"fqdn=.+,cn=computers,cn=accounts{ldap_realm}", dn) and all(attr in entry.entry_attributes_as_dict.keys() for attr in ["cn", "ipaUniqueID", "krbCanonicalName", "krbPrincipalName", "fqdn"]):
            realm_object = Computer(dn, entry["cn"], entry["ipaUniqueID"], sid+"-"+str(num_objects+index), entry["krbCanonicalName"],
                                    entry["krbPrincipalName"], entry["fqdn"])
            computers.append(realm_object)

        if realm_object is not None and "description" in entry.entry_attributes_as_dict.keys():
            realm_object.set_desc(entry["description"])

    return domains, users, groups, computers

if __name__ == "__main__":
    pass