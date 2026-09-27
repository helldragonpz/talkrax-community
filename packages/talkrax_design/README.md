# Talkrax Community design

A standalone Flutter package containing an asset-free neutral Community theme
and generic theme contracts. It includes dark/light appearances, high contrast,
custom accent colours and reduced-motion control styling.

This package is not the complete Talkrax client or server. It contains no official
commercial theme catalogue, premium artwork, mascot, stickers, marketplace or
billing implementation. It builds without the private Talkrax repository.

## Use
From a Flutter project, add a path dependency pointing to this package, then:

```dart
import 'package:flutter/material.dart';
import 'package:talkrax_design/talkrax_design.dart';

MaterialApp(
  theme: CommunityTheme.build(brightness: Brightness.light),
  darkTheme: CommunityTheme.build(),
  highContrastTheme: CommunityTheme.build(
    brightness: Brightness.light, highContrast: true),
  highContrastDarkTheme: CommunityTheme.build(highContrast: true),
  home: YourHomePage(),
);
```

Pass the device/user reduced-motion preference to reducedMotion. The theme
disables its own control/splash motion; the application must separately honour
that preference for its page, list and media animations.

Generic theme contracts allow an application to supply its own image provider.
No proprietary resolver, asset path or image is imported by the contracts.

## Verify
With Flutter 3.44.1 / Dart 3.12 or a compatible newer SDK:

```sh
flutter pub get
flutter analyze
flutter test
```

Tests edit a field and activate a button in each appearance, check text/button
contrast and confirm reduced-motion styling. This is component-level coverage,
not Windows/macOS/iPhone device acceptance.

## Licence
Copyright (c) 2026 Alexandar Penev. This package's authored source and tests are
available under AGPL-3.0-only; see LICENSE. You may modify, fork and redistribute
under that licence, including commercially. No warranty is provided.
Flutter/Dart and dependencies retain their own licences and are not vendored.
This licence does not grant rights to excluded official artwork or trademarks.
It does not relicense the separately distributed proprietary binary preview.
