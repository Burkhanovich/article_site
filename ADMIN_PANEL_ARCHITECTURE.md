# Admin Panel Architecture & Workflow Diagrams

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Admin Navbar Link (Conditional)                                │
│    └─→ Admin Panel Dashboard                                    │
│        ├─→ Reviewer Management                                  │
│        │   ├─ List/Search (reviewer_list.html)                 │
│        │   ├─ Create (reviewer_form.html)                      │
│        │   ├─ Edit (reviewer_form.html)                        │
│        │   ├─ View Details (reviewer_detail.html)              │
│        │   └─ Delete (reviewer_confirm_delete.html)            │
│        │                                                        │
│        ├─→ Category Management                                  │
│        │   ├─ List Categories (category_manage.html)           │
│        │   ├─ Assign Reviewers (category_reviewer_assign.html) │
│        │   └─ Configure Policy (category_policy_form.html)     │
│        │                                                        │
│        ├─→ Article Management                                   │
│        │   ├─ List/Filter (article_manage.html)                │
│        │   ├─ Single Action (article_action.html)              │
│        │   └─ Bulk Actions (bulk_article_action.html)          │
│        │                                                        │
│        └─→ Statistics (system_stats.html)                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                         VIEW LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  AdminAccessMixin (Access Control)                              │
│    ↓                                                            │
│  AdminDashboardView                                             │
│  ReviewerListView, ReviewerCreateView, ReviewerEditView...     │
│  CategoryManageView, CategoryReviewerAssignView...              │
│  ArticleManageView, ArticleActionView, BulkArticleActionView   │
│  SystemStatsView                                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                         FORM LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ReviewerAssignmentForm                                        │
│  ReviewerCreationForm                                          │
│  ReviewerEditForm                                              │
│  CategoryPolicyForm                                            │
│  ArticleActionForm                                             │
│  BulkArticleActionForm                                         │
│                                                                 │
│  ↓ Validation ↓                                                │
│  Email uniqueness, Password confirmation, etc.                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        MODEL LAYER                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  CustomUser (admin_panel uses existing)                        │
│  Article (admin_panel uses existing)                           │
│  Category (admin_panel uses existing)                          │
│  CategoryPolicy (admin_panel uses existing)                    │
│  Review (admin_panel uses existing)                            │
│                                                                 │
│  No new models created - Uses existing app models              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATABASE LAYER                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  SQLite (Development) / PostgreSQL (Production)               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## User Permission Flow

```
┌─────────────────────┐
│   User Requests     │
│   Admin Panel URL   │
└──────────┬──────────┘
           │
           ↓
┌──────────────────────────────────────┐
│  LoginRequiredMixin                  │
│  Is user logged in?                  │
└──────────┬──────────┬────────────────┘
           │          │
        YES│          │NO
           │          └──→ Redirect to login
           │
           ↓
┌──────────────────────────────────────┐
│  AdminAccessMixin.test_func()        │
│  Is user.is_admin_user or superuser? │
└──────────┬──────────┬────────────────┘
           │          │
        YES│          │NO
           │          └──→ Error message + Redirect to home
           │
           ↓
┌──────────────────────────────────────┐
│  Admin Panel Access Granted          │
│  Render appropriate template         │
└──────────────────────────────────────┘
```

## Reviewer Management Workflow

```
START
  │
  ├─→ View Reviewers List
  │    └─ Search/Filter
  │    └─ Paginate results
  │
  ├─→ Create New Reviewer
  │    ├─ Fill form:
  │    │  ├─ Username (unique)
  │    │  ├─ Email (unique)
  │    │  ├─ First/Last name
  │    │  ├─ Organization
  │    │  ├─ Password (hashed)
  │    │  └─ Assign categories
  │    │
  │    └─ Form Validation:
  │       ├─ Email format
  │       ├─ Username unique
  │       ├─ Password strength
  │       └─ Passwords match
  │
  │    └─ Save to DB:
  │       ├─ Create user with REVIEWER role
  │       └─ Add to categories
  │
  ├─→ View Reviewer Profile
  │    ├─ Personal details
  │    ├─ Assigned categories
  │    ├─ Review statistics
  │    └─ Recent reviews
  │
  ├─→ Edit Reviewer
  │    ├─ Modify details
  │    ├─ Change categories
  │    └─ Toggle active status
  │
  └─→ Delete Reviewer
       ├─ Confirmation prompt
       ├─ Remove from categories
       └─ Delete from system

END
```

