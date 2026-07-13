import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../api.dart';
import '../main.dart';
import '../models.dart';

class PostCard extends StatefulWidget {
  final Post post;
  final VoidCallback? onDeleted;
  const PostCard({super.key, required this.post, this.onDeleted});

  @override
  State<PostCard> createState() => _PostCardState();
}

class _PostCardState extends State<PostCard> {
  Future<void> _toggleLike() async {
    final post = widget.post;
    setState(() {
      post.likedByMe = !post.likedByMe;
      post.likesCount += post.likedByMe ? 1 : -1;
    });
    try {
      final res = await api.post('/posts/${post.id}/like/');
      setState(() {
        post.likedByMe = res['liked'];
        post.likesCount = res['likes_count'];
      });
    } catch (_) {}
  }

  String _kindChip(String kind) =>
      kind == 'agent' ? 'وكيل ذكي' : (kind == 'center' ? 'رسمي' : '');

  @override
  Widget build(BuildContext context) {
    final post = widget.post;
    final me = context.read<AuthState>().me;
    final chip = _kindChip(post.author.kind);

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: primaryBlue,
                  backgroundImage: post.author.avatar != null
                      ? NetworkImage(api.mediaUrl(post.author.avatar)!)
                      : null,
                  child: post.author.avatar == null
                      ? Text(
                          post.author.displayName.characters.first,
                          style: const TextStyle(color: Colors.white),
                        )
                      : null,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Flexible(
                            child: Text(
                              post.author.displayName,
                              style: const TextStyle(fontWeight: FontWeight.bold),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          if (chip.isNotEmpty) ...[
                            const SizedBox(width: 6),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                  horizontal: 8, vertical: 1),
                              decoration: BoxDecoration(
                                color: primaryBlue.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(12),
                              ),
                              child: Text(chip,
                                  style: const TextStyle(
                                      fontSize: 11, color: primaryBlue)),
                            ),
                          ],
                        ],
                      ),
                      Text(
                        _timeAgo(post.createdAt),
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
                if (me?.id == post.author.id)
                  IconButton(
                    icon: const Icon(Icons.delete_outline, size: 20),
                    onPressed: () async {
                      await api.delete('/posts/${post.id}/');
                      widget.onDeleted?.call();
                    },
                  ),
              ],
            ),
            if (post.text.isNotEmpty) ...[
              const SizedBox(height: 8),
              Text(post.text),
            ],
            if (post.image != null) ...[
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.network(api.mediaUrl(post.image)!),
              ),
            ],
            if (post.linkUrl.isNotEmpty) ...[
              const SizedBox(height: 8),
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  border: Border.all(color: Theme.of(context).dividerColor),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      post.linkTitle.isEmpty ? 'رابط خارجي' : post.linkTitle,
                      style: const TextStyle(fontWeight: FontWeight.w600),
                    ),
                    Text(
                      post.linkUrl,
                      style: Theme.of(context).textTheme.bodySmall,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      textDirection: TextDirection.ltr,
                    ),
                  ],
                ),
              ),
            ],
            const SizedBox(height: 6),
            Row(
              children: [
                IconButton(
                  onPressed: _toggleLike,
                  icon: Icon(
                    post.likedByMe ? Icons.favorite : Icons.favorite_border,
                    color: post.likedByMe ? Colors.pink : null,
                    size: 22,
                  ),
                ),
                Text('${post.likesCount}'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

String _timeAgo(DateTime dt) {
  final diff = DateTime.now().difference(dt);
  if (diff.inMinutes < 1) return 'الآن';
  if (diff.inHours < 1) return 'منذ ${diff.inMinutes} د';
  if (diff.inDays < 1) return 'منذ ${diff.inHours} س';
  return 'منذ ${diff.inDays} يوم';
}
