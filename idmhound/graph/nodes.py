# -*- coding:utf-8 -*-

class Node():
    """Represents an object of the realm, abstract class."""

    def __init__(self, dn: str, cn, ipaUniqueID, ipaNTSecurityIdentifier):
        self.dn = dn
        self.cn = str(cn)
        self.ipaUniqueID = str(ipaUniqueID)
        self.ipaNTSecurityIdentifier = str(ipaNTSecurityIdentifier)
        self.desc = ""

    def get_dn(self):
        return self.dn

    def get_id(self):
        return self.ipaNTSecurityIdentifier

    def set_desc(self, desc):
        self.desc = str(desc)


class Domain(Node):
    """Represents a domain."""

    def __init__(self, dn, cn, ipaNTDomainGUID, ipaNTFlatName, ipaNTSecurityIdentifier):

        super().__init__(dn, cn, ipaNTDomainGUID, ipaNTSecurityIdentifier)
        self.ipaNTFlatName = str(ipaNTFlatName)

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier, "Properties": {"name": self.ipaNTFlatName, "domain": self.cn, "domainsid": self.ipaNTSecurityIdentifier, "distinguishedname": self.dn, "highvalue":True, "description":self.desc}}


class User(Node):
    "Represents a user."

    def __init__(self, dn, cn, gecos, homeDirectory, ipaUniqueID, ipaNTSecurityIdentifier, krbCanonicalName, krbPrincipalName, loginShell, sn,
                 uid, uidNumber):
        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier)

        self.gecos = str(gecos)
        self.homeDirectory = str(homeDirectory)
        self.krbCanonicalName = str(krbCanonicalName)
        self.krbPrincipalName = str(krbPrincipalName)
        self.loginShell = str(loginShell)
        self.sn = str(sn)
        self.uid = str(uid)
        self.uidNumber = str(uidNumber)

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier,
                "Properties": {"name": self.krbCanonicalName, "distinguishedname": self.dn, "cn": self.cn,
                               "gecos": self.gecos,
                               "homedirectory": self.homeDirectory,
                               "sn": self.sn, "uid": self.uid, "uidNumber": self.uidNumber, "description": self.desc}}


class Computer(Node):
    """Represent a computer."""

    def __init__(self, dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, krbCanonicalName, krbPrincipalName, fqdn):
        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier)

        self.krbCanonicalName = str(krbCanonicalName)
        self.krbPrincipalName = str(krbPrincipalName)
        self.fqdn = str(fqdn)

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier,
                "Properties": {"distinguishedname": self.dn, "name": self.fqdn, "description": self.desc}}


class Group(Node):
    """Represent a group."""

    def __init__(self, dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, member):

        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier)

        self.member_dn = list(member)
        self.member = []

    def resolve_member_dn(self, accounts: list):

        for account in accounts:
            if isinstance(account, User) and account.get_dn() in self.member_dn:
                self.member.append({"ObjectIdentifier": account.get_id(), "ObjectType": "User"})
            elif isinstance(account, Computer) and account.get_dn() in self.member_dn:
                self.member.append({"ObjectIdentifier": account.get_id(), "ObjectType": "Computer"})

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier,
                "Properties": {"distinguishedname": self.dn, "name": self.cn, "description": self.desc},
                "Members": self.member}


if __name__ == "__main__":
    pass