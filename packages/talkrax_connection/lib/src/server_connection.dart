// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

import 'dart:convert';
import 'package:crypto/crypto.dart';
import 'token_storage_backend.dart';

/// One server origin is one authentication and private-key namespace.
class ServerConnection {
  ServerConnection._(this.origin);
  final String origin;

  factory ServerConnection.parse(String value) {
    final uri = Uri.tryParse(value.trim());
    if (uri == null ||
        !uri.hasAuthority ||
        uri.host.isEmpty ||
        uri.userInfo.isNotEmpty ||
        uri.hasQuery ||
        uri.hasFragment ||
        (uri.path.isNotEmpty && uri.path != '/')) {
      throw const FormatException(
        'Enter the server address only, without a path, login or query.',
      );
    }
    final loopback = {
      'localhost',
      '127.0.0.1',
      '[::1]',
      '::1',
    }.contains(uri.host.toLowerCase());
    if (uri.scheme != 'https' && !(uri.scheme == 'http' && loopback)) {
      throw const FormatException(
        'Use HTTPS. HTTP is allowed only for a server on this device.',
      );
    }
    if (uri.port < 1 || uri.port > 65535) {
      throw const FormatException('The server port is invalid.');
    }
    return ServerConnection._(uri.origin);
  }

  bool get isOfficial => origin == 'https://talkrax.com';
  String get storageNamespace =>
      'talkrax.instance.${sha256.convert(utf8.encode(origin))}.';
  Uri get releaseManifest =>
      Uri.parse(origin).resolve('/releases/release-manifest.json');

  TokenStorageBackend isolate(TokenStorageBackend backend) =>
      isOfficial ? backend : InstanceStorageBackend(backend, storageNamespace);
}

class InstanceStorageBackend implements TokenStorageBackend {
  InstanceStorageBackend(this.backend, this.namespace);
  final TokenStorageBackend backend;
  final String namespace;
  @override
  Future<String?> read({required String key}) =>
      backend.read(key: namespace + key);
  @override
  Future<void> write({required String key, required String value}) =>
      backend.write(key: namespace + key, value: value);
  @override
  Future<void> delete({required String key}) =>
      backend.delete(key: namespace + key);
}

class ServerConnectionPreferences {
  ServerConnectionPreferences(this.backend);
  final TokenStorageBackend backend;
  static const _selection = 'talkrax.selected_server.v1';

  Future<ServerConnection> load(String defaultOrigin) async =>
      ServerConnection.parse(
        await backend.read(key: _selection) ?? defaultOrigin,
      );

  Future<void> save(ServerConnection connection) =>
      backend.write(key: _selection, value: connection.origin);
}
