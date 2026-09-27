# Talkrax Community

Talkrax is a gaming community app for chat, voice and screen sharing.

An **independent Linux server preview** is now available as compiled server
images and operator tools. It runs its own accounts, database, file storage,
SMTP configuration, media service and administrator console.

The installed Linux client (build 36) has passed server selection, MFA sign-in
and session recovery with the official hosted service unreachable.

[Download the server preview](https://github.com/helldragonpz/talkrax-community/releases/tag/server-preview-2026.09.20.1)
- [Install and operate your own server](docs/SELF_HOSTING.md)
- [Install and connect the Linux client](docs/CLIENT_INSTALLATION.md)
- [Release status and tested limits](docs/RELEASE_STATUS.md)
- [Update and recover an independent server](docs/UPDATES.md)
- [Binary licence](BINARY-LICENCE.txt)

This repository contains the binary preview, operator tools and two independently
buildable **AGPL-3.0-only source libraries**:
- [Community design](packages/talkrax_design): neutral light/dark themes, accessibility
  settings and generic theme contracts; no paid artwork.
- [Server connection](packages/talkrax_connection): server address validation,
  operator discovery and separate credential namespaces.

[Build and use the source libraries](docs/SOURCE_BUILD.md).
These are components, not the complete client/server source release. The binary
preview retains its separate proprietary licence. Licence scope and excluded
assets are explained in [LICENSING.md](LICENSING.md).

The preview is not the completed Windows/Linux edition. Windows packaging,
public-network media/TURN acceptance and the open-source application split remain open.
Application-image upgrade and failure-recovery tools are now tested and available
through the [operator-tools release](https://github.com/helldragonpz/talkrax-community/releases/tag/operator-tools-2026.09.27.1).
Private messaging/file E2EE and Discord migration are not released.
Independent operators can currently access stored message/file content and must
provide their own privacy information and policies.

The official hosted service remains available at [talkrax.com](https://talkrax.com).
