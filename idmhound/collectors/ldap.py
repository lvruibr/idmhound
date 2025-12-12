# -*- coding:utf-8 -*-

import re
import logging
import ldap3.abstract.entry
from idmhound.graph.nodes import *
from idmhound.graph.legacy_nodes import *
from idmhound.graph.edges import *
from idmhound.graph.utils import *
from ldap3 import Server, Connection, ALL, SUBTREE

logger = logging.getLogger()

def collect(server: str, username: str, password: str, base: str) -> list:
    """Collect data by performing an LDAP query.
    :param server: server to connect to.
    :param username: username to use in the LDAP bind, leave empty for anonymous bind.
    :param password: password to use in the LDAP bind, leave empty for anonymouse bind.
    :param base: base of the LDAP request, leave empty to get all data.
    :return list: list of LDAP entries."""

    server = Server(server, get_info=ALL)
    conn = Connection(server, user=username, password=password)
    conn.bind()

    conn.search(search_base=base, search_filter="(objectClass=*)", search_scope=SUBTREE, attributes=["*"])
    data = conn.entries
    conn.unbind()

    return data


def parse(raw: list, realm: str, sid: str) -> tuple:
    """Parse LDAP data for use in the Opengraph file format.
    :param raw: list of LDAP entries.
    :param realm: name of the realm.
    :param sid: SID of the realm.
    :return: tuple of domains, users, groups, computers, hbac and membership."""

    ldap_realm = "".join([",dc=" + dc for dc in realm.split(".")])
    domains, users, groups, computers, hbac, membership = [], [], [], [], [], []
    for index, entry in enumerate(raw):
        dn = entry.entry_dn
        realm_object = None
        if re.match(f"cn=.+,cn=ad,cn=etc{ldap_realm}", dn):
            realm_object = Domain(dn, entry["cn"], entry["ipaNTDomainGUID"], entry["ipaNTFlatName"], sid)
            domains.append(realm_object)
        elif re.match(f"uid=.+,cn=users,cn=accounts{ldap_realm}", dn):
            realm_object = User(dn, entry["cn"], entry["gecos"], entry["homeDirectory"], entry["ipaUniqueID"],
                                entry["krbCanonicalName"], entry["krbPrincipalName"], entry["loginShell"],
                                entry["sn"], entry["uid"], entry["uidNumber"], sid)
            users.append(realm_object)
        elif re.match(f"cn=.+,cn=(hostgroups|groups),cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["cn", "ipaUniqueID", "member"]):
            realm_object = Group(dn, entry["cn"], entry["ipaUniqueID"], entry["member"], sid)
            membership.append(Membership(realm_object.member_dn, [realm_object.get_dn()]))
            groups.append(realm_object)
        elif re.match(f"fqdn=.+,cn=computers,cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in
                ["cn", "ipaUniqueID", "krbCanonicalName", "krbPrincipalName", "fqdn"]):
            realm_object = Computer(dn, entry["cn"], entry["ipaUniqueID"], entry["krbCanonicalName"],
                                    entry["krbPrincipalName"], entry["fqdn"], sid)
            computers.append(realm_object)
        elif re.match(f"ipaUniqueID=.+,cn=hbac{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["ipaUniqueID", "ipaEnabledFlag"]) and str(
                entry["ipaEnabledFlag"]) == "True":
            members, hosts, services, ipaid = parse_hbac(entry)
            hbac.append(HBAC(members, hosts, services, ipaid))

        if realm_object is not None and "description" in entry.entry_attributes_as_dict.keys():
            realm_object.set_desc(entry["description"])

    logger.info(f"Found {len(domains)} domains.")
    logger.info(f"Found {len(users)} domains.")
    logger.info(f"Found {len(groups)} domains.")
    logger.info(f"Found {len(computers)} domains.")

    return domains, users, groups, computers, hbac, membership


def legacy_parse(raw, realm, sid) -> tuple:
    """Parse LDAP data for use in the legacy file format.
    :param raw: list of LDAP entries.
    :param realm: name of the realm.
    :param sid: SID of the realm.
    :return: tuple of domains, users, groups, computers, hbac and membership."""

    ldap_realm = "".join([",dc=" + dc for dc in realm.split(".")])
    domains, users, groups, computers, hbac = [], [], [], [], []
    num_objects = len(raw) + 1000
    for index, entry in enumerate(raw):
        dn = entry.entry_dn
        realm_object = None
        if re.match(f"cn=.+,cn=ad,cn=etc{ldap_realm}", dn):
            realm_object = LegacyDomain(dn, entry["cn"], entry["ipaNTDomainGUID"], entry["ipaNTFlatName"],
                                        entry["ipaNTSecurityIdentifier"], sid)
            domains.append(realm_object)
        elif re.match(f"uid=.+,cn=users,cn=accounts{ldap_realm}", dn):
            realm_object = LegacyUser(dn, entry["cn"], entry["gecos"], entry["homeDirectory"], entry["ipaUniqueID"],
                                      entry["ipaNTSecurityIdentifier"], entry["krbCanonicalName"],
                                      entry["krbPrincipalName"],
                                      entry["loginShell"], entry["sn"], entry["uid"], entry["uidNumber"], sid)
            users.append(realm_object)
        elif re.match(f"cn=.+,cn=groups,cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in
                ["cn", "ipaUniqueID", "ipaNTSecurityIdentifier", "member"]):
            realm_object = LegacyGroup(dn, entry["cn"], entry["ipaUniqueID"], entry["ipaNTSecurityIdentifier"],
                                       entry["member"], sid)
            groups.append(realm_object)
        elif re.match(f"cn=.+,cn=(hostgroups|groups),cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["cn", "ipaUniqueID", "member"]):
            realm_object = LegacyGroup(dn, entry["cn"], entry["ipaUniqueID"], sid + "-" + str(num_objects + index),
                                       entry["member"], sid)
            groups.append(realm_object)
        elif re.match(f"fqdn=.+,cn=computers,cn=accounts{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in
                ["cn", "ipaUniqueID", "krbCanonicalName", "krbPrincipalName", "fqdn"]):
            realm_object = LegacyComputer(dn, entry["cn"], entry["ipaUniqueID"], sid + "-" + str(num_objects + index),
                                          entry["krbCanonicalName"], entry["krbPrincipalName"], entry["fqdn"], sid)
            computers.append(realm_object)
        elif re.match(f"ipaUniqueID=.+,cn=hbac{ldap_realm}", dn) and all(
                attr in entry.entry_attributes_as_dict.keys() for attr in ["ipaUniqueID", "ipaEnabledFlag"]) and str(
                entry["ipaEnabledFlag"]) == "True":
            members, hosts, services, ipaid = parse_hbac(entry)
            hbac.append(HBAC(members, hosts, services, ipaid))

        if realm_object is not None and "description" in entry.entry_attributes_as_dict.keys():
            realm_object.set_desc(entry["description"])

    logger.info(f"Found {len(domains)} domains.")
    logger.info(f"Found {len(users)} domains.")
    logger.info(f"Found {len(groups)} domains.")
    logger.info(f"Found {len(computers)} domains.")

    return domains, users, groups, computers, hbac


def parse_hbac(entry: ldap3.abstract.entry.Entry) -> tuple:
    """Parse an HBAC LDAP entry.
    :param entry: HBAC ldap entry.
    :return: members, hosts, services and ID of the HBAC."""

    if "userCategory" in entry.entry_attributes_as_dict.keys():
        members = list(entry["userCategory"])
    else:
        members = list(entry["memberUser"])
    if "hostCategory" in entry.entry_attributes_as_dict.keys():
        hosts = list(entry["hostCategory"])
    else:
        hosts = list(entry["memberHost"])
    if "serviceCategory" in entry.entry_attributes_as_dict.keys():
        services = list(entry["serviceCategory"])
    else:
        services = list(entry["memberService"])

    return members, hosts, services, entry["ipaUniqueID"]


if __name__ == "__main__":
    pass
