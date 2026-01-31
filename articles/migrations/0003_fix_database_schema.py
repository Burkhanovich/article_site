# Generated manually - fix database schema to match model
# The database was created from older migrations that had different columns.
# This migration removes legacy columns that no longer exist in the model.
# Uses conditional logic to safely run on both existing and fresh databases.

from django.db import migrations, connection


def drop_column_if_exists(apps, schema_editor):
    """
    Drop legacy columns if they exist. Safe for both existing and fresh databases.
    """
    columns_to_drop = ['title', 'content', 'cover_image', 'rejection_reason', 'reviewed_at', 'reviewed_by_id']

    # Check which columns exist
    with connection.cursor() as cursor:
        # Get existing columns for articles_article table
        cursor.execute("PRAGMA table_info(articles_article);")
        existing_columns = {row[1] for row in cursor.fetchall()}

        for column in columns_to_drop:
            if column in existing_columns:
                # SQLite doesn't support DROP COLUMN directly in older versions
                # This is a no-op for fresh databases
                try:
                    # For SQLite 3.35.0+, DROP COLUMN is supported
                    cursor.execute(f"ALTER TABLE articles_article DROP COLUMN {column};")
                except Exception:
                    # Silently ignore if column doesn't exist or can't be dropped
                    pass


def noop(apps, schema_editor):
    """Reverse migration - no-op."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_add_article_file_field'),
    ]

    operations = [
        migrations.RunPython(drop_column_if_exists, noop),
    ]
