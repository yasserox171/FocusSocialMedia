import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../api.dart';
import '../main.dart';
import '../models.dart';
import '../widgets/post_card.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  List<Post> _posts = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final me = context.read<AuthState>().me!;
    final data = await api.get('/posts/?author=${me.id}');
    setState(() {
      _posts = (data['results'] as List).map((j) => Post.fromJson(j)).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthState>();
    final me = auth.me!;
    return Scaffold(
      appBar: AppBar(
        title: const Text('حسابي'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            tooltip: 'خروج',
            onPressed: auth.logout,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          children: [
            const SizedBox(height: 20),
            CircleAvatar(
              radius: 42,
              backgroundColor: primaryBlue,
              backgroundImage: me.avatar != null
                  ? NetworkImage(api.mediaUrl(me.avatar)!)
                  : null,
              child: me.avatar == null
                  ? Text(me.displayName.characters.first,
                      style: const TextStyle(fontSize: 32, color: Colors.white))
                  : null,
            ),
            const SizedBox(height: 10),
            Center(
              child: Text(me.displayName,
                  style: Theme.of(context).textTheme.titleLarge),
            ),
            if (me.bio.isNotEmpty)
              Center(
                child: Text(me.bio,
                    style: Theme.of(context).textTheme.bodySmall),
              ),
            const Divider(height: 32),
            ..._posts.map((p) => PostCard(
                  post: p,
                  onDeleted: _load,
                )),
            if (_posts.isEmpty)
              const Padding(
                padding: EdgeInsets.all(40),
                child: Center(child: Text('لا منشورات بعد.')),
              ),
          ],
        ),
      ),
    );
  }
}
