"""
Test language switching functionality.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.utils import translation

def test_language_settings():
    """Test language configuration."""
    print("="*60)
    print("TIL SOZLAMALARINI TEKSHIRISH")
    print("="*60)

    print(f"\n[INFO] Default Language: {settings.LANGUAGE_CODE}")
    print(f"[INFO] USE_I18N: {settings.USE_I18N}")
    print(f"[INFO] USE_L10N: {settings.USE_L10N}")

    print(f"\n[INFO] Available Languages:")
    for code, name in settings.LANGUAGES:
        print(f"  - {code}: {name}")

    print(f"\n[INFO] LOCALE_PATHS:")
    for path in settings.LOCALE_PATHS:
        print(f"  - {path}")
        if os.path.exists(path):
            print(f"    [OK] Mavjud")
            # List language directories
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    mo_file = os.path.join(item_path, 'LC_MESSAGES', 'django.mo')
                    if os.path.exists(mo_file):
                        print(f"    [OK] {item}/LC_MESSAGES/django.mo")
                    else:
                        print(f"    [FAIL] {item}/LC_MESSAGES/django.mo topilmadi")
        else:
            print(f"    [FAIL] Yo'q")

    print(f"\n[INFO] Middleware:")
    for mw in settings.MIDDLEWARE:
        if 'locale' in mw.lower() or 'i18n' in mw.lower():
            print(f"  [OK] {mw}")

    # Test translation activation
    print(f"\n[TEST] Til faollashtirishni tekshirish:")

    for lang_code, lang_name in settings.LANGUAGES:
        translation.activate(lang_code)
        current = translation.get_language()
        print(f"  [{lang_code}] Faollashtirildi: {current} - ", end="")

        if current == lang_code:
            print("[OK]")

            # Test a simple translation
            from django.utils.translation import gettext
            test_str = gettext("Home")
            print(f"        'Home' tarjimasi: '{test_str}'")
        else:
            print("[FAIL]")

    translation.deactivate()

    print("\n" + "="*60)
    print("XULOSA")
    print("="*60)

    # Check for common issues
    issues = []

    # Check if LocaleMiddleware is present
    if not any('LocaleMiddleware' in mw for mw in settings.MIDDLEWARE):
        issues.append("LocaleMiddleware middleware da yo'q")

    # Check if i18n is enabled
    if not settings.USE_I18N:
        issues.append("USE_I18N o'chirilgan")

    # Check if locale files exist
    for lang_code, _ in settings.LANGUAGES:
        mo_file = settings.LOCALE_PATHS[0] / lang_code / 'LC_MESSAGES' / 'django.mo'
        if not os.path.exists(mo_file):
            issues.append(f"{lang_code} uchun django.mo fayli yo'q")

    if issues:
        print("\n[MUAMMOLAR TOPILDI]:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\n[SUCCESS] Hamma narsa to'g'ri sozlangan!")
        print("\nAgar til almashtirgich brauzerda ishlamasa:")
        print("1. Server qayta ishga tushiring: python manage.py runserver")
        print("2. Brauzerda Ctrl+F5 bosib cache ni tozalang")
        print("3. Yangi incognito/private window ochib sinang")
        print("4. Browser console da JavaScript xatolarni tekshiring (F12)")

if __name__ == '__main__':
    test_language_settings()
