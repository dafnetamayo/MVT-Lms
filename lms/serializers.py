from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Profile, Category, Tag, Course, Lesson, Enrollment,
    LessonProgress, CourseReview, Certificate, CourseResource,
    Wishlist, CourseAnnouncement
)


class UserSerializer(serializers.ModelSerializer):
    """Serializer for Django User model"""
    password = serializers.CharField(
        write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'is_active', 'date_joined', 'password']
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    class Meta:
        model = Profile
        fields = ['id', 'user', 'bio', 'birth_date', 'phone',
                  'avatar', 'is_instructor', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'icon', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'created_at']
        read_only_fields = ['id', 'created_at']


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model"""
    tags = TagSerializer(many=True, read_only=True)
    enrollment_count = serializers.SerializerMethodField()
    discount_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'instructor', 'category', 'tags', 'difficulty', 'status', 'language',
            'price', 'original_price', 'thumbnail', 'duration_hours', 'max_students',
            'prerequisites', 'learning_objectives', 'is_featured',
            'is_certificate_available', 'view_count', 'enrollment_count',
            'discount_percentage', 'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['id', 'view_count', 'created_at', 'updated_at', 'published_at']

    def get_enrollment_count(self, obj):
        return obj.get_enrollment_count()

    def get_discount_percentage(self, obj):
        return obj.get_discount_percentage()


class LessonSerializer(serializers.ModelSerializer):
    """Serializer for Lesson model"""

    class Meta:
        model = Lesson
        fields = [
            'id', 'course', 'title', 'description', 'lesson_type',
            'content', 'video_url', 'duration_minutes', 'order', 'is_published',
            'is_free', 'attachments', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnrollmentSerializer(serializers.ModelSerializer):
    """Serializer for Enrollment model"""

    class Meta:
        model = Enrollment
        fields = [
            'id', 'student', 'course', 'status', 'enrolled_at',
            'completed_at', 'progress_percentage', 'last_accessed', 'notes'
        ]
        read_only_fields = ['id', 'enrolled_at', 'completed_at']


class LessonProgressSerializer(serializers.ModelSerializer):
    """Serializer for LessonProgress model"""

    class Meta:
        model = LessonProgress
        fields = [
            'id', 'student', 'lesson', 'is_completed',
            'completed_at', 'time_spent_minutes', 'last_position', 'notes'
        ]
        read_only_fields = ['id']


class CourseReviewSerializer(serializers.ModelSerializer):
    """Serializer for CourseReview model"""

    class Meta:
        model = CourseReview
        fields = [
            'id', 'student', 'course', 'rating', 'comment',
            'is_anonymous', 'is_verified_purchase', 'helpful_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'helpful_count', 'created_at', 'updated_at']


class CertificateSerializer(serializers.ModelSerializer):
    """Serializer for Certificate model"""

    class Meta:
        model = Certificate
        fields = [
            'id', 'student', 'course', 'enrollment', 'certificate_number',
            'issued_at', 'pdf_file', 'verification_url'
        ]
        read_only_fields = ['id', 'certificate_number', 'issued_at']


class CourseResourceSerializer(serializers.ModelSerializer):
    """Serializer for CourseResource model"""

    class Meta:
        model = CourseResource
        fields = [
            'id', 'course', 'title', 'description', 'resource_type',
            'file', 'external_url', 'is_free', 'order', 'download_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'download_count', 'created_at', 'updated_at']


class WishlistSerializer(serializers.ModelSerializer):
    """Serializer for Wishlist model"""
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'course', 'added_at']
        read_only_fields = ['id', 'added_at']


class CourseAnnouncementSerializer(serializers.ModelSerializer):
    """Serializer for CourseAnnouncement model"""

    class Meta:
        model = CourseAnnouncement
        fields = [
            'id', 'course', 'instructor', 'title', 'content',
            'is_pinned', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
