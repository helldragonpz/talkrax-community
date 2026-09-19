# Talkrax Community

Talkrax is a communication app for gaming communities: chat, voice, video and
screen sharing, with Windows and Linux desktop clients.

This repository is the public distribution and documentation home for the
planned independent Windows/Linux edition. It is **not an open-source release
of the private Talkrax application**.

## Install and use the desktop app
- [Client installation, updates and first use](docs/CLIENT_INSTALLATION.md)
- [Official downloads](https://talkrax.com/downloads)
- [Release files and SHA-256 checksums](https://talkrax.com/releases/release-manifest.json)

Linux build 35 adds a Debian-format installer and fixes the native audio-device
enumeration regression. The portable archive remains available. The currently
published Windows client is still a portable build; a new Windows installer
has not yet passed release verification and signing.

## Independent servers
[Self-hosting status and operator guide](docs/SELF_HOSTING.md) explains the
deployment model, client connection flow and release requirements.

**A complete independent server package is not published yet.** Do not treat this
repository as an installable server or reuse configuration or accounts from the
official service. Public server installation commands will accompany the actual
versioned server package and its tested image inventory.

The intended edition uses the operator's accounts, database, keys, storage, email
and media infrastructure. Users should be able to run it without official Talkrax
accounts or access to the private repository. Android, iOS, proprietary paid
artwork and the official service's development tools are outside that edition's
requested scope.

## Security status
Current hosted text messages and attachments are not fully end-to-end encrypted.
Persistent MLS and file-encryption components are under development; they are
not a completed chat feature. Call-media encryption is a separate capability.
Discord migration is not released. See [release status](docs/RELEASE_STATUS.md).

Do not put passwords, authenticator codes, bot tokens, private conversations or
server configuration secrets into GitHub issues.

## Rights
Public visibility does not grant a licence to modify or redistribute the private
application or paid artwork. Released binaries and third-party components must
carry their applicable licence terms. Normal server administration and
configuration are part of the intended self-hosting use.
