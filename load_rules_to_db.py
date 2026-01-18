"""
Script to load article rules file into database for testing.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import ArticleRules
from django.core.files import File

def load_rules():
    """Load rules file into database."""
    print("="*60)
    print("MAQOLA QOIDALARINI DATABASE GA YUKLASH")
    print("="*60)

    # Check if rules already exist
    existing_rules = ArticleRules.objects.all()
    if existing_rules.exists():
        print(f"\n[INFO] {existing_rules.count()} ta qoida topildi.")
        print("Barcha eski qoidalarni o'chiramiz...")
        existing_rules.delete()
        print("[OK] Eski qoidalar o'chirildi.")

    # Create new rules with file
    rules_file_path = 'media/rules/maqola_qoidalari.txt'

    if not os.path.exists(rules_file_path):
        print(f"\n[ERROR] File topilmadi: {rules_file_path}")
        return

    print(f"\n[INFO] File topildi: {rules_file_path}")
    print(f"[INFO] File hajmi: {os.path.getsize(rules_file_path)} bytes")

    # Read file content for preview
    with open(rules_file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    print(f"[INFO] Kontent uzunligi: {len(content)} belgi")

    # Create ArticleRules object
    rules = ArticleRules.objects.create(
        title="Maqola Yozish Qoidalari",
        title_uz="Maqola Yozish Qoidalari",
        title_ru="Правила написания статей",
        title_en="Article Writing Rules",
        content="",  # Leave empty, will use file
        is_active=True
    )

    # Attach the file
    with open(rules_file_path, 'rb') as f:
        rules.rules_file.save('maqola_qoidalari.txt', File(f), save=True)

    print("\n[OK] Qoidalar muvaffaqiyatli yuklandi!")
    print(f"[OK] ID: {rules.id}")
    print(f"[OK] Sarlavha: {rules.title}")
    print(f"[OK] File: {rules.rules_file.name}")
    print(f"[OK] Faol: {rules.is_active}")

    # Test reading content
    retrieved_content = rules.get_rules_content()
    print(f"\n[TEST] Kontent o'qildi: {len(retrieved_content)} belgi")
    print(f"[TEST] Birinchi 100 belgi:")
    print("-" * 60)
    print(retrieved_content[:100] + "...")
    print("-" * 60)

    print("\n" + "="*60)
    print("YAKUNIY NATIJA")
    print("="*60)
    print("[SUCCESS] Barcha qoidalar database ga yuklandi!")
    print("\nTest qilish uchun:")
    print("1. Server ishga tushiring: python manage.py runserver")
    print("2. Author sifatida ro'yxatdan o'ting")
    print("3. Accept rules sahifasiga o'ting: /uz/users/accept-rules/")
    print("4. Qoidalarni o'qib, qabul qiling")
    print("5. Maqola yaratishni sinab ko'ring: /uz/articles/create/")
    print("\nAdmin panel orqali ko'rish:")
    print("http://127.0.0.1:8000/uz/admin/users/articlerules/")

if __name__ == '__main__':
    try:
        load_rules()
    except Exception as e:
        print(f"\n[ERROR] Xatolik yuz berdi: {e}")
        import traceback
        traceback.print_exc()
