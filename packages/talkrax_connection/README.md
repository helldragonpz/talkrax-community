# Talkrax Community connection
Standalone Dart code for validating a server origin, probing operator information
and isolating authentication storage per server. No Flutter, private repository,
hosted login, payment provider or proprietary asset is required.

This is a connection library, not a complete client, server, secure storage
implementation or messaging/encryption protocol. Implement TokenStorageBackend
using the operating system's secure credential store. The in-memory backend in
tests is for synthetic tests only.

ServerConnection.parse requires HTTPS except device loopback, rejects embedded
credentials/paths/queries, and canonicalizes the origin. Independent origins use
separate storage namespaces; the official origin retains its historical namespace
so existing hosted sessions do not disappear. Merely probing a server never moves
credentials to it. Changing the saved selection does not copy stored tokens.

ServerInstanceProbe requests only the selected origin's public instance metadata,
does not add authentication headers, disables redirects, bounds response size,
and requires compatible application/operator/policy information. Information is
operator-supplied, not a Talkrax certification. The consuming app must show that
information for user review before accepting a new server. The included tests use
mock HTTP responses and never contact the official hosted service.

## Verify
With Dart 3.12 or a compatible newer SDK:
```sh
dart pub get
dart analyze
dart test
```

## Licence
Copyright (c) 2026 Alexandar Penev. Authored code/tests: AGPL-3.0-only, see LICENSE.
Modification, redistribution, forks and commercial use are permitted under that
licence. No warranty. Dependencies retain their own licences and are not vendored.
This licence does not cover separate proprietary application binaries or artwork.
