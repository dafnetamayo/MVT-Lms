from django.contrib import admin
from django.urls import include, path, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from lms import views as lms_views
from rest_framework.routers import DefaultRouter

# API router (register lms viewsets here so API lives under /api/lms/)
api_router = DefaultRouter()
api_router.register(r'users', lms_views.UserViewSet)
api_router.register(r'profiles', lms_views.ProfileViewSet)
api_router.register(r'categories', lms_views.CategoryViewSet)
api_router.register(r'courses', lms_views.CourseViewSet)
api_router.register(r'lessons', lms_views.LessonViewSet)
api_router.register(r'enrollments', lms_views.EnrollmentViewSet)
api_router.register(r'reviews', lms_views.CourseReviewViewSet)
api_router.register(r'lesson-progress', lms_views.LessonProgressViewSet)

schema_view = get_schema_view(
    openapi.Info(
        title="LMS API Documentation",
        default_version='v1',
        description="A comprehensive Learning Management System API built with Django REST Framework. "
        "Supports multi-role users (instructors and students) with full CRUD operations "
        "for courses, lessons, enrollments, and more.",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="admin@lms.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('', include('lms.urls')),
    path('admin/', admin.site.urls),
    path('api/lms/', include((api_router.urls, 'lms'), namespace='lms-api')),
    # DRF browsable API login
    path('api-auth/', include('rest_framework.urls')),
    # Swagger documentation
    re_path(r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger',
         cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc',
         cache_timeout=0), name='schema-redoc'),
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
# In production (Railway), media files are served from the volume via WhiteNoise or nginx
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
