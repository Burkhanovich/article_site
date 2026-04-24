"""
Script to find all translatable strings and check which ones are missing translations.
"""
import re
import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

def extract_trans_strings():
    """Extract all translatable strings from templates and Python code."""
    trans_strings = set()
    
    # From templates
    for root, dirs, files in os.walk('templates'):
        # Skip emails directory
        if 'emails' in root:
            continue
        for f in files:
            if f.endswith('.html'):
                path = os.path.join(root, f)
                with open(path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                # {% trans "string" %} and {% trans 'string' %}
                matches = re.findall(r'{%\s*trans\s+"(.*?)"', content)
                trans_strings.update(matches)
                matches = re.findall(r"{%\s*trans\s+'(.*?)'", content)
                trans_strings.update(matches)
    
    # From Python files
    py_dirs = ['articles', 'users', 'admin_panel', 'core']
    for d in py_dirs:
        for root, dirs, files in os.walk(d):
            if '__pycache__' in root or 'migrations' in root:
                continue
            for f in files:
                if f.endswith('.py'):
                    path = os.path.join(root, f)
                    with open(path, 'r', encoding='utf-8') as fh:
                        content = fh.read()
                    # _("string") and _('string')
                    matches = re.findall(r'_\("(.*?)"', content)
                    trans_strings.update(matches)
                    matches = re.findall(r"_\('(.*?)'", content)
                    trans_strings.update(matches)
    
    return trans_strings


def get_po_entries(po_path):
    """Read existing .po file and return set of msgid strings."""
    import polib
    po = polib.pofile(po_path)
    entries = {}
    for entry in po:
        entries[entry.msgid] = entry.msgstr
    return entries


def main():
    import polib
    
    trans_strings = extract_trans_strings()
    print(f"Total unique translatable strings found: {len(trans_strings)}")
    print()
    
    languages = ['uz', 'ru', 'en']
    
    for lang in languages:
        po_path = f'locale/{lang}/LC_MESSAGES/django.po'
        if not os.path.exists(po_path):
            print(f"WARNING: {po_path} does not exist!")
            continue
        
        entries = get_po_entries(po_path)
        existing_msgids = set(entries.keys())
        
        # Find missing strings
        missing = []
        empty = []
        for s in sorted(trans_strings):
            if s not in existing_msgids:
                missing.append(s)
            elif not entries.get(s, '').strip():
                empty.append(s)
        
        print(f"=== {lang.upper()} ===")
        print(f"  Entries in .po: {len(existing_msgids)}")
        print(f"  Missing from .po: {len(missing)}")
        print(f"  Empty translation: {len(empty)}")
        
        if missing:
            print(f"  --- MISSING ---")
            for m in missing:
                print(f"    {repr(m)}")
        
        if empty:
            print(f"  --- EMPTY TRANSLATION ---")
            for e in empty:
                print(f"    {repr(e)}")
        
        print()


if __name__ == '__main__':
    main()
