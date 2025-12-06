from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class Profile(models.Model):
    """Extended user profile for LMS users"""
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(max_length=500, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    is_instructor = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.username})"

    class Meta:
        verbose_name = "Profile"
        verbose_name_plural = "Profiles"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Category(models.Model):
    """Course categories"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7, default='#007bff', help_text="Hex color code")
    icon = models.CharField(
        max_length=50, blank=True, help_text="Icon class name (e.g., 'fa-code')")
    is_active = models.BooleanField(default=True, help_text="Show category in listings")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']


class Tag(models.Model):
    """Tags for courses to improve searchability"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['name']


class Course(models.Model):
    """Course model"""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    LANGUAGE_CHOICES = [
        ('es', 'Spanish'),
        ('en', 'English'),
        ('fr', 'French'),
        ('de', 'German'),
        ('pt', 'Portuguese'),
        ('it', 'Italian'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True)
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='courses_taught')
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses')
    tags = models.ManyToManyField(
        'Tag', blank=True, related_name='courses', help_text="Tags for better searchability")
    difficulty = models.CharField(
        max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='draft')
    language = models.CharField(
        max_length=10, choices=LANGUAGE_CHOICES, default='es', help_text="Course language")
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    original_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Original price before discount")
    thumbnail = models.ImageField(
        upload_to='course_thumbnails/', null=True, blank=True)
    duration_hours = models.PositiveIntegerField(
        default=0, help_text="Total course duration in hours")
    max_students = models.PositiveIntegerField(
        null=True, blank=True, help_text="Maximum number of students (null = unlimited)")
    prerequisites = models.TextField(
        blank=True, help_text="Course prerequisites")
    learning_objectives = models.TextField(
        blank=True, help_text="What students will learn")
    is_featured = models.BooleanField(default=False)
    is_certificate_available = models.BooleanField(
        default=False, help_text="Certificate available upon completion")
    view_count = models.PositiveIntegerField(default=0, help_text="Number of times course was viewed")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'published' and not self.published_at:
            self.published_at = timezone.now()
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Get absolute URL for course detail page"""
        return reverse('course_detail', kwargs={'course_id': self.id})

    def get_discount_percentage(self):
        """Calculate discount percentage if original_price exists"""
        if self.original_price and self.original_price > self.price:
            return int(((self.original_price - self.price) / self.original_price) * 100)
        return 0

    def get_enrollment_count(self):
        """Get total number of active enrollments"""
        return self.enrollments.filter(status='active').count()

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Course"
        verbose_name_plural = "Courses"
        indexes = [
            models.Index(fields=['status', 'is_featured']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['-published_at']),
        ]


class Lesson(models.Model):
    """Lesson model for course content"""
    LESSON_TYPES = [
        ('video', 'Video'),
        ('text', 'Text'),
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('live', 'Live Session'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    lesson_type = models.CharField(
        max_length=20, choices=LESSON_TYPES, default='video')
    content = models.TextField(
        blank=True, help_text="Lesson content (text, video URL, etc.)")
    video_url = models.URLField(
        blank=True, help_text="Video URL for video lessons")
    duration_minutes = models.PositiveIntegerField(
        default=0, help_text="Lesson duration in minutes")
    order = models.PositiveIntegerField(
        default=0, help_text="Order within the course")
    is_published = models.BooleanField(default=True)
    is_free = models.BooleanField(
        default=False, help_text="Free lesson (accessible without enrollment)")
    attachments = models.FileField(
        upload_to='lesson_attachments/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'order']
        unique_together = ['course', 'order']
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"


class Enrollment(models.Model):
    """Student enrollment in courses (inscriptions)"""
    ENROLLMENT_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('suspended', 'Suspended'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(
        max_length=20, choices=ENROLLMENT_STATUS, default='active')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Course completion percentage"
    )
    last_accessed = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(
        blank=True, help_text="Instructor notes about this enrollment")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title}"

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        verbose_name = "Enrollment"
        verbose_name_plural = "Enrollments"


class LessonProgress(models.Model):
    """Track student progress through individual lessons"""
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name='progress')
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    time_spent_minutes = models.PositiveIntegerField(
        default=0, help_text="Time spent on this lesson")
    last_position = models.PositiveIntegerField(
        default=0, help_text="Last position in video (seconds)")
    notes = models.TextField(
        blank=True, help_text="Student notes for this lesson")

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.lesson.title}"

    class Meta:
        unique_together = ['student', 'lesson']
        verbose_name = "Lesson Progress"
        verbose_name_plural = "Lesson Progress"


class CourseReview(models.Model):
    """Student reviews for courses"""
    RATING_CHOICES = [
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    ]

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='course_reviews')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    is_anonymous = models.BooleanField(default=False)
    is_verified_purchase = models.BooleanField(
        default=False, help_text="Review from verified enrollment")
    helpful_count = models.PositiveIntegerField(
        default=0, help_text="Number of users who found this helpful")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.course.title} ({self.rating} stars)"

    class Meta:
        unique_together = ['student', 'course']
        ordering = ['-created_at', '-helpful_count']
        verbose_name = "Course Review"
        verbose_name_plural = "Course Reviews"
        indexes = [
            models.Index(fields=['course', '-rating']),
            models.Index(fields=['-created_at']),
        ]


class Certificate(models.Model):
    """Certificates issued to students upon course completion"""
    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='certificates')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='certificates')
    enrollment = models.OneToOneField(
        Enrollment, on_delete=models.CASCADE, related_name='certificate')
    certificate_number = models.CharField(
        max_length=50, unique=True, help_text="Unique certificate identifier")
    issued_at = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(
        upload_to='certificates/', null=True, blank=True,
        help_text="Generated PDF certificate file")
    verification_url = models.URLField(
        blank=True, help_text="URL to verify certificate authenticity")

    def __str__(self):
        return f"Certificate {self.certificate_number} - {self.student.get_full_name()} - {self.course.title}"

    def save(self, *args, **kwargs):
        if not self.certificate_number:
            # Generate unique certificate number
            import uuid
            self.certificate_number = f"CERT-{self.course.id}-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"
        ordering = ['-issued_at']
        indexes = [
            models.Index(fields=['certificate_number']),
            models.Index(fields=['student', '-issued_at']),
        ]


class CourseResource(models.Model):
    """Additional resources for courses (PDFs, files, links, etc.)"""
    RESOURCE_TYPES = [
        ('pdf', 'PDF Document'),
        ('video', 'Video File'),
        ('audio', 'Audio File'),
        ('link', 'External Link'),
        ('code', 'Code Repository'),
        ('other', 'Other'),
    ]

    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='resources')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    resource_type = models.CharField(
        max_length=20, choices=RESOURCE_TYPES, default='other')
    file = models.FileField(
        upload_to='course_resources/', null=True, blank=True,
        help_text="Upload file for this resource")
    external_url = models.URLField(
        blank=True, help_text="External URL if resource_type is 'link'")
    is_free = models.BooleanField(
        default=True, help_text="Available to all or only enrolled students")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    download_count = models.PositiveIntegerField(
        default=0, help_text="Number of times downloaded")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['course', 'order', 'title']
        verbose_name = "Course Resource"
        verbose_name_plural = "Course Resources"


class Wishlist(models.Model):
    """User wishlist for courses they want to take later"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='wishlist_items')
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='wishlist_users')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.course.title}"

    class Meta:
        unique_together = ['user', 'course']
        ordering = ['-added_at']
        verbose_name = "Wishlist Item"
        verbose_name_plural = "Wishlist Items"


class CourseAnnouncement(models.Model):
    """Announcements posted by instructors for their courses"""
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name='announcements')
    instructor = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='course_announcements')
    title = models.CharField(max_length=200)
    content = models.TextField()
    is_pinned = models.BooleanField(
        default=False, help_text="Pin announcement to top")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.course.title} - {self.title}"

    class Meta:
        ordering = ['-is_pinned', '-created_at']
        verbose_name = "Course Announcement"
        verbose_name_plural = "Course Announcements"
        indexes = [
            models.Index(fields=['course', '-is_pinned', '-created_at']),
        ]
