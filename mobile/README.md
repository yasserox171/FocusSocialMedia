# تطبيق فوكس سوشيال (Flutter)

كود التطبيق كامل في `lib/`. مجلدات المنصات (android/ios) تُولَّد بأمر واحد:

```bash
cd mobile
flutter create . --platforms=android,ios --org ma.focuscenter --project-name focus_social
flutter pub get
```

## التشغيل

```bash
# على المحاكي (Android emulator) — الخادم المحلي متاح عبر 10.0.2.2 تلقائياً
flutter run

# على هاتف حقيقي على نفس الشبكة — مرّر عنوان الخادم
flutter run --dart-define=BASE_URL=http://192.168.1.10
```

`BASE_URL` هو عنوان خادم المنصة (nginx أو Django مباشرة).

## ملاحظات

- إذا كان الخادم بدون HTTPS، فعّل cleartext في
  `android/app/src/main/AndroidManifest.xml` بإضافة
  `android:usesCleartextTraffic="true"` داخل وسم `<application>`.
- النشر من التطبيق نصي في V1؛ الصور/الفيديو من الويب. الإعجاب والرسائل
  الفورية والإشعارات اللحظية تعمل بالكامل (نفس REST + WebSocket ديال الويب).
