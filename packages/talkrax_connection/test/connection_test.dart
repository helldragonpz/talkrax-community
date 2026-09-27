// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:test/test.dart';
import 'package:talkrax_connection/talkrax_connection.dart';

class MemoryStorage implements TokenStorageBackend {
  final values = <String, String>{};
  @override
  Future<String?> read({required String key}) async => values[key];
  @override
  Future<void> write({required String key, required String value}) async {
    values[key] = value;
  }

  @override
  Future<void> delete({required String key}) async {
    values.remove(key);
  }
}

Map<String, dynamic> metadata() => {
  'application': 'Talkrax',
  'apiVersion': 1,
  'name': 'Our Guild',
  'mode': 'Independent',
  'operatorName': 'Guild Operator',
  'contactEmail': 'operator@example.invalid',
  'privacyUrl': 'https://guild.example/privacy',
  'termsUrl': 'https://guild.example/terms',
};

void main() {
  test('requires HTTPS, validates origins and normalizes default ports', () {
    for (final input in [
      'http://guild.example',
      'https://u:p@guild.example',
      'https://guild.example/api',
      'https://guild.example/?secret=x',
      'https://guild.example/#x',
      'file:///tmp/a',
      '//guild.example',
      'https://guild.example:0',
    ]) {
      expect(() => ServerConnection.parse(input), throwsFormatException);
    }
    expect(
      ServerConnection.parse('https://GUILD.EXAMPLE:443/').origin,
      'https://guild.example',
    );
    expect(
      ServerConnection.parse('http://[::1]:18080').origin,
      'http://[::1]:18080',
    );
  });

  test(
    'server namespaces preserve old hosted tokens and isolate other origins',
    () async {
      final backend = MemoryStorage();
      final hosted = ServerConnection.parse(
        'https://talkrax.com',
      ).isolate(backend);
      final alpha = ServerConnection.parse(
        'https://alpha.example',
      ).isolate(backend);
      final beta = ServerConnection.parse(
        'https://beta.example',
      ).isolate(backend);
      await hosted.write(key: 'session', value: 'synthetic-hosted');
      expect(await alpha.read(key: 'session'), isNull);
      await alpha.write(key: 'session', value: 'synthetic-alpha');
      expect(await beta.read(key: 'session'), isNull);
      await alpha.delete(key: 'session');
      expect(await hosted.read(key: 'session'), 'synthetic-hosted');
      expect(await alpha.read(key: 'session'), isNull);
      expect(
        ServerConnection.parse('https://alpha.example').releaseManifest.host,
        'alpha.example',
      );
    },
  );

  test(
    'selected origin persists separately from authentication material',
    () async {
      final backend = MemoryStorage();
      await ServerConnectionPreferences(
        backend,
      ).save(ServerConnection.parse('https://guild.example'));
      expect(
        (await ServerConnectionPreferences(
          backend,
        ).load('https://fallback.example')).origin,
        'https://guild.example',
      );
      expect(backend.values.values.toList(), ['https://guild.example']);
    },
  );

  test(
    'metadata probes use the chosen origin without credentials or redirects',
    () async {
      final probe = ServerInstanceProbe(
        client: MockClient((request) async {
          expect(
            request.url.toString(),
            'https://guild.example/api/public/instance',
          );
          expect(request.followRedirects, isFalse);
          expect(request.headers.keys, isNot(contains('authorization')));
          expect(request.headers.keys, isNot(contains('cookie')));
          return http.Response(
            jsonEncode(metadata()),
            200,
            headers: {'content-type': 'application/json'},
          );
        }),
      );
      expect(
        (await probe.inspect(
          ServerConnection.parse('https://guild.example'),
        )).operatorName,
        'Guild Operator',
      );
    },
  );

  test(
    'remote services cannot claim official status or omit operator policies',
    () {
      final connection = ServerConnection.parse('https://guild.example');
      expect(
        ServerInstanceInfo.fromJson(
          metadata()..['mode'] = 'Hosted',
          connection,
        ).independent,
        isTrue,
      );
      for (final name in [
        'operatorName',
        'contactEmail',
        'privacyUrl',
        'termsUrl',
      ]) {
        expect(
          () =>
              ServerInstanceInfo.fromJson(metadata()..remove(name), connection),
          throwsFormatException,
        );
      }
      expect(
        () => ServerInstanceInfo.fromJson(
          metadata()..['termsUrl'] = 'javascript:alert(1)',
          connection,
        ),
        throwsFormatException,
      );
    },
  );

  test(
    'redirect, HTML, unexpected schema and oversized metadata are rejected',
    () async {
      for (final response in [
        http.Response(
          '',
          302,
          headers: {'location': 'https://foreign.example'},
        ),
        http.Response('<html/>', 200, headers: {'content-type': 'text/html'}),
        http.Response('[]', 200, headers: {'content-type': 'application/json'}),
        http.Response(
          'x' * 32769,
          200,
          headers: {'content-type': 'application/json'},
        ),
      ]) {
        await expectLater(
          ServerInstanceProbe(
            client: MockClient((_) async => response),
          ).inspect(ServerConnection.parse('https://guild.example')),
          throwsFormatException,
        );
      }
    },
  );
}
