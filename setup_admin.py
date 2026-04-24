"""
Setup script to create admin user and test reviewers
"""
import os
import django

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser
from articles.models import Category

# Admin akkaunt yaratish yoki tekshirish
admin_exists = CustomUser.objects.filter(username='admin').exists()
if admin_exists:
    admin = CustomUser.objects.get(username='admin')
    print(f"✓ Admin akkaunt mavjud: {admin.username}")
    print(f"  Role: {admin.role}")
    print(f"  is_admin_user: {admin.is_admin_user}")
else:
    print("✗ Admin akkaunt yo'q, yaratilmoqda...")
    admin = CustomUser.objects.create_user(
        username='admin',
        email='admin@test.com',
        password='admin123',
        role=CustomUser.UserRole.ADMIN,
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True
    )
    print(f"✓ Admin akkaunt yaratildi!")
    print(f"  Username: {admin.username}")
    print(f"  Password: admin123")
    print(f"  Email: {admin.email}")

# Reviewer akkaunt yaratish
print("\n" + "="*60)
reviewer_count = CustomUser.objects.filter(role=CustomUser.UserRole.REVIEWER).count()
print(f"Mavjud Reviewers: {reviewer_count}")

if reviewer_count == 0:
    print("\nTest Reviewers yaratilmoqda...")
    for i in range(1, 3):
        reviewer = CustomUser.objects.create_user(
            username=f'reviewer{i}',
            email=f'reviewer{i}@test.com',
            password='reviewer123',
            role=CustomUser.UserRole.REVIEWER,
            first_name=f'Reviewer',
            last_name=f'{i}'
        )
        print(f"✓ Reviewer {i} yaratildi: {reviewer.username}")

# Kategoriya tekshirish
print("\n" + "="*60)
category_count = Category.objects.count()
print(f"Mavjud Kategoriyalar: {category_count}")

if category_count == 0:
    print("\nTest Kategoriya yaratilmoqda...")
    category = Category.objects.create(
        name_uz='Test Kategoriya',
        name_ru='Тестовая категория',
        name_en='Test Category',
        slug='test-category'
    )
    print(f"✓ Kategoriya yaratildi: {category.name_uz}")

print("\n" + "="*60)
print("✅ ADMIN PANEL SETUP COMPLETE!")
print("\n📍 Admin Panel URL:")
print("   → http://localhost:8000/uz/admin-panel/")
print("\n👤 Login Credentials:")
print("   Username: admin")
print("   Password: admin123")
print("\n📋 Admin Panel Features:")
print("   ✓ Reviewers qo'shish (Add Reviewers)")
print("   ✓ Kategoriyalarni sozlash (Manage Categories)")
print("   ✓ Maqolalarni boshqarish (Manage Articles)")
print("   ✓ Statistikani ko'rish (View Statistics)")
print("\n" + "="*60)
