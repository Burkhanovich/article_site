"""
Admin Panel for Article Publishing Platform

This module provides a dedicated admin control panel for managing:
1. Reviewer users (CRUD operations)
2. Category management and reviewer assignments
3. Article review workflow and status control
4. System-wide statistics and analytics

## Features

### 1. Reviewer Management
- Create new reviewer accounts with assigned categories
- Edit reviewer details and category assignments
- View reviewer profiles with review statistics
- Delete reviewers from the system

### 2. Category Management
- View all active categories with review statistics
- Assign reviewers to categories
- Configure category-specific workflow policies:
  - Minimum approvals required for publication
  - Maximum rejections before blocking article
  - Review deadline settings
  - Admin override permissions
  - Comment requirements for rejection/changes

### 3. Article Management
- Filter articles by status
- Take individual actions on articles:
  - Publish articles
  - Reject articles (with notes)
  - Request changes from authors
  - Reset article status
- Perform bulk actions on multiple articles
- View article details and review history

### 4. System Statistics
- Article statistics by status
- Articles distribution by category
- User management statistics
- Review statistics and analysis

## Access Control

Only users with role='ADMIN' or is_superuser=True can access the admin panel.
Access is secured via the AdminAccessMixin which redirects non-admin users.

## URL Patterns

- /admin-panel/                          - Dashboard (main entry point)
- /admin-panel/reviewers/                - List all reviewers
- /admin-panel/reviewers/create/         - Create new reviewer
- /admin-panel/reviewers/<id>/           - View reviewer details
- /admin-panel/reviewers/<id>/edit/      - Edit reviewer
- /admin-panel/reviewers/<id>/delete/    - Delete reviewer
- /admin-panel/categories/               - Manage categories
- /admin-panel/categories/<id>/assign-reviewers/ - Assign reviewers to category
- /admin-panel/categories/<id>/policy/   - Configure category policy
- /admin-panel/articles/                 - Manage articles
- /admin-panel/articles/<slug>/action/   - Take action on article
- /admin-panel/articles/bulk-action/     - Perform bulk actions
- /admin-panel/statistics/               - View system statistics

## Using the Admin Panel

### Accessing the Panel
1. Login as an admin user
2. Click on your username dropdown in the navbar
3. Select "Admin Panel" option (only visible to admins)

### Creating a Reviewer
1. Go to Admin Panel > Manage Reviewers
2. Click "Add New Reviewer"
3. Fill in reviewer details:
   - Username and email (must be unique)
   - First and last name
   - Organization and biography
   - Password (secure password required)
   - Assigned categories (select which categories they can review)
4. Click "Save"

### Assigning Reviewers to Categories
1. Go to Admin Panel > Manage Categories
2. Click "Assign Reviewers" for the category
3. Select reviewers to assign to this category
4. Click "Save Assignments"

### Configuring Category Policies
1. Go to Admin Panel > Manage Categories
2. Click "Policy" for the category
3. Configure workflow settings:
   - **Minimum Approvals to Publish**: How many reviewer approvals needed
   - **Minimum Required Reviews**: Total reviews needed before decision
   - **Maximum Rejections Before Block**: When article gets blocked
   - **Review Deadline**: Optional deadline for reviewers (in hours)
   - **Allow Admin Override**: Whether admin can bypass review voting
   - **Require Comments**: Whether reviewers must comment on rejection/changes
4. Click "Save Policy"

### Managing Articles
1. Go to Admin Panel > Article Management
2. Filter by status or search for specific articles
3. Click "Review" for an article to take action
4. Choose action:
   - **Publish Article**: Mark as published (visible to readers)
   - **Reject Article**: Mark as rejected with explanation
   - **Request Changes**: Send feedback to author
   - **Reset to In Review**: Reset status for re-review
5. Add optional admin notes (visible to author)
6. Click "Apply Action"

### Bulk Article Actions
1. Go to Admin Panel > Article Management
2. Select multiple articles using checkboxes
3. Choose bulk action from dropdown:
   - Publish Selected
   - Reject Selected
   - Request Changes on Selected
4. Click "Apply"
5. Add notes if needed for rejection/changes

### Viewing Statistics
1. Go to Admin Panel > Statistics
2. View comprehensive system analytics:
   - Total articles and status distribution
   - User management statistics
   - Review statistics
   - Articles per category

## Forms and Validation

### ReviewerCreationForm
- Username: Unique, required
- Email: Unique email address, required
- Password: Must be confirmed, secure password validation
- Categories: Multiple categories can be assigned

### ReviewerEditForm
- Can update all user details
- Can change category assignments
- Can activate/deactivate account

### CategoryPolicyForm
- Integer validation for all numeric fields
- Deadline hours must be positive if specified
- Policy changes apply immediately

### ArticleActionForm
- Requires action selection
- Optional notes for rejection/changes
- Admin note visible to article author

## Security Considerations

1. Only admins can access the panel (AdminAccessMixin)
2. All forms have CSRF protection
3. User actions are logged (admin_decision_by and admin_decision_at)
4. Email/username uniqueness enforced
5. Password hashing for reviewer accounts

## Performance Optimizations

1. select_related() used for foreign keys
2. annotate() with Count for statistics
3. Pagination on list views (20 items per page)
4. Database indexes on frequently queried fields

## Testing

Admin panel includes data-test attributes for testing:
- data-test="reviewer-row-{id}" - Reviewer list rows
- data-test="article-row-{id}" - Article rows
- data-test="action-form" - Action form
- data-test="filter-form" - Filter form

## Customization

### Adding New Admin Views
1. Create view class in views.py inheriting from AdminAccessMixin
2. Add URL pattern in urls.py
3. Create template in templates/admin_panel/

### Customizing Category Policy
Modify CategoryPolicyForm to add/remove policy fields as needed.

### Adding More Statistics
Extend SystemStatsView.get_context_data() to add custom statistics.

## Common Tasks

### How to remove a reviewer but keep their articles?
- Go to reviewer detail page
- Click "Edit"
- Uncheck all assigned categories
- The reviewer stays in system but has no active assignments

### How to view a reviewer's review history?
- Go to Admin Panel > Manage Reviewers
- Click "View" on the reviewer
- Scroll to "Recent Reviews" section

### How to find articles needing action?
- Go to Admin Panel > Article Management
- Filter by status "Pending Admin Review"
- Articles are sorted by submission date

### How to check overall system health?
- Go to Admin Panel > Statistics
- Review article status distribution
- Check user role distribution
- Review completion rates

## Error Handling

- Non-admin users: Redirected to home with error message
- Missing objects: 404 error pages
- Form validation: Error messages displayed on forms
- Bulk actions: Shows count of successful updates

## Future Enhancements

Potential improvements for the admin panel:
1. Email notifications to reviewers for new articles
2. Review deadline reminders
3. Activity logs for all admin actions
4. Export statistics to CSV/PDF reports
5. Batch reviewer password reset
6. Article timeline visualization
7. Performance analytics dashboard
8. Integration with email service for notifications
"""
