#!/usr/bin/env python
"""
Compile .po files to .mo files without requiring gettext.
This script uses Python's built-in msgfmt functionality.
"""
import os
import sys
from pathlib import Path

def compile_po_file(po_file):
    """Compile a single .po file to .mo format."""
    try:
        from django.core.management.commands.compilemessages import Command
        import polib

        # Use polib if available
        po = polib.pofile(str(po_file))
        mo_file = po_file.with_suffix('.mo')
        po.save_as_mofile(str(mo_file))
        print(f"[OK] Compiled: {po_file} -> {mo_file}")
        return True
    except ImportError:
        # Fallback: Try using msgfmt.py from Python's tools
        try:
            import msgfmt
            mo_file = po_file.with_suffix('.mo')
            msgfmt.make(str(po_file), str(mo_file))
            print(f"[OK] Compiled: {po_file} -> {mo_file}")
            return True
        except:
            print(f"[ERROR] Could not compile: {po_file}")
            print("  Install polib: pip install polib")
            return False

def main():
    """Find and compile all .po files in the locale directory."""
    base_dir = Path(__file__).resolve().parent
    locale_dir = base_dir / 'locale'

    if not locale_dir.exists():
        print(f"Error: locale directory not found at {locale_dir}")
        return 1

    # Find all .po files
    po_files = list(locale_dir.rglob('*.po'))

    if not po_files:
        print(f"No .po files found in {locale_dir}")
        return 1

    print(f"Found {len(po_files)} .po file(s) to compile:\n")

    success_count = 0
    for po_file in po_files:
        if compile_po_file(po_file):
            success_count += 1

    print(f"\n{'='*60}")
    print(f"Compilation complete: {success_count}/{len(po_files)} files compiled")
    print(f"{'='*60}")

    if success_count < len(po_files):
        print("\nTo install polib for compilation:")
        print("  pip install polib")
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
