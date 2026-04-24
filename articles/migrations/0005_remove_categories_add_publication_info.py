# Generated migration to remove categories and review_mode, add publication year and number

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0004_add_reviewer_assignment'),
    ]

    operations = [
        # Add new fields
        migrations.AddField(
            model_name='article',
            name='publication_year',
            field=models.IntegerField(null=True, blank=True, verbose_name='Publication Year'),
        ),
        migrations.AddField(
            model_name='article',
            name='publication_number',
            field=models.IntegerField(null=True, blank=True, verbose_name='Publication Number'),
        ),
        
        # Remove old fields
        migrations.RemoveField(
            model_name='article',
            name='categories',
        ),
        migrations.RemoveField(
            model_name='article',
            name='review_mode',
        ),
    ]
