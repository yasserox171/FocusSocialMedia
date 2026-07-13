class User {
  final int id;
  final String username;
  final String displayName;
  final String bio;
  final String? avatar;
  final String kind; // human | agent | center

  User.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        username = j['username'],
        displayName = j['display_name'] ?? '',
        bio = j['bio'] ?? '',
        avatar = j['avatar'],
        kind = j['kind'] ?? 'human';
}

class Post {
  final int id;
  final User author;
  final String text;
  final String? image;
  final String? video;
  final String linkUrl;
  final String linkTitle;
  final DateTime createdAt;
  int likesCount;
  bool likedByMe;

  Post.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        author = User.fromJson(j['author']),
        text = j['text'] ?? '',
        image = j['image'],
        video = j['video'],
        linkUrl = j['link_url'] ?? '',
        linkTitle = j['link_title'] ?? '',
        createdAt = DateTime.parse(j['created_at']),
        likesCount = j['likes_count'] ?? 0,
        likedByMe = j['liked_by_me'] ?? false;
}

class Conversation {
  final int id;
  final User otherUser;
  final String lastMessageText;
  final int unreadCount;

  Conversation.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        otherUser = User.fromJson(j['other_user']),
        lastMessageText = j['last_message']?['text'] ?? '',
        unreadCount = j['unread_count'] ?? 0;
}

class Message {
  final int id;
  final int sender;
  final String text;
  final DateTime createdAt;

  Message.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        sender = j['sender'],
        text = j['text'],
        createdAt = DateTime.parse(j['created_at']);
}

class AppNotification {
  final int id;
  final String kind;
  final String text;
  final int? conversationId;
  final bool isRead;
  final DateTime createdAt;

  AppNotification.fromJson(Map<String, dynamic> j)
      : id = j['id'],
        kind = j['kind'],
        text = j['text'],
        conversationId = j['conversation_id'],
        isRead = j['is_read'] ?? false,
        createdAt = DateTime.parse(j['created_at']);
}
