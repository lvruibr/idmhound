# IDMHound

IDMHound is a BloodHound ingestor for FreeIPA and Red Hat Identity Manager environments.

## Installation

```
git clone https://github.com/lvruibr/idmhound
pip install .
```

## Usage

By default, the results are saved in a JSON file in the Opengraph format.

```
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM>
```

Alternatively the legacy Bloodhound file format is also supported.

```
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM> --legacy
```

## Example Cypher queries

*List users part of groups that can SSH*
```
MATCH p=(:User)-[]-(:Group)-[:HBAC_sshd]->(:Group)
RETURN p
LIMIT 1000
```

## Limitations

* Search and pathfindings are not yet supported by Bloodhound when parsing files in the Opengraph format.
* When using the legacy file format, upload first the users, groups, domains and computers JSON file. Only then, upload the remaining files to prevent duplicated nodes.