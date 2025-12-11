# IDMHound

IDMHound is a BloodHound ingestor for FreeIPA and Red Hat Identity Manager environments.

## Installation

```
git clone https://github.com/lvruibr/idmhound
pip install .
```

## Usage

```
idmhound -dc <SERVER> -u <USERNAME> -p <PASSWORD> -d <REALM>
```

## Example Cypher queries

*List users part of groups that can SSH*
```
MATCH p=(:User)-[]-(:Group)-[:HBAC_sshd]->(:Group)
RETURN p
LIMIT 1000
```