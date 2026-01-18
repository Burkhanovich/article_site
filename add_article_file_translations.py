"""
Add article file display translations to .po files.
"""
import os

# New translations
translations = {
    'uz': [
        # Article list and detail translations
        ('Download Article File', 'Maqola Faylini Yuklash'),
        ('Open article file', 'Maqola faylini ochish'),
        ('Article File Available', 'Maqola Fayli Mavjud'),
        ('File Type', 'Fayl Turi'),
        ('Size', 'Hajmi'),
        ('Open File', 'Faylni Ochish'),
        ('Download', 'Yuklash'),
        ('Back to Articles', 'Maqolalarga Qaytish'),
        ('Published Articles', 'Nashr Qilingan Maqolalar'),
        ('Browse our collection of amazing articles', 'Bizning ajoyib maqolalar to\'plamini ko\'ring'),
        ('Search', 'Qidirish'),
        ('Showing results for', 'Qidiruv natijalari'),
        ('Clear', 'Tozalash'),
        ('Read Article', 'Maqolani O\'qish'),
        ('Page', 'Sahifa'),
        ('of', 'dan'),
        ('No articles published yet. Be the first to share your knowledge!',
         'Hali maqolalar nashr qilinmagan. Bilimingizni baham ko\'radigan birinchi bo\'ling!'),
        ('Last updated', 'Oxirgi yangilanish'),
        ('About the Author', 'Muallif Haqida'),
    ],
    'ru': [
        # Article list and detail translations
        ('Download Article File', 'Скачать Файл Статьи'),
        ('Open article file', 'Открыть файл статьи'),
        ('Article File Available', 'Файл Статьи Доступен'),
        ('File Type', 'Тип Файла'),
        ('Size', 'Размер'),
        ('Open File', 'Открыть Файл'),
        ('Download', 'Скачать'),
        ('Back to Articles', 'Вернуться к Статьям'),
        ('Published Articles', 'Опубликованные Статьи'),
        ('Browse our collection of amazing articles', 'Просмотрите нашу коллекцию замечательных статей'),
        ('Search', 'Поиск'),
        ('Showing results for', 'Показаны результаты для'),
        ('Clear', 'Очистить'),
        ('Read Article', 'Читать Статью'),
        ('Page', 'Страница'),
        ('of', 'из'),
        ('No articles published yet. Be the first to share your knowledge!',
         'Пока нет опубликованных статей. Будьте первым, кто поделится своими знаниями!'),
        ('Last updated', 'Последнее обновление'),
        ('About the Author', 'Об Авторе'),
    ],
    'en': [
        # Article list and detail translations (same as English)
        ('Download Article File', 'Download Article File'),
        ('Open article file', 'Open article file'),
        ('Article File Available', 'Article File Available'),
        ('File Type', 'File Type'),
        ('Size', 'Size'),
        ('Open File', 'Open File'),
        ('Download', 'Download'),
        ('Back to Articles', 'Back to Articles'),
        ('Published Articles', 'Published Articles'),
        ('Browse our collection of amazing articles', 'Browse our collection of amazing articles'),
        ('Search', 'Search'),
        ('Showing results for', 'Showing results for'),
        ('Clear', 'Clear'),
        ('Read Article', 'Read Article'),
        ('Page', 'Page'),
        ('of', 'of'),
        ('No articles published yet. Be the first to share your knowledge!',
         'No articles published yet. Be the first to share your knowledge!'),
        ('Last updated', 'Last updated'),
        ('About the Author', 'About the Author'),
    ]
}

def add_translations_to_po(lang_code, trans_list):
    """Add translations to a .po file."""
    po_file = f'locale/{lang_code}/LC_MESSAGES/django.po'

    if not os.path.exists(po_file):
        print(f"[ERROR] {po_file} not found")
        return

    with open(po_file, 'a', encoding='utf-8') as f:
        f.write('\n\n# Article File Display Translations\n')
        for msgid, msgstr in trans_list:
            # Escape quotes
            msgid_escaped = msgid.replace('"', '\\"')
            msgstr_escaped = msgstr.replace('"', '\\"')

            f.write(f'msgid "{msgid_escaped}"\n')
            f.write(f'msgstr "{msgstr_escaped}"\n')
            f.write('\n')

    print(f"[OK] Added {len(trans_list)} translations to {po_file}")

def main():
    print("=" * 60)
    print("ADDING ARTICLE FILE DISPLAY TRANSLATIONS")
    print("=" * 60)

    for lang_code, trans_list in translations.items():
        print(f"\n[INFO] Processing {lang_code}...")
        add_translations_to_po(lang_code, trans_list)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python compile_translations.py")
    print("2. Restart server")
    print("3. Clear browser cache (Ctrl+F5)")

if __name__ == '__main__':
    main()
