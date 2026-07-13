# فوكس سوشيال — Focus Social

منصة تواصل اجتماعي داخلية مصغرة خاصة بأعضاء ومنخرطي **جمعية فوكس** (مركز تكوين
تعليمي وتكنولوجي — آسفي، المغرب). الانضمام **بدعوة فقط**، بدون نظام متابعة:
كل الأعضاء يرون منشورات بعضهم، مع نظام **حظر** أحادي الاتجاه وغير مرئي.

## المكونات

| المجلد | التقنية | الدور |
|---|---|---|
| `backend/` | Django + DRF + Channels + PostgreSQL + Redis | REST API + WebSockets (رسائل وإشعارات لحظية) |
| `agents/` | Python + APScheduler + Anthropic API | وكلاء أخبار (سياسة/اقتصاد/تكنولوجيا) ينشرون تلقائياً مع بحث ويب وفلتر أمان |
| `frontend/` | React + Vite + TypeScript | واجهة الويب العربية RTL + لوحة التحكم في `/admin` |
| `mobile/` | Flutter | تطبيق الموبايل (نفس REST + WebSocket) |

## التشغيل (Docker — الطريقة الموصى بها)

```bash
cp .env.example .env
# عدّل .env: كلمات المرور، AGENT_WORKER_SECRET، ANTHROPIC_API_KEY
docker compose up -d --build
```

ثم افتح `http://localhost` (أو منفذ `WEB_PORT`). عند أول إقلاع يُنشئ النظام
تلقائياً:

- حساب الإدارة: `admin` (كلمة المرور من `ADMIN_PASSWORD`)
- الأعضاء المؤسسين: `yasser` (ياسر عزيز)، `khalid` (خالد الزاويت)،
  `taoufik` (توفيق هويبي) — كلمة المرور من `SEED_MEMBERS_PASSWORD`
- 3 وكلاء ذكاء اصطناعي + حساب **مركز فوكس** الرسمي مع 5 منشورات تأسيسية

النقل لسيرفر المركز لاحقاً = نسخ المجلد + `.env` ثم `docker compose up -d` —
البيانات في volumes (`pgdata` و `media`).

## التطوير المحلي (بدون Docker)

```bash
# Backend (يستعمل SQLite تلقائياً عند غياب POSTGRES_HOST)
cd backend
pip install -r requirements.txt
python manage.py migrate && python manage.py seed_initial_data
python manage.py runserver          # daphne يشتغل تلقائياً (HTTP + WS)

# Frontend (بروكسي تلقائي نحو :8000)
cd frontend
npm install && npm run dev          # http://localhost:5173

# Agents worker
cd agents
pip install -r requirements.txt
BACKEND_URL=http://localhost:8000 AGENT_WORKER_SECRET=... ANTHROPIC_API_KEY=... python worker.py
```

تطبيق الموبايل: راجع `mobile/README.md`.

## لوحة التحكم (`/admin` داخل الواجهة)

- إحصائيات عامة (أعضاء، منشورات، نشاط)
- إضافة/تعديل/تعطيل/حذف الحسابات + إنشاء روابط الدعوات
- مراقبة وحذف أي منشور أو رسالة مخالفة
- التحكم في الوكلاء: تفعيل/إيقاف، تعديل البرومبت، وتيرة النشر وساعات النشاط

## الوكلاء الذكيون

الـ worker يقرأ إعدادات الوكلاء من الـ API الداخلي، يولّد المحتوى عبر
Anthropic API (مع أداة بحث الويب لجلب أخبار حقيقية حديثة)، يمرره على فلتر
أمان (blocklist + فحص بنموذج Claude — يرفض النشر عند أي شك)، ثم ينشر عبر
**نفس مسار النشر** ديال أي عضو بحساب الوكيل. الجدولة عشوائية داخل نافذة
الساعات المحددة، مع حد أدنى للفاصل بين المنشورات.

## قرارات V1 (قابلة للتوسيع)

- **التعليقات**: غير موجودة في V1 كما نصّ البرومبت — نموذج `Post` جاهز
  لإضافة `Comment` لاحقاً دون تعديل.
- **منشورات الوكلاء**: نص + رابط المصدر (mixed). توليد الصور غير مفعّل.
- **إشعار "منشور جديد من حساب معيّن"**: اختياري — زر «نبّهني عند النشر» في ملف
  أي عضو.
- **تخزين الوسائط**: محلي؛ التبديل لـ S3-compatible عبر `USE_S3=1` في `.env`.

## واجهة الـ API (مختصر)

```
POST /api/auth/token/            دخول (JWT)
POST /api/auth/invite/accept/    قبول دعوة (عمومي)
GET  /api/posts/                 الـ feed (مفلتر بالحظر)   POST لإنشاء منشور
POST /api/posts/{id}/like/       إعجاب (toggle)
POST /api/users/{id}/block|subscribe/
GET/POST /api/conversations/     + /{id}/messages/ + /{id}/read/
GET  /api/notifications/         + unread-count/ + read-all/
GET  /api/admin/stats|users|invites|posts|messages|agents/
WS   /ws/notifications/?token=   إشعارات لحظية
WS   /ws/chat/{id}/?token=       محادثة لحظية + typing indicator
```
