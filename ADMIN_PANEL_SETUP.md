# Admin Panel Setup Guide

## Overview
The admin panel has been successfully created as a new Django application. It provides comprehensive control over:
- Reviewer user management (CRUD operations)
- Category and reviewer assignments
- Article workflow and status control
- System-wide statistics and analytics

## Installation Steps

### 1. Add to Django Settings
The `admin_panel` app has already been added to `INSTALLED_APPS` in `config/settings.py`.

### 2. Update URLs
The admin panel URLs have been added to `config/urls.py`:
```python
path('admin-panel/', include('admin_panel.urls')),
```

This makes the admin panel accessible at:
- Base URL: `/admin-panel/`
- With language prefix: `/uz/admin-panel/` or `/ru/admin-panel/` or `/en/admin-panel/`

### 3. Database Setup
No new models were created for the admin panel, so no migrations are needed.
The panel uses existing models: User, Article, Category, CategoryPolicy, Review

### 4. Access the Admin Panel
1. Login as an admin user (role='ADMIN' or is_superuser=True)
2. In the navbar, click on your username dropdown
3. Select "Admin Panel" (only visible to admins)
4. Or navigate directly to: `localhost:8000/uz/admin-panel/` (with your language code)

## Key Features

### 1. Reviewer Management
- **View**: Navigate to "Manage Reviewers" in admin sidebar
- **Create**: Click "Add New Reviewer" button
- **Edit**: Click "Edit" on any reviewer
- **Delete**: Click "Delete" (with confirmation)
- **Details**: Click "View" to see full profile and review statistics

### 2. Category Management
- **View Categories**: Click "Manage Categories"
- **Assign Reviewers**: Click "Assign Reviewers" button for each category
- **Configure Policy**: Click "Policy" to set review workflow rules

### 3. Article Management
- **Filter**: By status (Draft, In Review, Published, etc.)
- **Search**: By title, author name, or email
- **Single Action**: Click "Review" to publish, reject, or request changes
- **Bulk Actions**: Select multiple articles and apply action to all

### 4. System Statistics
- Click "Statistics" in sidebar to view:
  - Article distribution by status
  - Articles per category
  - User statistics by role
  - Review completion data

## File Structure

```
admin_panel/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py              # All form definitions
├── models.py             # (Currently empty)
├── urls.py               # URL routing
├── views.py              # View classes
├── tests.py              # Unit tests
└── README.md             # Detailed documentation

templates/admin_panel/
├── base.html             # Admin layout template
├── dashboard.html        # Main dashboard
├── reviewer_list.html    # Reviewer list with search
├── reviewer_form.html    # Create/Edit reviewer form
├── reviewer_detail.html  # Reviewer profile
├── category_manage.html  # Category management
├── category_reviewer_assign.html  # Assign reviewers
├── category_policy_form.html      # Policy configuration
├── article_manage.html   # Article list with filters
├── article_action.html   # Single article action
├── bulk_article_action.html       # Bulk article actions
├── system_stats.html     # Statistics dashboard
└── reviewer_confirm_delete.html   # Delete confirmation
```

## Navbar Integration

The admin panel link has been added to the main navbar in `templates/base.html`:
- Only visible to users with role='ADMIN' or is_superuser=True
- Located in user dropdown menu
- Labeled with "Admin Panel" and admin icon

## Security

- **Access Control**: AdminAccessMixin prevents non-admin access
- **CSRF Protection**: All forms have {% csrf_token %}
- **Authentication**: LoginRequiredMixin on all views
- **Authorization**: Role-based access checks
- **Audit Trail**: admin_decision_by and admin_decision_at fields track who did what

## Testing

Run the test suite with:
```bash
python manage.py test admin_panel
```

Tests cover:
- Access control
- Reviewer CRUD operations
- Category management
- Article actions
- Dashboard functionality

## Common Operations

### Create a Reviewer
1. Go to Admin Panel > Manage Reviewers
2. Click "Add New Reviewer"
3. Fill in details and assign categories
4. Click "Save"

