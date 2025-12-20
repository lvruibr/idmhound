# IDMHound

IDMHound is a [BloodHound](https://bloodhound.specterops.io/) collector for FreeIPA and Red Hat Identity Management environments.

It collects users, groups, domains, computers and HBAC relationships and can export them in Opengraph format or in the legacy Bloodhound file format.

Analysing of the relationship helps identifying privilege and lateral movements paths within the FreeIPA / Red Hat Identity Management realms.

## Installation

```
git clone https://github.com/lvruibr/idmhound
cd idmhound
pip install .
```

## Usage

By default, the results are saved in a JSON file in the Opengraph format.

```
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM>
```

Alternatively the legacy Bloodhound file format (or a mix of both) is also supported.

```
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM> --legacy
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
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[:HBAC_sshd]->(t)
RETURN p
LIMIT 1000
```

*List users part of groups that can FTP*
```
MATCH p=(s)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND type(e) CONTAINS 'ftp'
RETURN p
LIMIT 1000
```

*List users part of groups that can RDP (Xrdp and GNOME RDP)*
```
MATCH p=(s)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND type(e) IN ['xrdp', 'xrdp-sesman', 'gnome-remote-desktop']
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

* Search and pathfindings are not yet supported by Bloodhound when parsing files in the Opengraph format.
* When using the legacy file format, upload first the users, groups, domains and computers JSON file. Only then, upload the remaining files to prevent duplicated nodes.