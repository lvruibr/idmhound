# -*- coding:utf -*-

import json
from idmhound.graph.utils import *
from idmhound.collectors import ldap
import argparse


def main():

    parser = argparse.ArgumentParser(add_help=True, description="Bloodhound ingestor for FreeIPA/Red Hat IdM environment.")
    parser.add_argument("-d", "--domain", action="store", required=True, help="Domain / realm to query.")
    parser.add_argument("-u", "--username", action="store", required=True, help="Username to query the realm.")
    parser.add_argument("-p", "--password", action="store", required=True, help="Password of the account to query the realm.")
    parser.add_argument("-dc", "--domain-controller", action="store", required=True, help="Server to query.")
    parser.add_argument("-dn", "--base-dn", action="store", default="")
    args = parser.parse_args()

    bind_dn = f"uid={args.username},cn=users,cn=accounts,dc=lab,dc=lo"
    data = ldap.collect(args.domain_controller, bind_dn, args.password, args.base_dn)
    sid = identify_realm_sid(data, args.domain)

    domains, users, groups, computers, hbac = ldap.parse(data, args.domain, sid)
    member_lookup(users+computers, groups)
    member_lookup(users+computers+groups, hbac)



    with open("domains.json", "w") as output:
        output.write(json.dumps(to_json(domains, "domains")))
    with open("users.json", "w") as output:
        output.write(json.dumps(to_json(users, "users")))
    with open("groups.json", "w") as output:
        output.write(json.dumps(to_json(groups, "groups")))
    with open("computers.json", "w") as output:
        output.write(json.dumps(to_json(computers, "computers")))
    with open("hbac.json", "w") as output:
        output.write(json.dumps(to_opengraph(hbac)))


if __name__ == "__main__":
    main()