### Assign Reviewers to Category
1. Go to Admin Panel > Manage Categories
2. Find the category and click "Assign Reviewers"
3. Check/uncheck reviewers
4. Click "Save Assignments"

### Configure Review Workflow
1. Go to Admin Panel > Manage Categories
2. Click "Policy" for the category
3. Set minimum approvals, deadline, etc.
4. Click "Save Policy"

### Publish/Reject Article
1. Go to Admin Panel > Article Management
2. Click "Review" on an article
3. Select action (Publish, Reject, Request Changes)
4. Add optional notes
5. Click "Apply Action"

### Perform Bulk Actions
1. Go to Admin Panel > Article Management
2. Select multiple articles with checkboxes
3. Choose bulk action from dropdown
4. Click "Apply"

## Configuration Examples

### Strict Review Policy
- Min Approvals: 3
- Min Required Reviews: 3
- Max Rejections: 1
- Deadline: 72 hours
- Admin Override: Enabled

### Lenient Review Policy
- Min Approvals: 1
- Min Required Reviews: 2
- Max Rejections: 3
- Deadline: 168 hours (1 week)
- Admin Override: Disabled

### Emergency Override Policy
- Min Approvals: 1
- Min Required Reviews: 1
- Max Rejections: 0
- Deadline: None
- Admin Override: Enabled

## URL Reference

| Page | URL | Purpose |
|------|-----|---------|
| Dashboard | `/admin-panel/` | Overview & stats |
| Reviewers | `/admin-panel/reviewers/` | List reviewers |
| Create Reviewer | `/admin-panel/reviewers/create/` | Add new reviewer |
| Reviewer Detail | `/admin-panel/reviewers/<id>/` | View profile |
| Edit Reviewer | `/admin-panel/reviewers/<id>/edit/` | Modify details |
| Delete Reviewer | `/admin-panel/reviewers/<id>/delete/` | Remove reviewer |
| Categories | `/admin-panel/categories/` | Manage categories |
| Assign Reviewers | `/admin-panel/categories/<id>/assign-reviewers/` | Link reviewers |
| Category Policy | `/admin-panel/categories/<id>/policy/` | Configure workflow |
| Articles | `/admin-panel/articles/` | Manage articles |
| Article Action | `/admin-panel/articles/<slug>/action/` | Publish/Reject |
| Bulk Actions | `/admin-panel/articles/bulk-action/` | Multiple articles |
| Statistics | `/admin-panel/statistics/` | View analytics |

## Troubleshooting

### Admin panel not visible
- Ensure user role is 'ADMIN' or is_superuser=True
- Check that admin_panel app is in INSTALLED_APPS

### Forms not submitting
- Check CSRF token is present
- Verify form data is valid
- Check browser console for JavaScript errors

### Categories not showing reviewers
- Ensure reviewers exist in database
- Verify role is set to 'REVIEWER'
- Check reviewer is marked as active (is_active=True)

### Articles not filtering
- Make sure article status values are correct
- Verify article exists in database
- Check search terms are complete words

## Performance Notes

- Reviewer list uses pagination (20 per page)
- Category list uses annotation for review counts
- Article list uses select_related for author data
- Dashboard statistics use aggregation queries

## Next Steps

1. Create test admin user:
   ```bash
   python manage.py shell
   from users.models import CustomUser
   CustomUser.objects.create_user(
       username='admin',
       email='admin@example.com',
       password='secure_password',
       role='ADMIN'
   )
   ```

2. Start Django development server:
   ```bash
   python manage.py runserver
   ```

3. Access admin panel:
   - http://localhost:8000/uz/admin-panel/
   - Login with admin credentials
   - Start managing reviewers and content

## Support

For more detailed information, see:
- `admin_panel/README.md` - Comprehensive feature documentation
- `admin_panel/views.py` - View implementation details
- `admin_panel/forms.py` - Form definitions and validation
- `admin_panel/tests.py` - Test examples

## License

Part of the Article Publishing Platform