## Article Management Workflow

```
START: Admin Panel > Article Management
  │
  ├─→ Article List View
  │    ├─ Filter by status:
  │    │  ├─ DRAFT
  │    │  ├─ PENDING_ADMIN
  │    │  ├─ IN_REVIEW
  │    │  ├─ CHANGES_REQUESTED
  │    │  ├─ REJECTED
  │    │  └─ PUBLISHED
  │    │
  │    ├─ Search:
  │    │  ├─ By title
  │    │  ├─ By author name
  │    │  └─ By email
  │    │
  │    └─ Paginate (20 per page)
  │
  ├─→ Single Article Action
  │    ├─ View article details
  │    │  ├─ Title (all languages)
  │    │  ├─ Content preview
  │    │  ├─ Categories
  │    │  ├─ Author info
  │    │  └─ Review history
  │    │
  │    ├─ Select action:
  │    │  ├─ PUBLISH
  │    │  │  └─ Set status: PUBLISHED
  │    │  │  └─ Set published_at timestamp
  │    │  │
  │    │  ├─ REJECT
  │    │  │  └─ Set status: REJECTED
  │    │  │  └─ Add admin_note (visible to author)
  │    │  │
  │    │  ├─ REQUEST_CHANGES
  │    │  │  └─ Set status: CHANGES_REQUESTED
  │    │  │  └─ Add admin_note with feedback
  │    │  │
  │    │  └─ RESET_STATUS
  │    │     └─ Set status: IN_REVIEW
  │    │
  │    ├─ Record admin decision:
  │    │  ├─ admin_decision_by = current_user
  │    │  └─ admin_decision_at = now()
  │    │
  │    └─ Save to database
  │
  ├─→ Bulk Article Actions
  │    ├─ Select multiple articles (checkboxes)
  │    ├─ Choose bulk action
  │    │  ├─ Publish selected
  │    │  ├─ Reject selected
  │    │  └─ Request changes on selected
  │    │
  │    ├─ Optional admin notes
  │    │
  │    ├─ Apply action to each:
  │    │  ├─ Update status
  │    │  ├─ Record admin decision
  │    │  └─ Save to database
  │    │
  │    └─ Show success message with count
  │
  └─→ Redirect to article list

END
```

## Category & Policy Configuration Workflow

```
START: Admin Panel > Manage Categories
  │
  ├─→ View Categories List
  │    └─ Show:
  │       ├─ Category names (Uz, Ru, En)
  │       ├─ Reviewer count
  │       └─ Article count
  │
  ├─→ Assign Reviewers to Category
  │    ├─ Select category
  │    ├─ Show available reviewers:
  │    │  ├─ Filter role=REVIEWER
  │    │  └─ Sort by name
  │    │
  │    ├─ User selects/deselects reviewers
  │    │
  │    ├─ Save assignments:
  │    │  ├─ Clear old assignments
  │    │  ├─ Add selected reviewers
  │    │  └─ Update category.reviewers M2M
  │    │
  │    └─ Confirm with success message
  │
  ├─→ Configure Category Policy
  │    ├─ Get/create CategoryPolicy for category
  │    │
  │    ├─ Configure settings:
  │    │  ├─ min_approvals_to_publish (int)
  │    │  ├─ min_required_reviews (int)
  │    │  ├─ max_rejections_before_block (int)
  │    │  ├─ review_deadline_hours (optional int)
  │    │  ├─ allow_admin_override (bool)
  │    │  ├─ require_changes_comment (bool)
  │    │  └─ require_reject_comment (bool)
  │    │
  │    ├─ Validate form:
  │    │  ├─ Min/max values
  │    │  ├─ Required fields
  │    │  └─ Type validation
  │    │
  │    └─ Save policy to database
  │
  └─→ Redirect to category list

END
```

