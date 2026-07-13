import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:web_socket_channel/web_socket_channel.dart';

import '../api.dart';
import '../main.dart';
import '../models.dart';

class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  List<Conversation> _conversations = [];
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final data = await api.get('/conversations/') as List;
      setState(() {
        _conversations = data.map((j) => Conversation.fromJson(j)).toList();
        _loading = false;
      });
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('الرسائل')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _load,
              child: _conversations.isEmpty
                  ? ListView(children: const [
                      SizedBox(height: 120),
                      Center(child: Text('لا محادثات بعد.')),
                    ])
                  : ListView.builder(
                      itemCount: _conversations.length,
                      itemBuilder: (context, i) {
                        final c = _conversations[i];
                        return ListTile(
                          leading: CircleAvatar(
                            backgroundColor: primaryBlue,
                            backgroundImage: c.otherUser.avatar != null
                                ? NetworkImage(
                                    api.mediaUrl(c.otherUser.avatar)!)
                                : null,
                            child: c.otherUser.avatar == null
                                ? Text(
                                    c.otherUser.displayName.characters.first,
                                    style:
                                        const TextStyle(color: Colors.white))
                                : null,
                          ),
                          title: Text(c.otherUser.displayName),
                          subtitle: Text(c.lastMessageText,
                              maxLines: 1, overflow: TextOverflow.ellipsis),
                          trailing: c.unreadCount > 0
                              ? Badge(label: Text('${c.unreadCount}'))
                              : null,
                          onTap: () async {
                            await Navigator.push(
                              context,
                              MaterialPageRoute(
                                builder: (_) => ChatScreen(conversation: c),
                              ),
                            );
                            _load();
                          },
                        );
                      },
                    ),
            ),
    );
  }
}

class ChatScreen extends StatefulWidget {
  final Conversation conversation;
  const ChatScreen({super.key, required this.conversation});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final List<Message> _messages = [];
  final _controller = TextEditingController();
  final _scroll = ScrollController();
  WebSocketChannel? _channel;
  bool _typing = false;

  @override
  void initState() {
    super.initState();
    _load();
    _connect();
  }

  Future<void> _load() async {
    final data =
        await api.get('/conversations/${widget.conversation.id}/messages/');
    setState(() {
      _messages
        ..clear()
        ..addAll((data['results'] as List).map((j) => Message.fromJson(j)));
    });
    _scrollDown();
    api.post('/conversations/${widget.conversation.id}/read/');
  }

  void _connect() {
    _channel = WebSocketChannel.connect(
      Uri.parse(api.wsUrl('/ws/chat/${widget.conversation.id}/')),
    );
    _channel!.stream.listen(
      (raw) {
        final msg = jsonDecode(raw);
        if (msg['type'] == 'message') {
          final m = Message.fromJson(msg['data']);
          if (!_messages.any((x) => x.id == m.id)) {
            setState(() {
              _typing = false;
              _messages.add(m);
            });
            _scrollDown();
          }
        } else if (msg['type'] == 'typing') {
          setState(() => _typing = true);
          Future.delayed(const Duration(seconds: 3), () {
            if (mounted) setState(() => _typing = false);
          });
        }
      },
      onDone: () => Future.delayed(const Duration(seconds: 4), () {
        if (mounted) _connect();
      }),
      onError: (_) {},
    );
  }

  void _scrollDown() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.jumpTo(_scroll.position.maxScrollExtent);
      }
    });
  }

  void _send() {
    final text = _controller.text.trim();
    if (text.isEmpty) return;
    _channel?.sink.add(jsonEncode({'type': 'message', 'text': text}));
    _controller.clear();
  }

  @override
  void dispose() {
    _channel?.sink.close();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final myId = context.read<AuthState>().me!.id;
    return Scaffold(
      appBar: AppBar(title: Text(widget.conversation.otherUser.displayName)),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scroll,
              padding: const EdgeInsets.all(12),
              itemCount: _messages.length + (_typing ? 1 : 0),
              itemBuilder: (context, i) {
                if (_typing && i == _messages.length) {
                  return const Align(
                    alignment: AlignmentDirectional.centerEnd,
                    child: Padding(
                      padding: EdgeInsets.all(8),
                      child: Text('يكتب…'),
                    ),
                  );
                }
                final m = _messages[i];
                final mine = m.sender == myId;
                return Align(
                  alignment: mine
                      ? AlignmentDirectional.centerStart
                      : AlignmentDirectional.centerEnd,
                  child: Container(
                    margin: const EdgeInsets.symmetric(vertical: 3),
                    padding: const EdgeInsets.symmetric(
                        horizontal: 14, vertical: 9),
                    constraints: BoxConstraints(
                        maxWidth: MediaQuery.of(context).size.width * 0.75),
                    decoration: BoxDecoration(
                      color: mine
                          ? primaryBlue
                          : Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      m.text,
                      style: TextStyle(color: mine ? Colors.white : null),
                    ),
                  ),
                );
              },
            ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(12, 4, 12, 8),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      onSubmitted: (_) => _send(),
                      onChanged: (_) =>
                          _channel?.sink.add(jsonEncode({'type': 'typing'})),
                      decoration: const InputDecoration(
                        hintText: 'اكتب رسالة…',
                        border: OutlineInputBorder(),
                        isDense: true,
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: _send,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
