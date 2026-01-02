# IDMHound

IDMHound is a [BloodHound](https://bloodhound.specterops.io/) collector for FreeIPA and Red Hat Identity Management environments.

It collects users, groups, domains, computers and HBAC relationships and can export them in Opengraph format or in the legacy Bloodhound file format.

Analysing of the relationship helps identifying privilege and lateral movements paths within the FreeIPA / Red Hat Identity Management realms.

![IDMHound](https://lvruibr.github.io/images/idmhound/idmhound.png)

## Installation

```bash
git clone https://github.com/lvruibr/idmhound
cd idmhound
pip install .
```

## Usage

**Output format**

By default, the results are saved in a JSON file in the Opengraph format.

```bash 
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM>
```

Alternatively the legacy Bloodhound file format (or a mix of both) is also supported.

```bash
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM> --legacy
```

**Authentication**

Regarding authentication, plain text credentials (or an anonymous bind) will be used by default, but Kerberos is also supported.

1. A valid TGT is required. For instance, running `klist` should return an output similar to the one below.

```bash
$ klist
Ticket cache: FILE:/tmp/krb5cc_1000
Default principal: lbal@LAB.LO

Valid starting     Expires            Service principal
01/02/26 16:25:59  01/03/26 15:26:02  krbtgt/LAB.LO@LAB.LO
```

2. The domain name of the LDAP server must be provided to IDMHound along with the Kerberos switch (`-k` or `--kerberos`).
```bash
idmhound -dc idm01.lab.lo -d lab.lo -k
```

## Example Cypher queries

*List members of highly privileged (_T0_) groups*
```
MATCH p=(u:User)-[:MemberOf]->(g:Group)
WHERE g.name IN ['ADMINS', 'TRUST ADMINS']
RETURN p
LIMIT 1000;
```

*List users part of groups that can SSH*
```
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[:HBAC_sshd|HBAC_all]->(t)
RETURN p
LIMIT 1000
```

*List users part of groups that can FTP*
```
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND (type(e) CONTAINS 'ftp' or type(e) CONTAINS 'all')
RETURN p
LIMIT 1000
```

*List users part of groups that can RDP (Xrdp and GNOME RDP)*
```
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND (type(e) CONTAINS 'xrdp' or type(e) CONTAINS  'xrdp-sesman' or type(e) CONTAINS 'gnome-remote-desktop' or type(e) CONTAINS 'all')
RETURN p
LIMIT 1000
```

*List users and groups with sudoer rights*
```
MATCH p=(s)-[e]->(t)
WHERE type(e) CONTAINS 'Sudoer'
RETURN p
LIMIT 1000
```

*List Kerberoastable accounts*
```
MATCH (u)
WHERE u.hasspn=true
RETURN u
LIMIT 100
```

*List disabled accounts*
```
MATCH (s)
WHERE s:User and s.enabled = FALSE
RETURN s
LIMIT 1000
```

*Shortest path to highly privileged groups (T0)*
```
MATCH p=shortestPath((t)-[*1..]->(s:Group))
WHERE s.name IN ['ADMINS', 'TRUST ADMINS'] AND s<>t
RETURN p
LIMIT 1000
```

## Limitations

* Search and pathfinding are not yet supported by BloodHound when parsing files in the Opengraph format[^1].
* When using the legacy file format, upload first the users, groups, domains and computers JSON files. Only then, upload the remaining files to prevent duplicated nodes.

[^1]: [https://bloodhound.specterops.io/opengraph/faq#do-custom-nodes-and-edges-work-with-search-and-pathfinding](https://bloodhound.specterops.io/opengraph/faq#do-custom-nodes-and-edges-work-with-search-and-pathfinding)