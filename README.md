# IDMHound

IDMHound is a [BloodHound](https://bloodhound.specterops.io/) collector for FreeIPA and Red Hat Identity Management environments.

It collects users, groups, domains, computers and HBAC relationships and can export them in Opengraph format or in the legacy Bloodhound file format.

Analysing of the relationship helps identifying privilege and lateral movements paths within the FreeIPA / Red Hat Identity Management realms.

![IDMHound](https://lvruibr.github.io/images/idmhound/idmhound.png)

## Table of contents

* [Features](#features)
* [Requirements](#requirements)
* [Installation](#installation)
* [Usage](#usage)
  * [Command-line options](#command-line-options)
  * [Output format](#output-format)
  * [Authentication](#authentication)
  * [Output files](#output-files)
  * [Importing into BloodHound](#importing-into-bloodhound)
* [Example Cypher queries](#example-cypher-queries)
* [Limitations](#limitations)
* [Contributing](#contributing)
* [License](#license)
* [Disclaimer](#disclaimer)

## Features

IDMHound performs a single subtree LDAP search against the realm and turns the returned entries into a graph:

* **Domains** – the realm itself, including its SID (resolved from `ipaNTSecurityIdentifier`).
* **Users** – user accounts and Kerberos service principals (services are exported as user nodes).
* **Groups** – user groups and host groups.
* **Computers** – enrolled hosts.
* **HBAC** – host-based access control rules, expanded per HBAC service (for example `HBAC_sshd`, `HBAC_all`).
* **Sudo** – sudo rules, including sudo command groups and commands.
* **IPA rights** – privileges such as `GetKeytab` and `SetKeytab`.
* **Memberships** – `MemberOf` relationships between users, services, computers and groups.

Two output formats are supported:

* **Opengraph JSON** (default) – a single file containing all nodes and edges.
* **Legacy BloodHound format** (`--legacy`) – multiple files, one per object type, plus the HBAC, sudo and IPA rights edges in Opengraph format.

## Requirements

* Python **3.12** or later.
* Kerberos system libraries and headers, required to build/run the `gssapi` dependency (for example `krb5-devel` and `krb5-workstation` on RHEL/Fedora, `libkrb5-dev` and `krb5-user` on Debian/Ubuntu).
* Network access to the LDAP port of a FreeIPA / Red Hat IdM server.
* A valid Kerberos TGT if Kerberos authentication is used (see [Authentication](#authentication)).

Python dependencies (installed automatically): [`ldap3`](https://pypi.org/project/ldap3/) `>=2.9.1` and [`gssapi`](https://pypi.org/project/gssapi/) `>=1.9.0`.

## Installation

```bash
git clone https://github.com/lvruibr/idmhound
cd idmhound
pip install .
```

The installation exposes the `idmhound` console script (entry point `idmhound.main:main`).

## Usage

```bash
idmhound -dc <SERVER> -d <REALM> [-u <USERNAME>] [-p <PASSWORD>] [-dn <BASE_DN>] [-l] [-k]
```

### Command-line options

| Flag | Long form | Description | Required | Default |
| --- | --- | --- | --- | --- |
| `-d` | `--domain` | Domain / realm to query. Also used to build the base DN of the bind account and to locate realm objects. | Yes | – |
| `-dc` | `--domain-controller` | Server to query. | Yes | – |
| `-u` | `--username` | Username to query the realm. Used to build the bind DN `uid=<username>,cn=users,cn=accounts,dc=...`. | No | empty (anonymous bind) |
| `-p` | `--password` | Password of the account to query the realm. | No | empty (anonymous bind) |
| `-dn` | `--base-dn` | Base DN of the LDAP search. Leave empty to search from the root. | No | empty |
| `-l` | `--legacy` | Output the files in the legacy BloodHound format. | No | `false` (Opengraph) |
| `-k` | `--kerberos` | Use Kerberos (GSSAPI/SASL) authentication instead of a simple bind. | No | `false` |
| `-h` | `--help` | Show the help message and exit. | No | – |

Both a username and a password must be supplied for a simple bind; if either is missing, an anonymous bind is performed and the collected data will be limited (the realm SID can then only be approximated, and IDMHound logs a warning).

### Output format

By default, the results are saved in a JSON file in the Opengraph format.

```bash
idmhound -dc idm01.lab.lo -u lbal -p 'Password123!' -d lab.lo
```

Alternatively the legacy Bloodhound file format (or a mix of both) is also supported.

```bash
idmhound -dc idm01.lab.lo -u lbal -p 'Password123!' -d lab.lo --legacy
```

### Authentication

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

An anonymous bind can be attempted by omitting the credentials entirely:

```bash
idmhound -dc idm01.lab.lo -d lab.lo
```

### Output files

Files are written to the current working directory. Every filename is suffixed with the collection timestamp (`YYYYMMDDHHMMSS`).

| Mode | Files |
| --- | --- |
| Opengraph (default) | `idmhound_<timestamp>.json` |
| Legacy (`--legacy`) | `domains_<timestamp>.json`, `users_<timestamp>.json`, `groups_<timestamp>.json`, `computers_<timestamp>.json`, `hbac_<timestamp>.json`, `sudoer_<timestamp>.json`, `iparights_<timestamp>.json` |

In legacy mode, `users_<timestamp>.json` contains both user accounts and Kerberos service principals, while `hbac_`, `sudoer_` and `iparights_` files hold edges in the Opengraph format.

### Importing into BloodHound

**Opengraph output**

1. Open the BloodHound UI and go to *Administration* → *File Ingest*.
2. Upload `idmhound_<timestamp>.json`.
3. Once the ingest job completes, the IDMHound nodes and edges are available in the *Cypher* tab.

**Legacy output**

1. Open the BloodHound UI and go to *Administration* → *File Ingest*.
2. Upload `domains_<timestamp>.json`, `users_<timestamp>.json`, `groups_<timestamp>.json` and `computers_<timestamp>.json` **first**, and wait for the ingest to finish.
3. Then upload `hbac_<timestamp>.json`, `sudoer_<timestamp>.json` and `iparights_<timestamp>.json`.

Uploading the edge files before the node files creates duplicated nodes.

## Example Cypher queries

*List members of highly privileged (_T0_) groups*

Returns the accounts that are direct members of the built-in administrative groups.

```cypher
MATCH p=(u:User)-[:MemberOf]->(g:Group)
WHERE g.name IN ['ADMINS', 'TRUST ADMINS']
RETURN p
LIMIT 1000;
```

*List users part of groups that can SSH*

Follows group memberships of any depth, then any HBAC rule granting the `sshd` service (or all services).

```cypher
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[:HBAC_sshd|HBAC_all]->(t)
RETURN p
LIMIT 1000
```

*List users part of groups that can FTP*

```cypher
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND (type(e) CONTAINS 'ftp' or type(e) CONTAINS 'all')
RETURN p
LIMIT 1000
```

*List users part of groups that can RDP (Xrdp and GNOME RDP)*

```cypher
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[e]->(t)
WHERE type(e) CONTAINS 'HBAC' AND (type(e) CONTAINS 'xrdp' or type(e) CONTAINS  'xrdp-sesman' or type(e) CONTAINS 'gnome-remote-desktop' or type(e) CONTAINS 'all')
RETURN p
LIMIT 1000
```

*List users and groups with sudoer rights*

Any principal able to run commands through a sudo rule, directly or through a group.

```cypher
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[e]->(t)
WHERE type(e) CONTAINS 'Sudoer'
RETURN p
LIMIT 1000
```

*List every HBAC edge reaching a given host*

Useful to review who is allowed on a specific machine and through which service (the `name` property of a computer is its FQDN).

```cypher
MATCH p=(s)-[e]->(t:Computer)
WHERE type(e) CONTAINS 'HBAC' AND t.name = 'idm01.lab.lo'
RETURN p
LIMIT 1000
```

*List Kerberoastable accounts*

Accounts carrying a service principal name, which can be targeted for Kerberoasting.

```cypher
MATCH (u)
WHERE u.hasspn=true
RETURN u
LIMIT 100
```

*List disabled accounts*

```cypher
MATCH (s)
WHERE s:User and s.enabled = FALSE
RETURN s
LIMIT 1000
```

*Shortest path to highly privileged groups (T0)*

Shortest attack path from any node to the administrative groups.

```cypher
MATCH p=shortestPath((t)-[*1..]->(s:Group))
WHERE s.name IN ['ADMINS', 'TRUST ADMINS'] AND s<>t
RETURN p
LIMIT 1000
```

*Shortest path from a specific user to a T0 group*

Same idea, scoped to one starting account.

```cypher
MATCH p=shortestPath((s:User {name: 'lbal@LAB.LO'})-[*1..]->(g:Group))
WHERE g.name IN ['ADMINS', 'TRUST ADMINS']
RETURN p
LIMIT 1000
```

*List users who can read or write Keytab*

Principals able to retrieve or overwrite a keytab, and therefore to impersonate the target.

```cypher
MATCH p=(s:User)-[:MemberOf*0..]->(g)-[:GetKeytab|SetKeytab]->(t)
RETURN p
LIMIT 1000
```

## Limitations

* Search and pathfinding are not yet supported by BloodHound when parsing files in the Opengraph format[^1].
* When using the legacy file format, upload first the users, groups, domains and computers JSON files. Only then, upload the remaining files to prevent duplicated nodes.

[^1]: [https://bloodhound.specterops.io/opengraph/faq#do-custom-nodes-and-edges-work-with-search-and-pathfinding](https://bloodhound.specterops.io/opengraph/faq#do-custom-nodes-and-edges-work-with-search-and-pathfinding)

## Contributing

Issues and pull requests are welcome on [GitHub](https://github.com/lvruibr/idmhound). When reporting a bug, please include the IDMHound version, the Python version and the command line used (without credentials). When contributing code, keep the existing style and describe the FreeIPA / Red Hat IdM setup the change was tested against.

## License

IDMHound is distributed under the terms of the GNU General Public License v3.0. See [LICENSE](LICENSE) for the full text.

## Disclaimer

IDMHound is intended for authorised security assessments and administration of environments you own or have explicit written permission to test. Using it against systems without authorisation is illegal. The authors accept no liability for misuse or for any damage caused by this tool.
