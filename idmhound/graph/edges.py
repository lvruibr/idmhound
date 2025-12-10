# -*- coding:utf-8 -*-
import re
from idmhound.graph.nodes import *

class Edges():
    """Represent an edge or a group of edges, abstract class."""

    def __init__(self, starts: list, ends: list, kinds: list, ipaUniqueID):
        self.ipaUniqueID = str(ipaUniqueID)
        self.starts_dn = [str(start) for start in starts]
        self.ends_dn = [str(end) for end in ends]
        self.kinds = [str(kind) for kind in kinds]
        self.desc = ""

    def set_desc(self, desc):
        self.desc = str(desc)


class HBAC(Edges):
    """Represent a Host-Based Access Control."""

    def __init__(self, starts: list, ends: list, services: list, ipaUniqueID):

        if "all" not in services:
            services = [re.findall("cn=(.+),cn=hbacservices,cn=hbac,.+", service)[0].replace("-", "_") for service in services]
        super().__init__(starts, ends, services, ipaUniqueID)
        self.ends = []
        self.starts = []

    def resolve_member_dn(self, accounts: list):

        for account in accounts:
            if account.get_dn() in self.ends_dn or ("all" in self.ends_dn and isinstance(account, Computer)):
                self.ends.append(account.get_id())
            if account.get_dn() in self.starts_dn or ("all" in self.starts_dn and isinstance(account, User)):
                self.starts.append(account.get_id())

    def to_json(self):

        edges = []
        for kind in self.kinds:
            for start in self.starts:
                for end in self.ends:
                    edges.append({"kind": f"HBAC_{kind}", "start": {"value": start, "match_by": "id"},
                                  "end": {"value": end, "match_by": "id"}})
        return edges
