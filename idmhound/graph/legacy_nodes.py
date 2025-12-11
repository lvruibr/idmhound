# -*- coding:utf-8 -*-

class LegacyNode():
    """Represents an object of the realm, abstract class."""

    def __init__(self, dn: str, cn, ipaUniqueID, ipaNTSecurityIdentifier, domainsid):
        self.dn = dn
        self.cn = str(cn)
        self.ipaUniqueID = str(ipaUniqueID)
        self.ipaNTSecurityIdentifier = str(ipaNTSecurityIdentifier)
        self.desc = ""
        self.acl = []
        self.domainsid = str(domainsid)

    def get_dn(self):
        return self.dn

    def get_id(self):
        return self.ipaNTSecurityIdentifier

    def set_desc(self, desc):
        self.desc = str(desc)

    def add_ace(self, right, principal_sid, principal_type):
        self.acl.append({"RightName": right,"IsInherited": False, "PrincipalSID": principal_sid, "PrincipalType": principal_type})

class LegacyDomain(LegacyNode):
    """Represents a domain."""

    def __init__(self, dn, cn, ipaNTDomainGUID, ipaNTFlatName, ipaNTSecurityIdentifier, domainsid):

        super().__init__(dn, cn, ipaNTDomainGUID, ipaNTSecurityIdentifier, domainsid)
        self.ipaNTFlatName = str(ipaNTFlatName)

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier, "Properties": {"name": self.ipaNTFlatName, "domain": self.cn, "domainsid": self.domainsid, "distinguishedname": self.dn, "highvalue":True, "description":self.desc},
                "Aces": self.acl}


class LegacyUser(LegacyNode):
    "Represents a user."

    def __init__(self, dn, cn, gecos, homeDirectory, ipaUniqueID, ipaNTSecurityIdentifier, krbCanonicalName, krbPrincipalName, loginShell, sn,
                 uid, uidNumber, domainsid):
        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, domainsid)

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
                "Properties": {"name": self.krbCanonicalName, "distinguishedname": self.dn, "cn": self.cn, "domainsid":self.domainsid,
                               "gecos": self.gecos,
                               "homedirectory": self.homeDirectory,
                               "sn": self.sn, "uid": self.uid, "uidNumber": self.uidNumber, "description": self.desc},
                "Aces": self.acl}



class LegacyComputer(LegacyNode):
    """Represent a computer."""

    def __init__(self, dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, krbCanonicalName, krbPrincipalName, fqdn, domainsid):
        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, domainsid)

        self.krbCanonicalName = str(krbCanonicalName)
        self.krbPrincipalName = str(krbPrincipalName)
        self.fqdn = str(fqdn)

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier,
                "Properties": {"distinguishedname": self.dn, "name": self.fqdn, "description": self.desc,"domainsid":self.domainsid},
                "Aces": self.acl}


class LegacyGroup(LegacyNode):
    """Represent a group."""

    def __init__(self, dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, member, domainsid):

        super().__init__(dn, cn, ipaUniqueID, ipaNTSecurityIdentifier, domainsid)

        self.member_dn = list(member)
        self.member = []

    def resolve_member_dn(self, accounts: list):

        for account in accounts:
            if isinstance(account, LegacyUser) and account.get_dn() in self.member_dn:
                self.member.append({"ObjectIdentifier": account.get_id(), "ObjectType": "User"})
            elif isinstance(account, LegacyComputer) and account.get_dn() in self.member_dn:
                self.member.append({"ObjectIdentifier": account.get_id(), "ObjectType": "Computer"})

    def to_json(self):
        return {"ObjectIdentifier": self.ipaNTSecurityIdentifier,
                "Properties": {"distinguishedname": self.dn, "name": self.cn, "description": self.desc,"domainsid":self.domainsid},
                "Members": self.member,
                "Aces": self.acl}


if __name__ == "__main__":
    pass