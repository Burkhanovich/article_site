"""
Fix .po files by removing incorrectly added translations and re-adding them with proper escaping.
"""
import re

def fix_po_file(po_file):
    """Fix a single .po file."""
    print(f"\n[INFO] Fixing {po_file}...")

    # Read the file
    with open(po_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the last occurrence of a standard translation before our additions
    # We'll remove everything after "# Form Field Translations"
    marker = '# Form Field Translations'
    if marker in content:
        # Remove everything after the marker
        content = content[:content.index(marker)]
        print(f"[OK] Removed incorrectly formatted translations")

    return content

def add_translations_properly(content):
    """Add translations with proper escaping."""
    # Translations with proper escaping
    translations_uz = [
        ('Article Title', 'Maqola Sarlavhasi'),
        ('Article Content', 'Maqola Kontenti'),
        ('Article File', 'Maqola Fayli'),
        ('Maximum 200 characters', 'Maksimal 200 belgi'),
        ('Write your article content with rich text formatting', 'Maqolangiz kontentini boy matn formatlash bilan yozing'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Maqolani fayl sifatida yuklang. Ruxsat etilgan formatlar: TXT, DOC, DOCX, PDF. Maksimal hajm: 10MB'),
        ('Choose \\"Draft\\" to save without publishing, or \\"Published\\" to make it visible to readers',
         '\\"Qoralama\\" ni tanlang nashr etmasdan saqlash uchun, yoki \\"Nashr etilgan\\" ni tanlang o\'quvchilarga ko\'rinishi uchun'),
        ('Optional', 'Ixtiyoriy'),
        ('Current file', 'Joriy fayl'),
        ('Type', 'Turi'),
        ('Size', 'Hajmi'),
        ('Update Article', 'Maqolani Yangilash'),
        ('Writing Tips', 'Yozish Maslahatlari'),
        ('Use a clear, descriptive title that summarizes your article',
         'Maqolangizni umumlashtiruvchi aniq, tavsifiy sarlavhadan foydalaning'),
        ('Add a cover image to make your article more attractive (optional but recommended)',
         'Maqolangizni jozibador qilish uchun muqova rasmini qo\'shing (ixtiyoriy, ammo tavsiya etiladi)'),
        ('Upload your article as a file (TXT, DOC, DOCX, or PDF) if you prefer (optional)',
         'Agar xohlasangiz maqolangizni fayl sifatida yuklang (TXT, DOC, DOCX, yoki PDF) (ixtiyoriy)'),
        ('Format your content with headings, lists, and images for better readability',
         'Yaxshi o\'qilishi uchun kontentingizni sarlavhalar, ro\'yxatlar va rasmlar bilan formatlang'),
        ('Save as Draft if you want to continue editing later',
         'Keyinroq tahrirlashni davom ettirish uchun Qoralama sifatida saqlang'),
        ('Publish when your article is ready for readers',
         'Maqolangiz o\'quvchilar uchun tayyor bo\'lganda nashr eting'),
    ]

    content += '\n# Form Field Translations\n'
    for msgid, msgstr in translations_uz:
        content += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'

    return content

def main():
    print("="*60)
    print(".PO FAYLLARNI TUZATISH")
    print("="*60)

    # Fix Uzbek
    print("\n[UZ] Uzbek faylini tuzatish...")
    content = fix_po_file('locale/uz/LC_MESSAGES/django.po')
    content = add_translations_properly(content)
    with open('locale/uz/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] Uzbek fayli tuzatildi va yangilandi")

    # Fix Russian
    print("\n[RU] Rus faylini tuzatish...")
    content_ru = fix_po_file('locale/ru/LC_MESSAGES/django.po')
    content_ru += '\n# Form Field Translations\n'
    translations_ru = [
        ('Article Title', 'Заголовок Статьи'),
        ('Article Content', 'Содержание Статьи'),
        ('Article File', 'Файл Статьи'),
        ('Maximum 200 characters', 'Максимум 200 символов'),
        ('Write your article content with rich text formatting', 'Напишите содержание статьи с форматированным текстом'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Загрузите статью как файл. Разрешенные форматы: TXT, DOC, DOCX, PDF. Максимальный размер: 10МБ'),
        ('Choose \\"Draft\\" to save without publishing, or \\"Published\\" to make it visible to readers',
         'Выберите \\"Черновик\\" для сохранения без публикации или \\"Опубликовано\\" чтобы сделать видимым для читателей'),
        ('Optional', 'Необязательно'),
        ('Current file', 'Текущий файл'),
        ('Type', 'Тип'),
        ('Size', 'Размер'),
        ('Update Article', 'Обновить Статью'),
        ('Writing Tips', 'Советы по Написанию'),
        ('Use a clear, descriptive title that summarizes your article',
         'Используйте четкий, описательный заголовок, который обобщает вашу статью'),
        ('Add a cover image to make your article more attractive (optional but recommended)',
         'Добавьте обложку, чтобы сделать статью более привлекательной (необязательно, но рекомендуется)'),
        ('Upload your article as a file (TXT, DOC, DOCX, or PDF) if you prefer (optional)',
         'Загрузите статью как файл (TXT, DOC, DOCX или PDF), если хотите (необязательно)'),
        ('Format your content with headings, lists, and images for better readability',
         'Форматируйте содержание с заголовками, списками и изображениями для лучшей читаемости'),
        ('Save as Draft if you want to continue editing later',
         'Сохраните как черновик, если хотите продолжить редактирование позже'),
        ('Publish when your article is ready for readers',
         'Опубликуйте, когда ваша статья готова для читателей'),
    ]
    for msgid, msgstr in translations_ru:
        content_ru += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
    with open('locale/ru/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
        f.write(content_ru)
    print("[OK] Rus fayli tuzatildi va yangilandi")

    # Fix English
    print("\n[EN] Ingliz faylini tuzatish...")
    content_en = fix_po_file('locale/en/LC_MESSAGES/django.po')
    content_en += '\n# Form Field Translations\n'
    translations_en = [
        ('Article Title', 'Article Title'),
        ('Article Content', 'Article Content'),
        ('Article File', 'Article File'),
        ('Maximum 200 characters', 'Maximum 200 characters'),
        ('Write your article content with rich text formatting', 'Write your article content with rich text formatting'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB'),
        ('Choose \\"Draft\\" to save without publishing, or \\"Published\\" to make it visible to readers',
         'Choose \\"Draft\\" to save without publishing, or \\"Published\\" to make it visible to readers'),
        ('Optional', 'Optional'),
        ('Current file', 'Current file'),
        ('Type', 'Type'),
        ('Size', 'Size'),
        ('Update Article', 'Update Article'),
        ('Writing Tips', 'Writing Tips'),
        ('Use a clear, descriptive title that summarizes your article',
         'Use a clear, descriptive title that summarizes your article'),
        ('Add a cover image to make your article more attractive (optional but recommended)',
         'Add a cover image to make your article more attractive (optional but recommended)'),
        ('Upload your article as a file (TXT, DOC, DOCX, or PDF) if you prefer (optional)',
         'Upload your article as a file (TXT, DOC, DOCX, or PDF) if you prefer (optional)'),
        ('Format your content with headings, lists, and images for better readability',
         'Format your content with headings, lists, and images for better readability'),
        ('Save as Draft if you want to continue editing later',
         'Save as Draft if you want to continue editing later'),
        ('Publish when your article is ready for readers',
         'Publish when your article is ready for readers'),
    ]
    for msgid, msgstr in translations_en:
        content_en += f'\nmsgid "{msgid}"\nmsgstr "{msgstr}"\n'
    with open('locale/en/LC_MESSAGES/django.po', 'w', encoding='utf-8') as f:
        f.write(content_en)
    print("[OK] Ingliz fayli tuzatildi va yangilandi")

    print("\n" + "="*60)
    print("BARCHA FAYLLAR TUZATILDI!")
    print("="*60)
    print("\nKeyingi qadam: Kompilyatsiya qiling")
    print("> python compile_translations.py")

if __name__ == '__main__':
    main()
