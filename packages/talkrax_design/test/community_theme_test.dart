// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:talkrax_design/talkrax_design.dart';

double contrast(Color a, Color b) {
  final x = a.computeLuminance(), y = b.computeLuminance();
  return ((x > y ? x : y) + 0.05) / ((x < y ? x : y) + 0.05);
}

void main() {
  for (final brightness in Brightness.values) {
    for (final accessible in [false, true]) {
      testWidgets(
        'Community controls render without assets: $brightness high contrast $accessible',
        (tester) async {
          var activated = false;
          final theme = CommunityTheme.build(
            brightness: brightness,
            highContrast: accessible,
            reducedMotion: true,
          );
          await tester.pumpWidget(
            MaterialApp(
              theme: theme,
              themeAnimationDuration: Duration.zero,
              home: Scaffold(
                body: Column(
                  children: [
                    const Text('Independent community'),
                    const TextField(
                      decoration: InputDecoration(labelText: 'Message'),
                    ),
                    FilledButton(
                      onPressed: () => activated = true,
                      child: const Text('Send'),
                    ),
                  ],
                ),
              ),
            ),
          );
          await tester.enterText(find.byType(TextField), 'A community message');
          await tester.tap(find.text('Send'));
          await tester.pump();
          expect(activated, isTrue);
          expect(find.text('A community message'), findsOneWidget);
          expect(tester.takeException(), isNull);
          expect(
            contrast(
              theme.colorScheme.onSurface,
              theme.scaffoldBackgroundColor,
            ),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            contrast(theme.colorScheme.onPrimary, theme.colorScheme.primary),
            greaterThanOrEqualTo(4.5),
          );
          expect(
            theme.filledButtonTheme.style!.animationDuration,
            Duration.zero,
          );
          expect(theme.splashFactory, NoSplash.splashFactory);
        },
      );
    }
  }

  test('accent customization changes colours without proprietary assets', () {
    final blue = CommunityTheme.build();
    final orange = CommunityTheme.build(accent: Colors.deepOrange);
    expect(blue.colorScheme.primary, isNot(orange.colorScheme.primary));
  });
}
