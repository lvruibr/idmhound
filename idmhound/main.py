# -*- coding:utf -*-

import json
from idmhound.graph.utils import *
from idmhound.collectors import ldap
import argparse
import logging
import sys
from datetime import datetime


def main():

    parser = argparse.ArgumentParser(add_help=True, description="Bloodhound ingestor for FreeIPA/Red Hat IdM environment.")
    parser.add_argument("-d", "--domain", action="store", required=True, help="Domain / realm to query.")
    parser.add_argument("-u", "--username", action="store", required=True, help="Username to query the realm.")
    parser.add_argument("-p", "--password", action="store", required=True, help="Password of the account to query the realm.")
    parser.add_argument("-dc", "--domain-controller", action="store", required=True, help="Server to query.")
    parser.add_argument("-dn", "--base-dn", action="store", default="")
    parser.add_argument("-l", "--legacy", action="store_true", default=False)
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, encoding="utf-8", filemode="w", level=logging.INFO,
                        format="{asctime} - {levelname}: {message}", style="{", datefmt="%d-%m-%Y %H:%M:%S")
    logger = logging.getLogger()

    logger.info(f"Getting LDAP data of {args.domain}...")
    ldap_realm = "".join([",dc=" + dc for dc in args.domain.split(".")])
    bind_dn = f"uid={args.username},cn=users,cn=accounts{ldap_realm}"
    data = ldap.collect(args.domain_controller, bind_dn, args.password, args.base_dn)
    logger.info(f"Found {len(data)} LDAP entries.")
    sid = identify_realm_sid(data, args.domain)
    logger.info(f"Realm SID: {sid}")

    logger.info("Parsing LDAP data...")
    if args.legacy:
        domains, users, groups, computers, hbac = ldap.legacy_parse(data, args.domain, sid)
        member_lookup(users+computers+groups, groups)
        member_lookup(users+computers+groups, hbac)
        logger.info("Save output to legacy JSON file format.")
        legacy_save(domains, users, groups, computers, hbac)
    else:
        domains, users, groups, computers, hbac, membership = ldap.parse(data, args.domain, sid)
        member_lookup(users+computers+groups, membership)
        member_lookup(users+computers+groups, hbac)
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        logger.info(f"Save output to Opengraph file format: idmhound_{now}.json")
        with open(f"idmhound_{now}.json","w") as output:
            output.write(json.dumps(to_opengraph(domains+users+groups+computers, hbac+membership)))






if __name__ == "__main__":
    main()

