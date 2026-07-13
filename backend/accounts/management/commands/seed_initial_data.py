"""
Seeds the mandatory initial data (idempotent — safe to run repeatedly):
  - one platform admin (credentials from env or defaults)
  - the 3 founding human members
  - the 3 AI agent accounts + their AgentProfile configs
  - the official Focus Center account with 5 founding posts

Run: python manage.py seed_initial_data
"""
import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from aiagents.models import AgentProfile
from posts.models import Post

User = get_user_model()

HUMANS = [
    ("yasser", "ياسر عزيز", "رئيس جمعية فوكس"),
    ("khalid", "خالد الزاويت", "أمين عام لجمعية فوكس"),
    ("taoufik", "توفيق هويبي", "كاتب عام لجمعية فوكس"),
]

AGENTS = [
    {
        "username": "agent_politics",
        "display_name": "وكيل الأخبار السياسية",
        "bio": "وكيل ذكاء اصطناعي ينشر آخر الأخبار السياسية العالمية والمغربية.",
        "topic": "politics",
        "system_prompt": (
            "أنت وكيل أخبار سياسية لمنصة داخلية لأعضاء جمعية فوكس بآسفي، المغرب. "
            "ابحث عن آخر الأخبار السياسية الحقيقية والحديثة، مع أولوية للأخبار المغربية "
            "ثم العربية ثم العالمية. اكتب منشوراً موجزاً بالعربية الفصحى الواضحة (3-6 جمل)، "
            "بأسلوب محايد ومهني، دون تحيز حزبي أو محتوى تحريضي. اذكر المصدر."
        ),
    },
    {
        "username": "agent_economy",
        "display_name": "وكيل الأخبار الاقتصادية",
        "bio": "وكيل ذكاء اصطناعي ينشر آخر الأخبار الاقتصادية العالمية والمغربية.",
        "topic": "economy",
        "system_prompt": (
            "أنت وكيل أخبار اقتصادية لمنصة داخلية لأعضاء جمعية فوكس بآسفي، المغرب. "
            "ابحث عن آخر الأخبار الاقتصادية الحقيقية والحديثة: الاقتصاد المغربي، الأسواق، "
            "العملات، والاقتصاد العالمي. اكتب منشوراً موجزاً بالعربية الواضحة (3-6 جمل) "
            "بأسلوب مهني ومبسط يفهمه غير المتخصص. اذكر المصدر."
        ),
    },
    {
        "username": "agent_tech",
        "display_name": "وكيل الأخبار التكنولوجية",
        "bio": "وكيل ذكاء اصطناعي ينشر آخر أخبار التكنولوجيا العالمية والمغربية.",
        "topic": "technology",
        "system_prompt": (
            "أنت وكيل أخبار تكنولوجية لمنصة داخلية لأعضاء جمعية فوكس بآسفي، المغرب — "
            "مركز تكوين تعليمي وتكنولوجي. ابحث عن آخر أخبار التكنولوجيا الحقيقية والحديثة: "
            "الذكاء الاصطناعي، البرمجة، المقاولات الناشئة المغربية، والتقنية العالمية. "
            "اكتب منشوراً موجزاً وشيقاً بالعربية (3-6 جمل) يناسب شباباً مهتمين بالتقنية. اذكر المصدر."
        ),
    },
]

CENTER_POSTS = [
    "مرحباً بكم في المنصة الاجتماعية الداخلية لمركز فوكس! 🎉 هذه المساحة خاصة بأعضاء "
    "ومنخرطي الجمعية للتواصل ومشاركة الأخبار والأفكار. (محتوى نموذجي قابل للتعديل من لوحة التحكم)",
    "تأسس مركز فوكس بآسفي كمركز تكوين تعليمي وتكنولوجي يهدف إلى تمكين الشباب من مهارات "
    "العصر الرقمي. (محتوى نموذجي قابل للتعديل)",
    "من أنشطتنا السابقة: دورات تكوينية في البرمجة والتصميم، وورشات عملية في الروبوتيك "
    "والذكاء الاصطناعي لفائدة شباب المدينة. (محتوى نموذجي قابل للتعديل)",
    "ينظم المركز لقاءات دورية ومسابقات تقنية لتشجيع روح المبادرة والابتكار لدى المنخرطين. "
    "(محتوى نموذجي قابل للتعديل)",
    "تابعوا هذه المنصة باستمرار: أخبار الجمعية، مواعيد الأنشطة، وآخر مستجدات المركز "
    "ستجدونها هنا أولاً. (محتوى نموذجي قابل للتعديل)",
]


class Command(BaseCommand):
    help = "Seed initial accounts and founding content"

    def handle(self, *args, **options):
        created_credentials = []

        # -- Admin --------------------------------------------------------
        admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        admin_password = os.environ.get("ADMIN_PASSWORD", "FocusAdmin2026!")
        admin, created = User.objects.get_or_create(
            username=admin_username,
            defaults={
                "display_name": "إدارة المنصة",
                "kind": User.Kind.HUMAN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password(admin_password)
            admin.save()
            created_credentials.append((admin_username, admin_password))

        # -- Founding members ------------------------------------------------
        default_password = os.environ.get("SEED_MEMBERS_PASSWORD", "FocusMember2026!")
        for username, name, role in HUMANS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"display_name": name, "bio": role, "kind": User.Kind.HUMAN},
            )
            if created:
                user.set_password(default_password)
                user.save()
                created_credentials.append((username, default_password))

        # -- AI agents ---------------------------------------------------------
        for spec in AGENTS:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "display_name": spec["display_name"],
                    "bio": spec["bio"],
                    "kind": User.Kind.AGENT,
                },
            )
            if created:
                user.set_unusable_password()
                user.save()
            AgentProfile.objects.get_or_create(
                user=user,
                defaults={
                    "topic": spec["topic"],
                    "system_prompt": spec["system_prompt"],
                    "posts_per_day": int(os.environ.get("AGENT_POSTS_PER_DAY", "2")),
                },
            )

        # -- Center account + founding posts ---------------------------------------
        center, created = User.objects.get_or_create(
            username="focus_center",
            defaults={
                "display_name": "مركز فوكس",
                "bio": "الحساب الرسمي لمركز فوكس — مركز تكوين تعليمي وتكنولوجي بآسفي.",
                "kind": User.Kind.CENTER,
            },
        )
        if created:
            center.set_unusable_password()
            center.save()
        if not center.posts.exists():
            for text in CENTER_POSTS:
                Post.objects.create(author=center, text=text)

        self.stdout.write(self.style.SUCCESS("Seed complete."))
        for username, password in created_credentials:
            self.stdout.write(f"  created account: {username} / {password}")
        if not created_credentials:
            self.stdout.write("  (all accounts already existed — nothing changed)")
