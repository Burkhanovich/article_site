"""
Add form field translations to .po files.
"""

# New translations to add
new_translations = {
    'uz': [
        ('Article Title', 'Maqola Sarlavhasi'),
        ('Article Content', 'Maqola Kontenti'),
        ('Article File', 'Maqola Fayli'),
        ('Maximum 200 characters', 'Maksimal 200 belgi'),
        ('Write your article content with rich text formatting', 'Maqolangiz kontentini boy matn formatlash bilan yozing'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Maqolani fayl sifatida yuklang. Ruxsat etilgan formatlar: TXT, DOC, DOCX, PDF. Maksimal hajm: 10MB'),
        ('Choose "Draft" to save without publishing, or "Published" to make it visible to readers',
         '"Qoralama" ni tanlang nashr etmasdan saqlash uchun, yoki "Nashr etilgan" ni tanlang o\'quvchilarga ko\'rinishi uchun'),
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
    ],
    'ru': [
        ('Article Title', 'Заголовок Статьи'),
        ('Article Content', 'Содержание Статьи'),
        ('Article File', 'Файл Статьи'),
        ('Maximum 200 characters', 'Максимум 200 символов'),
        ('Write your article content with rich text formatting', 'Напишите содержание статьи с форматированным текстом'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Загрузите статью как файл. Разрешенные форматы: TXT, DOC, DOCX, PDF. Максимальный размер: 10МБ'),
        ('Choose "Draft" to save without publishing, or "Published" to make it visible to readers',
         'Выберите "Черновик" для сохранения без публикации или "Опубликовано" чтобы сделать видимым для читателей'),
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
    ],
    'en': [
        ('Article Title', 'Article Title'),
        ('Article Content', 'Article Content'),
        ('Article File', 'Article File'),
        ('Maximum 200 characters', 'Maximum 200 characters'),
        ('Write your article content with rich text formatting', 'Write your article content with rich text formatting'),
        ('Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB',
         'Upload article as file. Allowed formats: TXT, DOC, DOCX, PDF. Maximum size: 10MB'),
        ('Choose "Draft" to save without publishing, or "Published" to make it visible to readers',
         'Choose "Draft" to save without publishing, or "Published" to make it visible to readers'),
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
}

def add_translations():
    """Add new translations to .po files."""
    print("="*60)
    print("TARJIMALAR QO'SHILMOQDA")
    print("="*60)

    for lang, translations in new_translations.items():
        po_file = f'locale/{lang}/LC_MESSAGES/django.po'

        print(f"\n[{lang.upper()}] {po_file} faylini yangilanmoqda...")

        # Read existing file
        with open(po_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Add new translations
        new_entries = []
        for msgid, msgstr in translations:
            # Check if translation already exists
            if f'msgid "{msgid}"' in content:
                print(f"  [SKIP] '{msgid}' - allaqachon mavjud")
                continue

            # Escape double quotes in msgid and msgstr
            msgid_escaped = msgid.replace('"', '\\"')
            msgstr_escaped = msgstr.replace('"', '\\"')

            entry = f'\nmsgid "{msgid_escaped}"\nmsgstr "{msgstr_escaped}"\n'
            new_entries.append(entry)
            print(f"  [OK] '{msgid}' qo'shildi")

        if new_entries:
            # Append to file
            with open(po_file, 'a', encoding='utf-8') as f:
                f.write('\n# Form Field Translations\n')
                for entry in new_entries:
                    f.write(entry)

            print(f"\n[SUCCESS] {len(new_entries)} ta yangi tarjima qo'shildi!")
        else:
            print(f"\n[INFO] Yangi tarjimalar topilmadi, hammasi mavjud")

    print("\n" + "="*60)
    print("BARCHA TARJIMALAR QO'SHILDI!")
    print("="*60)
    print("\nKeyingi qadam: Tarjimalarni kompilyatsiya qiling")
    print("> python compile_translations.py")

if __name__ == '__main__':
    add_translations()
