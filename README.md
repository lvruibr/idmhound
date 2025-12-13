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
MATCH p=(:User)-[]-(:Group)-[:HBAC_sshd]->(:Group)
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

## Limitations

* Search and pathfindings are not yet supported by Bloodhound when parsing files in the Opengraph format.
* When using the legacy file format, upload first the users, groups, domains and computers JSON file. Only then, upload the remaining files to prevent duplicated nodes.