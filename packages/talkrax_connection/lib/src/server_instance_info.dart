// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'server_connection.dart';

/// Operator-supplied information, not a certification of the remote service.
class ServerInstanceInfo {
  const ServerInstanceInfo({
    required this.name,
    required this.operatorName,
    required this.independent,
    this.contactEmail,
    this.privacyUrl,
    this.termsUrl,
  });
  final String name;
  final String operatorName;
  final bool independent;
  final String? contactEmail;
  final Uri? privacyUrl;
  final Uri? termsUrl;

  factory ServerInstanceInfo.fromJson(
    Map<String, dynamic> json,
    ServerConnection connection,
  ) {
    String? field(String key) {
      final value = json[key];
      if (value == null) return null;
      if (value is! String ||
          value.trim().isEmpty ||
          value.length > 200 ||
          value.runes.any((r) => r < 32 || r == 127)) {
        throw const FormatException(
          'This server returned invalid operator information.',
        );
      }
      return value;
    }

    Uri? policy(String key) {
      final value = json[key];
      if (value == null) return null;
      final uri = value is String && value.length <= 2048
          ? Uri.tryParse(value)
          : null;
      if (uri == null ||
          uri.scheme != 'https' ||
          uri.host.isEmpty ||
          uri.userInfo.isNotEmpty) {
        throw const FormatException(
          'This server returned an invalid policy address.',
        );
      }
      return uri;
    }

    if (json['application'] != 'Talkrax' ||
        json['apiVersion'] != 1 ||
        !{'Independent', 'Hosted'}.contains(json['mode'])) {
      throw const FormatException(
        'This address does not provide a compatible Talkrax server.',
      );
    }
    // A remote server cannot label itself as the official Talkrax service.
    final independent = !connection.isOfficial;
    final name = field('name');
    final operatorName = field('operatorName');
    final email = field('contactEmail');
    final privacy = policy('privacyUrl');
    final terms = policy('termsUrl');
    if (name == null ||
        (independent &&
            (operatorName == null ||
                email == null ||
                privacy == null ||
                terms == null))) {
      throw const FormatException(
        'This server has not published its operator, contact and policies.',
      );
    }
    return ServerInstanceInfo(
      name: name,
      independent: independent,
      operatorName: operatorName ?? 'Talkrax',
      contactEmail: email,
      privacyUrl: privacy,
      termsUrl: terms,
    );
  }
}

class ServerInstanceProbe {
  ServerInstanceProbe({this._client});
  final http.Client? _client;
  Future<ServerInstanceInfo> inspect(ServerConnection connection) async {
    final client = _client ?? http.Client();
    try {
      return await _inspect(
        client,
        connection,
      ).timeout(const Duration(seconds: 10));
    } finally {
      if (_client == null) client.close();
    }
  }

  Future<ServerInstanceInfo> _inspect(
    http.Client client,
    ServerConnection connection,
  ) async {
    final request =
        http.Request(
            'GET',
            Uri.parse(connection.origin).resolve('/api/public/instance'),
          )
          ..followRedirects = false
          ..headers['Accept'] = 'application/json';
    final response = await client.send(request);
    if (response.statusCode != 200 ||
        !(response.headers['content-type'] ?? '').toLowerCase().startsWith(
          'application/json',
        )) {
      throw const FormatException(
        'The server could not provide its Talkrax information.',
      );
    }
    const maximumBytes = 32768;
    if ((response.contentLength ?? 0) > maximumBytes) {
      throw const FormatException('The server information is too large.');
    }
    final bytes = <int>[];
    await for (final chunk in response.stream) {
      if (bytes.length + chunk.length > maximumBytes) {
        throw const FormatException('The server information is too large.');
      }
      bytes.addAll(chunk);
    }
    final json = jsonDecode(utf8.decode(bytes));
    if (json is! Map<String, dynamic>) {
      throw const FormatException(
        'The server information has an invalid format.',
      );
    }
    return ServerInstanceInfo.fromJson(json, connection);
  }
}
