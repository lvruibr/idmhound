# -*- coding:utf-8 -*-

class Node():
    """Represents an object of the realm, abstract class."""

    def __init__(self, dn: str, cn, ipaUniqueID, domainsid):
        self.dn = dn
        self.cn = str(cn)
        self.ipaUniqueID = str(ipaUniqueID)
        self.desc = ""
        self.acl = []
        self.domainsid = str(domainsid)

    def get_dn(self):
        return self.dn

    def get_id(self):
        return self.ipaUniqueID

    def set_desc(self, desc):
        self.desc = str(desc)

    def add_ace(self, right, principal_sid, principal_type):
        self.acl.append({"RightName": right,"IsInherited": False, "PrincipalSID": principal_sid, "PrincipalType": principal_type})

class Domain(Node):
    """Represents a domain."""

    def __init__(self, dn, cn, ipaNTDomainGUID, ipaNTFlatName, domainsid):

        super().__init__(dn, cn, ipaNTDomainGUID, domainsid)
        self.ipaNTFlatName = str(ipaNTFlatName)

    def to_json(self):
        return {"id": self.ipaUniqueID, "Properties": {"name": self.ipaNTFlatName, "domain": self.cn, "domainsid": self.domainsid, "distinguishedname": self.dn, "highvalue":True, "description":self.desc, "system_tags":"test1", "user_tags":"test1"},
                "kinds": ["Domain"]}


class User(Node):
    "Represents a user."

    def __init__(self, dn, cn, gecos, homeDirectory, ipaUniqueID, krbCanonicalName, krbPrincipalName, loginShell, sn,
                 uid, uidNumber, domainsid):
        super().__init__(dn, cn, ipaUniqueID, domainsid)

        self.gecos = str(gecos)
        self.homeDirectory = str(homeDirectory)
        self.krbCanonicalName = str(krbCanonicalName)
        self.krbPrincipalName = str(krbPrincipalName)
        self.loginShell = str(loginShell)
        self.sn = str(sn)
        self.uid = str(uid)
        self.uidNumber = str(uidNumber)

    def to_json(self):
        return {"id": self.ipaUniqueID,
                "properties": {"name": self.krbCanonicalName, "distinguishedname": self.dn, "cn": self.cn, "domainsid":self.domainsid,
                               "gecos": self.gecos,
                               "homedirectory": self.homeDirectory,
                               "sn": self.sn, "uid": self.uid, "uidNumber": self.uidNumber, "description": self.desc},
                "kinds": ["User"]}



class Computer(Node):
    """Represent a computer."""

    def __init__(self, dn, cn, ipaUniqueID, krbCanonicalName, krbPrincipalName, fqdn, domainsid):
        super().__init__(dn, cn, ipaUniqueID, domainsid)

        self.krbCanonicalName = str(krbCanonicalName)
        self.krbPrincipalName = str(krbPrincipalName)
        self.fqdn = str(fqdn)

    def to_json(self):
        return {"id": self.ipaUniqueID,
                "properties": {"distinguishedname": self.dn, "name": self.fqdn, "description": self.desc,"domainsid":self.domainsid},
                "kinds": ["Computer"]}


class Group(Node):
    """Represent a group."""

    def __init__(self, dn, cn, ipaUniqueID, member, domainsid):

        super().__init__(dn, cn, ipaUniqueID, domainsid)

        self.member_dn = list(member)
        self.member = []

    def resolve_member_dn(self, accounts: list):

        for account in accounts:
            if isinstance(account, (User,Computer)) and account.get_dn() in self.member_dn:
                self.member.append(account.get_id())


    def to_json(self):
        return {"id": self.ipaUniqueID,
                "Properties": {"distinguishedname": self.dn, "name": self.cn, "description": self.desc,"domainsid":self.domainsid},
                "kinds": ["Group"]}


if __name__ == "__main__":
    pass