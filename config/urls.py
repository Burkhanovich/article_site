"""
URL configuration for article publishing platform with multi-language support.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.generic import RedirectView

# Custom error handlers
handler403 = 'core.views.error_403'
handler404 = 'core.views.error_404'
handler500 = 'core.views.error_500'

# Non-i18n URLs (no language prefix needed)
urlpatterns = [
    # Language switching
    path('i18n/', include('django.conf.urls.i18n')),

    # CKEditor (no language prefix needed)
    path('ckeditor/', include('ckeditor_uploader.urls')),
]

# i18n URLs (with language prefix: /uz/, /ru/, /en/)
urlpatterns += i18n_patterns(
    # Admin
    path('admin/', admin.site.urls),

    # Apps
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('articles/', include('articles.urls')),

    # Redirect root to home (with language prefix)
    path('', RedirectView.as_view(pattern_name='core:home', permanent=False)),

    prefix_default_language=True,  # Include language prefix for default language too
)

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom admin site headers
admin.site.site_header = "Article Platform Administration"
admin.site.site_title = "Article Platform Admin"
admin.site.index_title = "Welcome to Article Platform Administration"
