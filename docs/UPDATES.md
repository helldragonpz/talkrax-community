# Independent server updates

Operator tools version: 2026.09.27.1. Linux only.

These tools can apply a reviewed update to the API, worker and admin images.
They do not automatically install arbitrary upstream or nightly releases.
This tools release does not replace the existing server binaries or provide a
new server-image update manifest. Future reviewed binary releases supply one.

## Get the complete tool set
Download the operator-tools archive and SHA256SUMS.txt from:
https://github.com/helldragonpz/talkrax-community/releases/tag/operator-tools-2026.09.27.1

Verify the downloaded checksum file against the GitHub release, then:
```sh
sha256sum -c SHA256SUMS.txt
tar -xzf Talkrax-Operator-Tools-2026.09.27.1.tar.gz
cd Talkrax-Operator-Tools-2026.09.27.1
```
Keep configure.py, manage.py and upgrade.py together. Replacing manage.py alone
is not supported because the tools share the operation lock.
Your existing private instance directory can remain in its current location.
Never run the new-install generator over an existing installation.

## Plan an update
Obtain the future release's update.json, reviewed checksum and image archive.
Verify/load its image archive before applying; digest-pinned registry references
are pulled only when applying and only if absent locally.

```sh
python3 upgrade.py --directory /srv/my-talkrax-instance \
  --project talkrax-my-community --release update.json \
  --sha256 RELEASE_MANIFEST_SHA256
```

Replace RELEASE_MANIFEST_SHA256 with the actual 64-character checksum.
Without --apply, this command only inspects the installation and prints a plan.
It requires the exact supported source image inventory, all seven services
running, unchanged running-image identities, and project ownership matching the
selected compose.json. It rejects mutable tags, unsupported dependency changes,
wrong-project collisions and incomplete previous upgrades.

A checksum checks file integrity; it does not establish publisher identity by
itself. Obtain release files and checksums through the reviewed GitHub release,
not an untrusted message, mirror or random image manifest.

## Apply during a maintenance window
```sh
python3 upgrade.py --directory /srv/my-talkrax-instance \
  --project talkrax-my-community --release update.json \
  --sha256 RELEASE_MANIFEST_SHA256 --apply \
  --backup /srv/private-backups/talkrax-before-update
```

The backup path must be new and outside the instance directory. The update:
1. Locks operator operations for this installation and verifies target images.
2. Stops only this instance's proxy, API, worker and admin.
3. Saves and verifies the database, files, configuration and original keys.
4. Changes only application images and starts the updated application services.
5. Checks image identities, API health and independent operator identity before
   restoring proxy ingress.

Database, Redis, LiveKit and proxy image changes are intentionally rejected.
They require their own release-specific migration procedure. No unattended timer
is installed and no unrelated service is stopped.

Check public HTTPS, sign-in, messages and media after the command succeeds.
The health check does not certify every feature or an arbitrary future migration.

## Failed update and recovery
Before new binaries have run, a backup/preparation failure resumes the original
services. Once new binaries have started, a failure leaves proxy and writers
stopped and records recovery-required in the private .upgrade-state.json.
manage.py start refuses to bypass that state. Do not delete this marker to force
old code to run: a new binary may already have changed the database.

Restore the pre-update backup into a NEW directory and project:
```sh
python3 manage.py --directory /srv/talkrax-recovered \
  --project talkrax-recovered-community restore \
  --backup /srv/private-backups/talkrax-before-update
```

Restore starts only the recovered database. Verify keys, configuration and data;
review ports and DNS before starting the recovered application:
```sh
python3 manage.py --directory /srv/talkrax-recovered \
  --project talkrax-recovered-community start
```

The stopped failed instance may still run database/cache/media containers and
hold media ports. After confirming you selected the failed independent project,
stop those remaining containers with its exact compose file/project before
starting the recovered services on the same ports. Do not delete its volumes.
If the failure occurred before a complete backup was written, retain the instance
and partial backup for investigation; do not restore an unverified archive.

## Verification and limits
The 27 September test used separate Docker networks with internet egress blocked,
a fresh database, synthetic users and private test certificates. It verified:
- successful image replacement preserves messages, sessions and keys;
- a wrong installation/project pair is rejected before mutation;
- a deliberately broken image closes ingress and blocks ordinary restart;
- the pre-update backup restores data and keys to another project.

The changed test image used the same server code with a different image identity,
and the broken image used an intentionally failing entry point. This establishes
the update/recovery mechanism, not compatibility with future schema migrations.
The evidence file records the complete checks. Public-network media, Windows,
integrated messaging/file E2EE and the complete open-source client/server remain
outside this acceptance.
