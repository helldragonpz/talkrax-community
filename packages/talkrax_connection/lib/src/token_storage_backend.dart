// Copyright (c) 2026 Alexandar Penev.
// SPDX-License-Identifier: AGPL-3.0-only

abstract interface class TokenStorageBackend {
  Future<void> write({required String key, required String value});
  Future<String?> read({required String key});
  Future<void> delete({required String key});
}
