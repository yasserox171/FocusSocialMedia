from rest_framework import serializers

from accounts.serializers import UserSerializer

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    liked_by_me = serializers.BooleanField(read_only=True, default=False)

    class Meta:
        model = Post
        fields = ["id", "author", "text", "image", "video", "link_url",
                  "link_title", "created_at", "likes_count", "liked_by_me"]
        read_only_fields = ["id", "author", "created_at"]

    def validate(self, attrs):
        # On create, require at least one kind of content.
        if self.instance is None:
            has_content = any([
                attrs.get("text", "").strip(),
                attrs.get("image"),
                attrs.get("video"),
                attrs.get("link_url", "").strip(),
            ])
            if not has_content:
                raise serializers.ValidationError("المنشور فارغ.")
        return attrs
