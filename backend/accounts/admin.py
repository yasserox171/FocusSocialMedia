from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Block, Invite, PostSubscription, User


@admin.register(User)
class FocusUserAdmin(UserAdmin):
    list_display = ["username", "display_name", "kind", "is_active", "is_staff"]
    fieldsets = UserAdmin.fieldsets + (
        ("Focus", {"fields": ("kind", "display_name", "bio", "avatar")}),
    )


admin.site.register(Invite)
admin.site.register(Block)
admin.site.register(PostSubscription)
