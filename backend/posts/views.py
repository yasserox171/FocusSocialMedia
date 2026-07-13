from django.db.models import Count, Exists, OuterRef
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from accounts.models import Block, PostSubscription
from accounts.permissions import IsAdmin
from notifications.services import notify

from .models import Like, Post
from .serializers import PostSerializer


def annotated_posts(user, queryset=None):
    qs = queryset if queryset is not None else Post.objects.all()
    return (
        qs.select_related("author")
        .annotate(
            likes_count=Count("likes", distinct=True),
            liked_by_me=Exists(Like.objects.filter(post=OuterRef("pk"), user=user)),
        )
    )


class PostViewSet(viewsets.ModelViewSet):
    """
    Global feed (everyone sees everyone — no follow system), filtered only
    by the requesting user's blocks. Also handles create / delete / like.
    """

    serializer_class = PostSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    http_method_names = ["get", "post", "delete"]

    def get_queryset(self):
        user = self.request.user
        qs = annotated_posts(user)
        blocked = Block.objects.filter(blocker=user).values_list("blocked_id", flat=True)
        qs = qs.exclude(author_id__in=blocked)
        author = self.request.query_params.get("author")
        if author:
            qs = qs.filter(author_id=author)
        return qs

    def perform_create(self, serializer):
        post = serializer.save(author=self.request.user)
        # Notify opt-in subscribers of this author.
        subscriber_ids = PostSubscription.objects.filter(
            target=self.request.user
        ).values_list("subscriber_id", flat=True)
        for sid in subscriber_ids:
            notify(
                recipient_id=sid,
                kind="new_post",
                actor=self.request.user,
                text=f"نشر {self.request.user.display_name} منشوراً جديداً",
                post_id=post.id,
            )

    def destroy(self, request, *args, **kwargs):
        post = self.get_object()
        if post.author_id != request.user.id and not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        """Toggle like. Returns the new state."""
        post = self.get_object()
        like, created = Like.objects.get_or_create(user=request.user, post=post)
        if created:
            if post.author_id != request.user.id:
                notify(
                    recipient_id=post.author_id,
                    kind="like",
                    actor=request.user,
                    text=f"أعجب {request.user.display_name} بمنشورك",
                    post_id=post.id,
                )
        else:
            like.delete()
        return Response({
            "liked": created,
            "likes_count": post.likes.count(),
        })


class AdminPostViewSet(viewsets.ReadOnlyModelViewSet):
    """Moderation view: admins see everything (no block filtering) and delete."""

    permission_classes = [IsAdmin]
    serializer_class = PostSerializer

    def get_queryset(self):
        return annotated_posts(self.request.user)

    def destroy(self, request, *args, **kwargs):
        self.get_object().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    http_method_names = ["get", "delete"]
