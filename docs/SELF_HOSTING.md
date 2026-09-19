# Talkrax independent Linux server preview

This package runs its own accounts, database, file storage, mail configuration,
media service and administration. It contains server binaries, not proprietary
application source. Read BINARY-LICENCE.txt and THIRD-PARTY-NOTICES before use.

This preview has passed isolated Linux installation, account verification/MFA,
administrator sign-in, direct messages, file transfer, account export, password
recovery, restart and backup/restore checks. Its services were denied internet
egress during those checks. Public-network voice/video, restrictive-NAT/TURN
support, a separate Windows server installer, and a current Windows client have
not passed release acceptance. Private text/files are currently service-readable;
integrated messaging/file E2EE and Discord migration are not released.

## Before installation

Use a Linux x86-64 host with Docker Engine, Docker Compose v2 and Python 3.10 or
newer. Installation was exercised with PostgreSQL 17, the digest-pinned
dependencies in images.json and the native Linux build 35 client.

Provide two DNS names pointing to the server and working SMTP credentials.
Allow inbound TCP 80 and 443 for HTTPS; media additionally needs TCP 7881 and UDP
50000-50100 forwarded to this host. Use your actual reachable public IP in
mediaPublicIp, not a private/LAN address. No bandwidth or participant guarantee
is implied by configured limits. TURN is not configured in this preview.

Keep the adminAllowedCidrs list limited to your administrator public IP or VPN.
Do not list a broad public range. Caddy is the only trusted proxy. Adding another
proxy requires a reviewed configuration change, not accepting client-supplied
forwarding headers.

Do not install over an existing directory. Backups must preserve the database,
stored files and the original instance keys together.

## Install

Extract the release into a directory you own, then verify SHA256SUMS.txt.
The binary image archive and the operator-tools archive are separate release
assets. Extract the tools, put the image archive beside images.json, then run:

    sha256sum -c SHA256SUMS.txt
    docker load --input Talkrax-Independent-Server-2026.09.20-preview.1-images.tar.gz
    chmod 700 .
    cp operator.example.json operator.json
    chmod 600 operator.json

Edit operator.json with your own details, SMTP credentials and admin IP ranges.
The example intentionally fails validation until you replace those values.
The policy URLs must be your own published policies.

    python3 configure.py --operator operator.json --images images.json --output instance
    python3 manage.py --directory instance --project talkrax-my-community start
    python3 manage.py --directory instance --project talkrax-my-community status

Initial dependency images are fetched by immutable digest from their upstream
registries. The supplied Talkrax API/worker/admin images are loaded from the
binary archive. No Talkrax source build, official login, licence-server connection
or access to the official database is required.

The generated directory is mode 0700. Read-only bind files inside it are mode
0444 so unprivileged containers can read them; other local users cannot traverse
the parent directory. Do not make that directory public or copy those files to
a web root. operator.json and backups also contain secrets.

## Connect the client and appoint the owner

Install the current Linux .deb from the Talkrax release downloads, or extract the
portable Linux archive. At sign-in select Change server, enter your HTTPS origin,
review the operator and policies, and select Use server. Accounts and sessions
are separate for each origin.

Register a new account on your instance, verify its email, and enable
authenticator MFA in User Settings. Then run on the server:

    python3 manage.py --directory instance --project talkrax-my-community appoint-owner --email owner@your-domain.example --reason "Initial community server setup"

The command rejects unverified accounts, accounts without confirmed MFA, hosted
instances and second attempts. It records the appointment. No default admin
password or special email address grants ownership.

Open https://chat.your-domain.example/admin from an allowed admin address and
sign in with that account and MFA. Staff management, reports, operational settings
and privacy-request review are provided by this instance's administration
service. Completing a privacy request does not erase an account: the preview
cannot mark an unexecuted erasure as completed.

## Backup and restore

    python3 manage.py --directory instance --project talkrax-my-community backup --output backup-2026-09-20

Backup briefly pauses this instance's API, worker and admin processes to keep its
database and files consistent, and resumes them in a finally block. It does not
pause other projects. Store the private backup on protected off-host storage;
it contains user data and instance keys. Its manifest verifies accidental
corruption, not the authenticity of an untrusted third-party backup.

Restore always requires a NEW project and directory:

    python3 manage.py --directory restored-instance --project talkrax-restored-community restore --backup backup-2026-09-20

Restore verifies checksums, rejects unsafe storage archive entries and refuses
existing project resources. It preserves account data and keys, allocates a fresh
private bridge subnet and starts only the new database. Inspect DNS, media IP
and published ports before starting restored services; do not run both instances
against the same public ports.

    python3 manage.py --directory restored-instance --project talkrax-restored-community start

## Update and removal

There is no accepted automated update path for this first preview. Back up before
any later update, retain the original keys and follow that release's migration
instructions. Never rerun the new-install generator on existing data.

To remove the running preview, use Docker Compose with this exact project's name
and compose.json. Stopping/removing containers does not remove named volumes
unless you explicitly request volume deletion. Keep a verified backup before
deleting any volumes or instance directory.

Windows packaging and media acceptance remain open. Do not describe this Linux
preview as the completed Windows/Linux distribution.
