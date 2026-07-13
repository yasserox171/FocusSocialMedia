import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../api.dart';
import 'feed.dart';
import 'messages.dart';
import 'notifications.dart';
import 'profile.dart';

/// Bottom-navigation shell + global notifications socket (snackbar + badge).
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _tab = 0;
  int _unread = 0;
  WebSocketChannel? _channel;

  @override
  void initState() {
    super.initState();
    _loadUnread();
    _connect();
  }

  Future<void> _loadUnread() async {
    try {
      final data = await api.get('/notifications/unread-count/');
      if (mounted) setState(() => _unread = data['count']);
    } catch (_) {}
  }

  void _connect() {
    try {
      _channel =
          WebSocketChannel.connect(Uri.parse(api.wsUrl('/ws/notifications/')));
      _channel!.stream.listen(
        (raw) {
          final msg = jsonDecode(raw);
          if (msg['type'] == 'notification' && mounted) {
            setState(() => _unread += 1);
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text('🔔 ${msg['data']['text']}')),
            );
          }
        },
        onDone: () => Future.delayed(const Duration(seconds: 5), () {
          if (mounted) _connect();
        }),
        onError: (_) {},
      );
    } catch (_) {}
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final screens = [
      const FeedScreen(),
      const MessagesScreen(),
      NotificationsScreen(onOpened: () => setState(() => _unread = 0)),
      const ProfileScreen(),
    ];
    return Scaffold(
      body: screens[_tab],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _tab,
        onDestinationSelected: (i) => setState(() => _tab = i),
        destinations: [
          const NavigationDestination(icon: Icon(Icons.home_outlined), label: 'الرئيسية'),
          const NavigationDestination(icon: Icon(Icons.chat_bubble_outline), label: 'الرسائل'),
          NavigationDestination(
            icon: Badge(
              isLabelVisible: _unread > 0,
              label: Text('$_unread'),
              child: const Icon(Icons.notifications_outlined),
            ),
            label: 'الإشعارات',
          ),
          const NavigationDestination(icon: Icon(Icons.person_outline), label: 'حسابي'),
        ],
      ),
    );
  }
}
