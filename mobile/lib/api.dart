/// REST + WebSocket client for the Focus Social backend.
///
/// Point [baseUrl] at the server (defaults work with `adb reverse` or the
/// Android emulator's 10.0.2.2 alias). Override at build time:
///   flutter run --dart-define=BASE_URL=http://192.168.1.10
library;

import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

const String baseUrl =
    String.fromEnvironment('BASE_URL', defaultValue: 'http://10.0.2.2:8000');

class ApiException implements Exception {
  final int status;
  final String message;
  ApiException(this.status, this.message);
  @override
  String toString() => message;
}

class ApiClient {
  String? _access;
  String? _refresh;

  Future<void> loadTokens() async {
    final prefs = await SharedPreferences.getInstance();
    _access = prefs.getString('access');
    _refresh = prefs.getString('refresh');
  }

  bool get hasToken => _access != null;
  String? get accessToken => _access;

  Future<void> _saveTokens(String access, [String? refresh]) async {
    _access = access;
    if (refresh != null) _refresh = refresh;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access', access);
    if (refresh != null) await prefs.setString('refresh', refresh);
  }

  Future<void> clearTokens() async {
    _access = null;
    _refresh = null;
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access');
    await prefs.remove('refresh');
  }

  Future<void> login(String username, String password) async {
    final res = await http.post(
      Uri.parse('$baseUrl/api/auth/token/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'username': username, 'password': password}),
    );
    if (res.statusCode != 200) {
      throw ApiException(res.statusCode, 'بيانات الدخول غير صحيحة');
    }
    final data = jsonDecode(res.body);
    await _saveTokens(data['access'], data['refresh']);
  }

  Future<bool> _tryRefresh() async {
    if (_refresh == null) return false;
    final res = await http.post(
      Uri.parse('$baseUrl/api/auth/refresh/'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'refresh': _refresh}),
    );
    if (res.statusCode != 200) return false;
    await _saveTokens(jsonDecode(res.body)['access']);
    return true;
  }

  Future<dynamic> _request(
    String method,
    String path, {
    Object? body,
    bool retried = false,
  }) async {
    final headers = <String, String>{
      if (_access != null) 'Authorization': 'Bearer $_access',
      if (body != null) 'Content-Type': 'application/json',
    };
    final uri = Uri.parse('$baseUrl/api$path');
    late http.Response res;
    switch (method) {
      case 'GET':
        res = await http.get(uri, headers: headers);
      case 'POST':
        res = await http.post(uri,
            headers: headers, body: body == null ? null : jsonEncode(body));
      case 'PATCH':
        res = await http.patch(uri, headers: headers, body: jsonEncode(body));
      case 'DELETE':
        res = await http.delete(uri, headers: headers);
    }
    if (res.statusCode == 401 && !retried && await _tryRefresh()) {
      return _request(method, path, body: body, retried: true);
    }
    if (res.statusCode >= 400) {
      String message = 'خطأ (${res.statusCode})';
      try {
        final data = jsonDecode(utf8.decode(res.bodyBytes));
        if (data is Map && data['detail'] != null) message = data['detail'];
      } catch (_) {}
      throw ApiException(res.statusCode, message);
    }
    if (res.statusCode == 204 || res.bodyBytes.isEmpty) return null;
    return jsonDecode(utf8.decode(res.bodyBytes));
  }

  Future<dynamic> get(String path) => _request('GET', path);
  Future<dynamic> post(String path, [Object? body]) =>
      _request('POST', path, body: body ?? {});
  Future<dynamic> patch(String path, Object body) =>
      _request('PATCH', path, body: body);
  Future<dynamic> delete(String path) => _request('DELETE', path);

  /// ws:// URL carrying the JWT, matching the backend's Channels middleware.
  String wsUrl(String path) {
    final ws = baseUrl.replaceFirst('http', 'ws');
    return '$ws$path?token=$_access';
  }

  /// Absolute URL for media paths returned by the API.
  String? mediaUrl(String? path) {
    if (path == null) return null;
    return path.startsWith('http') ? path : '$baseUrl$path';
  }
}

final api = ApiClient();
