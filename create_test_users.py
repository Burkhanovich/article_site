"""
Create test users for testing the platform.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser

def create_test_users():
    """Create test users for different roles."""
    print("="*60)
    print("TEST FOYDALANUVCHILARNI YARATISH")
    print("="*60)

    users_to_create = [
        {
            'username': 'test_author',
            'email': 'author@test.com',
            'password': 'test123456',
            'role': CustomUser.UserRole.AUTHOR,
            'has_accepted_rules': False
        },
        {
            'username': 'test_reader',
            'email': 'reader@test.com',
            'password': 'test123456',
            'role': CustomUser.UserRole.READER,
            'has_accepted_rules': False
        }
    ]

    print("\n[INFO] Foydalanuvchilar yaratilmoqda...\n")

    for user_data in users_to_create:
        # Check if user already exists
        if CustomUser.objects.filter(username=user_data['username']).exists():
            print(f"[SKIP] {user_data['username']} - allaqachon mavjud")
            continue

        # Create user
        user = CustomUser.objects.create_user(
            username=user_data['username'],
            email=user_data['email'],
            password=user_data['password']
        )
        user.role = user_data['role']
        user.has_accepted_rules = user_data['has_accepted_rules']
        user.save()

        print(f"[OK] {user_data['username']} yaratildi")
        print(f"     Email: {user_data['email']}")
        print(f"     Parol: {user_data['password']}")
        print(f"     Rol: {user.get_role_display()}")
        print()

    print("="*60)
    print("TEST UCHUN MA'LUMOTLAR")
    print("="*60)
    print("\n1. AUTHOR ACCOUNT (Maqola yozish uchun):")
    print("   Username: test_author")
    print("   Parol: test123456")
    print("   Login: http://127.0.0.1:8000/uz/users/login/")
    print()
    print("2. READER ACCOUNT (O'qish uchun):")
    print("   Username: test_reader")
    print("   Parol: test123456")
    print()
    print("3. ADMIN ACCOUNT:")
    print("   Username: admin")
    print("   Parol: [sizning admin parolingiz]")
    print("   Admin panel: http://127.0.0.1:8000/uz/admin/")
    print()
    print("="*60)
    print("BARCHA FOYDALANUVCHILAR RO'YXATI:")
    print("="*60)

    all_users = CustomUser.objects.all().order_by('-date_joined')
    for user in all_users:
        print(f"• {user.username} ({user.get_role_display()}) - {user.email}")
        if user.is_staff:
            print("  [ADMIN]")

    print(f"\nJami: {all_users.count()} ta foydalanuvchi")

if __name__ == '__main__':
    try:
        create_test_users()
    except Exception as e:
        print(f"\n[ERROR] Xatolik: {e}")
        import traceback
        traceback.print_exc()
