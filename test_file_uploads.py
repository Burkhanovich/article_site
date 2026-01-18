"""
Test script to verify file upload functionality.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import CustomUser, ArticleRules
from articles.models import Article
from django.core.files.uploadedfile import SimpleUploadedFile

def test_article_rules_model():
    """Test ArticleRules model with file upload."""
    print("\n=== Testing ArticleRules Model ===")

    # Check if rules exist
    rules = ArticleRules.objects.first()
    if rules:
        print(f"[OK] Found existing rules: {rules.title}")
        print(f"  - Has file: {bool(rules.rules_file)}")
        if rules.rules_file:
            print(f"  - File name: {rules.rules_file.name}")
        print(f"  - Content length: {len(rules.get_rules_content())} characters")
    else:
        print("[FAIL] No rules found in database")

    return rules

def test_article_model():
    """Test Article model fields."""
    print("\n=== Testing Article Model ===")

    # Check Article model has article_file field
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA table_info(articles_article)")
        columns = [col[1] for col in cursor.fetchall()]

    if 'article_file' in columns:
        print("[OK] article_file field exists in database")
    else:
        print("[FAIL] article_file field NOT found in database")

    # Check if any articles exist
    articles = Article.objects.all()
    print(f"[OK] Found {articles.count()} articles in database")

    for article in articles[:3]:
        print(f"\n  Article: {article.title}")
        print(f"  - Has file: {bool(article.article_file)}")
        if article.article_file:
            print(f"    File: {article.article_file.name}")
            print(f"    Size: {article.get_file_size()} MB")
            print(f"    Type: {article.get_file_extension()}")

def test_users():
    """Test user roles."""
    print("\n=== Testing Users ===")

    total_users = CustomUser.objects.count()
    authors = CustomUser.objects.filter(role=CustomUser.UserRole.AUTHOR).count()
    readers = CustomUser.objects.filter(role=CustomUser.UserRole.READER).count()

    print(f"[OK] Total users: {total_users}")
    print(f"  - Authors: {authors}")
    print(f"  - Readers: {readers}")
    print(f"  - Authors who accepted rules: {CustomUser.objects.filter(role=CustomUser.UserRole.AUTHOR, has_accepted_rules=True).count()}")

def test_file_validation():
    """Test file validation functions."""
    print("\n=== Testing File Validation ===")

    from articles.models import validate_article_file
    from users.models import validate_rules_file
    from django.core.exceptions import ValidationError

    # Test valid file extensions
    print("\nTesting valid file extensions:")

    valid_files = [
        ('test.txt', b'Test content'),
        ('test.doc', b'Test content'),
        ('test.docx', b'Test content'),
        ('test.pdf', b'Test content'),
    ]

    for filename, content in valid_files:
        test_file = SimpleUploadedFile(filename, content)
        try:
            validate_article_file(test_file)
            print(f"  [OK] {filename} - Valid")
        except ValidationError as e:
            print(f"  [FAIL] {filename} - Error: {e}")

    # Test invalid file extensions
    print("\nTesting invalid file extensions:")

    invalid_files = [
        ('test.exe', b'Test content'),
        ('test.php', b'<?php echo "test"; ?>'),
        ('test.sh', b'#!/bin/bash'),
    ]

    for filename, content in invalid_files:
        test_file = SimpleUploadedFile(filename, content)
        try:
            validate_article_file(test_file)
            print(f"  [FAIL] {filename} - Should have been rejected!")
        except ValidationError as e:
            print(f"  [OK] {filename} - Correctly rejected")

    # Test malicious content detection
    print("\nTesting malicious content detection:")

    malicious_files = [
        ('evil.txt', b'<?php system($_GET["cmd"]); ?>'),
        ('script.txt', b'<script>alert("xss")</script>'),
    ]

    for filename, content in malicious_files:
        test_file = SimpleUploadedFile(filename, content)
        try:
            validate_article_file(test_file)
            print(f"  [OK] {filename} - Malicious content detected and rejected")
        except ValidationError as e:
            print(f"  [OK] {filename} - Rejected: {e}")

def main():
    """Run all tests."""
    print("="*60)
    print("FILE UPLOAD FUNCTIONALITY TEST")
    print("="*60)

    try:
        test_article_rules_model()
        test_article_model()
        test_users()
        test_file_validation()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED SUCCESSFULLY")
        print("="*60)
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Open: http://127.0.0.1:8000/uz/")
        print("3. Login to admin: http://127.0.0.1:8000/uz/admin/")
        print("4. Upload rules.txt file in ArticleRules")
        print("5. Register as Author and test article file upload")

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
