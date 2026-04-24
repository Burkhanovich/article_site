# Generated migration for Journal model and review_deadline field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0006_make_review_category_optional'),
    ]

    operations = [
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveIntegerField(help_text='Publication year (e.g., 2026)', verbose_name='Year')),
                ('number', models.PositiveIntegerField(help_text='Journal issue number', verbose_name='Number')),
                ('description', models.TextField(blank=True, null=True, verbose_name='Description')),
                ('is_active', models.BooleanField(default=True, help_text='Active journals are available for article submission', verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Journal',
                'verbose_name_plural': 'Journals',
                'ordering': ['-year', '-number'],
            },
        ),
        migrations.AddField(
            model_name='reviewerassignment',
            name='review_deadline',
            field=models.DateTimeField(blank=True, help_text='Deadline by which the reviewer should complete the review', null=True, verbose_name='Review Deadline'),
        ),
        migrations.AddConstraint(
            model_name='journal',
            constraint=models.UniqueConstraint(fields=['year', 'number'], name='unique_year_number'),
        ),
    ]
