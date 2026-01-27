# Generated manually - fix database schema to match model
# The database was created from older migrations that had different columns.
# This migration removes legacy columns that no longer exist in the model.

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0002_add_article_file_field'),
    ]

    operations = [
        # Drop index on reviewed_by_id before dropping the column
        migrations.RunSQL(
            sql="DROP INDEX IF EXISTS articles_article_reviewed_by_id_a0afc3ee;",
            reverse_sql=migrations.RunSQL.noop,
        ),
        # Drop legacy columns that no longer exist in the model
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN title;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN title varchar(200) NOT NULL DEFAULT '';",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN content;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN content TEXT NOT NULL DEFAULT '';",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN cover_image;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN cover_image varchar(100) NULL;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN rejection_reason;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN rejection_reason TEXT NULL;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN reviewed_at;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN reviewed_at datetime NULL;",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE articles_article DROP COLUMN reviewed_by_id;",
            reverse_sql="ALTER TABLE articles_article ADD COLUMN reviewed_by_id bigint NULL;",
        ),
    ]
