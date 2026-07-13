import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../api.dart';
import '../main.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _username = TextEditingController();
  final _password = TextEditingController();
  final _server = TextEditingController();
  String? _error;
  bool _busy = false;

  @override
  void initState() {
    super.initState();
    _server.text = baseUrl;
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      final auth = context.read<AuthState>();
      if (_server.text.trim().isNotEmpty && _server.text.trim() != baseUrl) {
        await api.setBaseUrl(_server.text);
      }
      await auth.login(
            _username.text.trim(),
            _password.text,
          );
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(28),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 380),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                Text(
                  'فوكس.سوشيال',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: primaryBlue,
                        fontWeight: FontWeight.bold,
                      ),
                ),
                const SizedBox(height: 4),
                Text(
                  'المنصة الداخلية لأعضاء جمعية فوكس — آسفي',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                const SizedBox(height: 28),
                if (_error != null) ...[
                  Text(_error!,
                      style: TextStyle(
                          color: Theme.of(context).colorScheme.error)),
                  const SizedBox(height: 12),
                ],
                TextField(
                  controller: _username,
                  decoration: const InputDecoration(
                    labelText: 'اسم المستخدم',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _password,
                  obscureText: true,
                  onSubmitted: (_) => _submit(),
                  decoration: const InputDecoration(
                    labelText: 'كلمة المرور',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 20),
                FilledButton(
                  onPressed: _busy ? null : _submit,
                  child: Text(_busy ? 'جارٍ الدخول…' : 'دخول'),
                ),
                const SizedBox(height: 16),
                ExpansionTile(
                  title: const Text('إعدادات الخادم',
                      style: TextStyle(fontSize: 13)),
                  tilePadding: EdgeInsets.zero,
                  childrenPadding: const EdgeInsets.only(bottom: 8),
                  children: [
                    TextField(
                      controller: _server,
                      textDirection: TextDirection.ltr,
                      decoration: const InputDecoration(
                        labelText: 'عنوان الخادم',
                        hintText: 'http://192.168.1.10',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
