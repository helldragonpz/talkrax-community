# Release status - 20 September 2026

## Independent Linux server preview 1

The [release](https://github.com/helldragonpz/talkrax-community/releases/tag/server-preview-2026.09.20.1)
contains API, worker and administrator binaries as a Docker image archive,
operator tools, pinned dependency references, licences/notices and checksums.

The initial server release passed 24 checks. The follow-up with Linux client
build 36 passed [27 checks](evidence/independent-linux-client36.json) with internet
egress blocked, covering fresh setup, SMTP verification, MFA, owner setup, admin browser sign-in,
two-user messaging, file upload/download, account export, recovery, restart and
backup/restore. Browser review saved and reloaded a privacy decision and checked
its staff audit record. The installed Linux client also reviewed its server
operator, signed in with
MFA and restored its authenticated session after restart. This establishes those
Linux workflows; it does not verify public-internet voice/video or every platform.

## Clients

Linux client build 36 includes Change server, separate sessions per
origin, a .deb installer and a portable archive. It is the available client for
testing this server preview. The current public Windows build is older and is
not an accepted independent-server client. Android/web are not part of the
independent distribution scope.

## Not released or accepted

- Current Windows client/server installer and runtime acceptance.
- Public-internet media across independent hosts and restrictive-NAT/TURN support.
- Additional native workflows, physical devices, Wayland and public-host media acceptance.
- Automated server updates.
- Integrated text/file E2EE, legacy encrypted-history conversion and independent security review.
- Discord migration.
- Verified account-erasure execution, complete legal-request/retention workflows
  and commercial Bulgarian/EU legal clearance.

Account deletion can be requested and reviewed. A status-only action cannot
claim erasure has occurred. Do not treat a reviewed request as proof of deletion.
