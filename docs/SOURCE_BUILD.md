# Build the Community source libraries

These two libraries build from this public repository without access to the
private repository or a Talkrax account. They are not a runnable chat application
or server. For the existing compiled preview, use SELF_HOSTING.md and
CLIENT_INSTALLATION.md.

## Requirements and clone

Install Flutter 3.44.1 (includes Dart 3.12) using the official
[Flutter installation instructions](https://docs.flutter.dev/install).
The connection library alone needs only Dart 3.12.

```sh
git clone https://github.com/helldragonpz/talkrax-community.git
cd talkrax-community
```

The source is platform independent. Verification for this release ran on Linux;
this does not certify native Windows, macOS or iPhone applications.

## Design and accessibility

```sh
cd packages/talkrax_design
flutter pub get
flutter analyze
flutter test
```

Five tests exercise light/dark and high-contrast controls, custom accents and
reduced-motion styling. No commercial assets are required. Application-level
animations must separately respect the user's reduced-motion preference.
See the package README for a MaterialApp example.

## Server connection and discovery

From the repository root:

```sh
cd packages/talkrax_connection
dart pub get
dart analyze
dart test
```

Six tests cover origin validation, separate per-server token storage, preserving
the existing hosted namespace, operator metadata validation, redirects and
oversized responses. HTTP responses and credentials in tests are synthetic.
The library does not require contact with the official Talkrax service.

A consuming application must implement TokenStorageBackend with its operating
system's secure credential store and show the operator information for user
review before selecting a server. This package does not implement secure storage,
E2EE, chat, media transport or server authentication.

## Add a library to your app

Use a path dependency on a local checkout, or a pinned Git dependency:

```yaml
dependencies:
  talkrax_design:
    git:
      url: https://github.com/helldragonpz/talkrax-community.git
      ref: community-modules-2026.09.27.1
      path: packages/talkrax_design
  talkrax_connection:
    git:
      url: https://github.com/helldragonpz/talkrax-community.git
      ref: community-modules-2026.09.27.1
      path: packages/talkrax_connection
```

Run your app's package resolution and retain its lockfile for repeatable builds.
Both components are AGPL-3.0-only; review LICENSING.md before incorporating them.

## Scope and evidence

The reviewed source file inventory and SHA-256 hashes are in
[evidence/community-source-20260927.json](evidence/community-source-20260927.json).
Generated package caches, build output and private source/history are excluded.
The full independent client/server still needs a dedicated application entry
point, removal of commerce/hosted UI dependencies, packaging and acceptance tests.
See RELEASE_STATUS.md for released features and remaining work.
