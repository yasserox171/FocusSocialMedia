import 'package:flutter/material.dart';

import '../api.dart';
import '../models.dart';

class NotificationsScreen extends StatefulWidget {
  final VoidCallback? onOpened;
  const NotificationsScreen({super.key, this.onOpened});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<AppNotification> _items = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
    widget.onOpened?.call();
    api.post('/notifications/read-all/');
  }

  Future<void> _load() async {
    try {
      final data = await api.get('/notifications/');
      setState(() {
        _items = (data['results'] as List)
            .map((j) => AppNotification.fromJson(j))
            .toList();
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  IconData _icon(String kind) => switch (kind) {
        'like' => Icons.favorite,
        'message' => Icons.chat_bubble,
        _ => Icons.article,
      };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الإشعارات')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _items.isEmpty
                  ? ListView(children: const [
                      SizedBox(height: 120),
                      Center(child: Text('لا إشعارات بعد.')),
                    ])
                  : ListView.builder(
                      itemCount: _items.length,
                      itemBuilder: (context, i) {
                        final n = _items[i];
                        return ListTile(
                          leading: Icon(_icon(n.kind)),
                          title: Text(n.text),
                          tileColor: n.isRead
                              ? null
                              : Theme.of(context)
                                  .colorScheme
                                  .primaryContainer
                                  .withOpacity(0.3),
                        );
                      },
                    ),
            ),
    );
  }
}
