# Independent server operator guide

**Pre-release status:** no complete server installer or accepted binary image
inventory is published. The steps below describe the required deployment and
acceptance process, not commands for an already available package.

## Intended deployment
A server installation uses its own API and worker, PostgreSQL, internal Redis,
persistent storage, LiveKit and HTTPS reverse proxy. Windows/Linux desktop clients
connect to the operator's HTTPS address. The operator supplies email delivery,
DNS, TLS, firewall configuration, media capacity and public policies.

A Windows server release needs a tested supported runtime and installation path;
a Linux Compose prototype alone is not a native Windows server release.
Database and cache ports must remain private. Media needs independently
reachable TCP/UDP paths; an advertised NIC speed is not verified internet capacity.

## New installation requirements
The eventual versioned release must include a reviewed installer/configuration
tool, exact immutable image inventory, supported operating systems, third-party
notices and checksums. It must create fresh keys and credentials for each
installation and securely provision the first operator. Never copy official
Talkrax secrets, user data or seed accounts.

The operator provides a server name, real contact details, published privacy and
terms URLs, API/media hostnames, a verified public media address and SMTP
submission credentials. Secret configuration belongs in protected local storage,
not this repository.

## First-use acceptance
Before inviting users, verify registration and email delivery, independent
accounts, administrator access and MFA, private room permissions, messaging,
file permissions, calls between different networks and restricted media policy.
Test recovery after a restart and deny access to revoked accounts/devices.

Encrypted messaging, encrypted history recovery and Discord migration must not
be advertised until their separate implementations and acceptance tests pass.

## Updates and backups
A versioned update must preserve installed authentication/storage keys and
persistent database and uploaded files. Back up those items together before
applying a database migration. Test restoration into an isolated instance.
Starting a fresh installer over an existing installation is not an update.

A backup containing secrets needs access control and encryption. Losing a storage
key can make stored operational secrets unusable. Keeping a database without its
matching keys is not a verified recovery plan.

## Independence boundary
Official subscriptions, marketplace services, push credentials, private source
and paid artwork are not automatically included. The intended product permits
normal operation and configuration by its owner; proprietary software and
third-party components remain subject to their respective terms.

Release acceptance must prove that official Talkrax services can be unavailable
without breaking local accounts, ordinary server operation or locally hosted media.