## Data Flow Diagram

```
┌──────────────┐
│   Browser    │ User fills form
└────┬─────────┘
     │ Form data (POST)
     ↓
┌──────────────────────────┐
│  Django View             │
│  (receives request)      │
└────┬─────────────────────┘
     │ Form validation
     ↓
┌──────────────────────────┐
│  Form Class              │
│  (validate form data)    │
└────┬─────────────────────┘
     │ if valid
     ↓
┌──────────────────────────┐
│  Model Instance          │
│  (create/update)         │
└────┬─────────────────────┘
     │ save()
     ↓
┌──────────────────────────┐
│  Database                │
│  (persist data)          │
└────┬─────────────────────┘
     │ success
     ↓
┌──────────────────────────┐
│  View (redirect)         │
│  Success message         │
└────┬─────────────────────┘
     │ Render response
     ↓
┌──────────────┐
│   Browser    │ Display success page
└──────────────┘
```

## Access Control Flow

```
Admin User Request
  │
  ├─→ Authentication Check (LoginRequiredMixin)
  │    ├─ User logged in? ✓
  │    └─ Continue
  │
  ├─→ Authorization Check (AdminAccessMixin)
  │    ├─ user.is_admin_user == True? ✓
  │    └─ Continue
  │
  └─→ View Execution
       ├─ Get data from DB
       ├─ Render template with data
       └─ Return response to user

Non-Admin User Request
  │
  ├─→ Authentication Check
  │    ├─ User logged in? ✓
  │    └─ Continue
  │
  ├─→ Authorization Check
  │    ├─ user.is_admin_user == True? ✗
  │    └─ Call handle_no_permission()
  │
  └─→ Error Handling
       ├─ Show error message
       ├─ Redirect to home
       └─ Return redirect response
```

## Database Relationships (Admin Panel Perspective)

```
┌──────────────────┐
│   CustomUser     │
│   (ADMIN role)   │
└────────┬─────────┘
         │ 1
         │ admin to many
         │
         ├──→ Article (admin_decision_by)
         │    └─ Track who published/rejected
         │
         └──→ Reviewer Assignment (via UI)
              └─ Assign reviewers to categories

┌──────────────────┐
│   CustomUser     │
│   (REVIEWER role)│
└────────┬─────────┘
         │ M2M
         │
         ├──→ Category (reviewers)
         │    └─ What categories can review
         │
         └──→ Review (reviewer FK)
              └─ Reviews submitted by reviewer

┌──────────────────┐
│   Category       │
└────────┬─────────┘
         │ 1
         │
         ├──→ CategoryPolicy (1:1)
         │    └─ Workflow configuration
         │
         ├──→ Article (M2M)
         │    └─ Articles in category
         │
         └──→ CustomUser (M2M, reviewers)
              └─ Assigned reviewers

┌──────────────────┐
│   Article        │
└────────┬─────────┘
         │
         ├──→ CustomUser (author FK)
         │    └─ Who wrote it
         │
         ├──→ CustomUser (admin_decision_by FK)
         │    └─ Who made final decision
         │
         ├──→ Category (M2M)
         │    └─ Categories article belongs to
         │
         └──→ Review (1:M)
              └─ Reviews for this article
```

## Statistics Collection Flow

```
SystemStatsView.get_context_data()
  │
  ├─→ Article Statistics
  │    ├─ Count total articles
  │    ├─ Count by status (group by status)
  │    ├─ Count by category (annotate)
  │    └─ Sum total views
  │
  ├─→ User Statistics
  │    ├─ Count total users
  │    ├─ Count by role (group by role)
  │    └─ Count active users
  │
  └─→ Review Statistics
       ├─ Count total reviews
       ├─ Count by decision (group by decision)
       └─ Calculate averages

         │
         ↓
    Render to template
         │
         ↓
    Display dashboard
```

---

All diagrams show the complete flow of data through the admin panel system, from user interaction through database persistence and back to the user interface.
