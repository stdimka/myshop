from django.db import migrations

def create_default_category(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Category.objects.get_or_create(
        id=1,
        defaults={'name': 'General', 'slug': 'general'}
    )

def reverse_create_default_category(apps, schema_editor):
    Category = apps.get_model('shop', 'Category')
    Category.objects.filter(id=1, name='General').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('shop', '0002_alter_product_category'),  # ← имя предыдущей миграции
    ]

    operations = [
        migrations.RunPython(create_default_category, reverse_create_default_category),
    ]