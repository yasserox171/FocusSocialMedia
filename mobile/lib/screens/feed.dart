import 'package:flutter/material.dart';

import '../api.dart';
import '../models.dart';
import '../widgets/post_card.dart';

class FeedScreen extends StatefulWidget {
  const FeedScreen({super.key});

  @override
  State<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> {
  final List<Post> _posts = [];
  final _scroll = ScrollController();
  int? _nextPage = 1;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadMore();
    _scroll.addListener(() {
      if (_scroll.position.extentAfter < 600) _loadMore();
    });
  }

  Future<void> _loadMore() async {
    if (_loading || _nextPage == null) return;
    setState(() => _loading = true);
    try {
      final data = await api.get('/posts/?page=$_nextPage');
      final known = _posts.map((p) => p.id).toSet();
      setState(() {
        _posts.addAll((data['results'] as List)
            .map((j) => Post.fromJson(j))
            .where((p) => !known.contains(p.id)));
        _nextPage = data['next'] != null ? _nextPage! + 1 : null;
      });
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _refresh() async {
    setState(() {
      _posts.clear();
      _nextPage = 1;
    });
    await _loadMore();
  }

  Future<void> _compose() async {
    final controller = TextEditingController();
    final posted = await showModalBottomSheet<bool>(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => Padding(
        padding: EdgeInsets.only(
          bottom: MediaQuery.of(ctx).viewInsets.bottom,
          left: 16,
          right: 16,
          top: 16,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: controller,
              autofocus: true,
              maxLines: 5,
              minLines: 3,
              decoration: const InputDecoration(
                hintText: 'شارك خبراً أو فكرة مع أعضاء فوكس…',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),
            FilledButton(
              onPressed: () async {
                if (controller.text.trim().isEmpty) return;
                await api.post('/posts/', {'text': controller.text.trim()});
                if (ctx.mounted) Navigator.pop(ctx, true);
              },
              child: const Text('انشر'),
            ),
            const SizedBox(height: 16),
          ],
        ),
      ),
    );
    if (posted == true) _refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('فوكس.سوشيال')),
      floatingActionButton: FloatingActionButton(
        onPressed: _compose,
        child: const Icon(Icons.edit),
      ),
      body: RefreshIndicator(
        onRefresh: _refresh,
        child: ListView.builder(
          controller: _scroll,
          itemCount: _posts.length + 1,
          itemBuilder: (context, i) {
            if (i == _posts.length) {
              return _loading
                  ? const Padding(
                      padding: EdgeInsets.all(20),
                      child: Center(child: CircularProgressIndicator()),
                    )
                  : const SizedBox(height: 80);
            }
            return PostCard(
              post: _posts[i],
              onDeleted: () => setState(() => _posts.removeAt(i)),
            );
          },
        ),
      ),
    );
  }
}
