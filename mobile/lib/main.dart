import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:provider/provider.dart';

import 'api.dart';
import 'models.dart';
import 'screens/home.dart';
import 'screens/login.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await api.loadTokens();
  runApp(const FocusApp());
}

/// Authentication state shared across the app.
class AuthState extends ChangeNotifier {
  User? me;
  bool loading = true;

  AuthState() {
    _bootstrap();
  }

  Future<void> _bootstrap() async {
    if (api.hasToken) {
      try {
        me = User.fromJson(await api.get('/users/me/'));
      } catch (_) {
        await api.clearTokens();
      }
    }
    loading = false;
    notifyListeners();
  }

  Future<void> login(String username, String password) async {
    await api.login(username, password);
    me = User.fromJson(await api.get('/users/me/'));
    notifyListeners();
  }

  Future<void> logout() async {
    await api.clearTokens();
    me = null;
    notifyListeners();
  }
}

// Safi ceramic blue identity — matches the web design system.
const primaryBlue = Color(0xFF2149C7);
const tealAccent = Color(0xFF0F9E9E);
const amberAccent = Color(0xFFE8930C);

class FocusApp extends StatelessWidget {
  const FocusApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AuthState(),
      child: MaterialApp(
        title: 'فوكس سوشيال',
        debugShowCheckedModeBanner: false,
        locale: const Locale('ar'),
        supportedLocales: const [Locale('ar')],
        localizationsDelegates: const [
          GlobalMaterialLocalizations.delegate,
          GlobalWidgetsLocalizations.delegate,
          GlobalCupertinoLocalizations.delegate,
        ],
        theme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: primaryBlue,
            secondary: tealAccent,
            tertiary: amberAccent,
          ),
        ),
        darkTheme: ThemeData(
          useMaterial3: true,
          colorScheme: ColorScheme.fromSeed(
            seedColor: primaryBlue,
            brightness: Brightness.dark,
            secondary: tealAccent,
            tertiary: amberAccent,
          ),
        ),
        home: Consumer<AuthState>(
          builder: (context, auth, _) {
            if (auth.loading) {
              return const Scaffold(
                body: Center(child: CircularProgressIndicator()),
              );
            }
            return auth.me == null ? const LoginScreen() : const HomeScreen();
          },
        ),
      ),
    );
  }
}
