from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from .models import (
    Profile, Category, Tag, Course, Lesson, Enrollment,
    LessonProgress, CourseReview, Certificate, CourseResource,
    Wishlist, CourseAnnouncement
)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_instructor', 'created_at']
    list_filter = ['is_instructor', 'created_at']
    search_fields = ['user__username', 'user__email', 'bio']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    
    def color_display(self, obj):
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color, obj.color
        )
    color_display.short_description = 'Color'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'category', 'status', 'price', 'is_featured', 'view_count', 'published_at']
    list_filter = ['status', 'difficulty', 'category', 'is_featured', 'language', 'created_at']
    search_fields = ['title', 'description', 'instructor__username']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'published_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'short_description', 'instructor', 'category', 'tags')
        }),
        ('Course Details', {
            'fields': ('difficulty', 'language', 'status', 'duration_hours', 'max_students')
        }),
        ('Pricing', {
            'fields': ('price', 'original_price')
        }),
        ('Content', {
            'fields': ('thumbnail', 'prerequisites', 'learning_objectives')
        }),
        ('Settings', {
            'fields': ('is_featured', 'is_certificate_available')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at', 'published_at')
        }),
    )


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'lesson_type', 'order', 'is_published', 'is_free', 'duration_minutes']
    list_filter = ['lesson_type', 'is_published', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    ordering = ['course', 'order']


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'progress_percentage', 'enrolled_at', 'last_accessed']
    list_filter = ['status', 'enrolled_at', 'completed_at']
    search_fields = ['student__username', 'course__title']
    readonly_fields = ['enrolled_at', 'completed_at']


@admin.register(LessonProgress)
class LessonProgressAdmin(admin.ModelAdmin):
    list_display = ['student', 'lesson', 'is_completed', 'time_spent_minutes', 'completed_at']
    list_filter = ['is_completed', 'completed_at']
    search_fields = ['student__username', 'lesson__title']


@admin.register(CourseReview)
class CourseReviewAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rating', 'is_verified_purchase', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_anonymous', 'is_verified_purchase', 'created_at']
    search_fields = ['student__username', 'course__title', 'comment']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['certificate_number', 'student', 'course', 'issued_at']
    list_filter = ['issued_at']
    search_fields = ['certificate_number', 'student__username', 'course__title']
    readonly_fields = ['certificate_number', 'issued_at']


@admin.register(CourseResource)
class CourseResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'resource_type', 'is_free', 'download_count', 'order']
    list_filter = ['resource_type', 'is_free', 'created_at']
    search_fields = ['title', 'description', 'course__title']
    ordering = ['course', 'order']


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'added_at']
    list_filter = ['added_at']
    search_fields = ['user__username', 'course__title']


@admin.register(CourseAnnouncement)
class CourseAnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'instructor', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'created_at']
    search_fields = ['title', 'content', 'course__title']
    readonly_fields = ['created_at', 'updated_at']
