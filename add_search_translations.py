"""
Add search functionality translations to .po files.
"""
import os

# New translations
translations = {
    'uz': [
        ('Search by title, author, or content...', 'Sarlavha, muallif yoki kontent bo\'yicha qidiring...'),
    ],
    'ru': [
        ('Search by title, author, or content...', 'Поиск по заголовку, автору или содержанию...'),
    ],
    'en': [
        ('Search by title, author, or content...', 'Search by title, author, or content...'),
    ]
}

def add_translations_to_po(lang_code, trans_list):
    """Add translations to a .po file."""
    po_file = f'locale/{lang_code}/LC_MESSAGES/django.po'

    if not os.path.exists(po_file):
        print(f"[ERROR] {po_file} not found")
        return

    with open(po_file, 'a', encoding='utf-8') as f:
        f.write('\n\n# Search Functionality Translations\n')
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
    print("ADDING SEARCH TRANSLATIONS")
    print("=" * 60)

    for lang_code, trans_list in translations.items():
        print(f"\n[INFO] Processing {lang_code}...")
        add_translations_to_po(lang_code, trans_list)

    print("\n" + "=" * 60)
    print("DONE!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run: python compile_translations.py")
    print("2. Restart server (if needed)")
    print("3. Clear browser cache (Ctrl+F5)")

if __name__ == '__main__':
    main()
