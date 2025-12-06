from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, FileResponse
from django.db.models import Avg
from .forms import RegistroForm

from .models import (
    Profile, Category, Tag, Course, Lesson, Enrollment,
    LessonProgress, CourseReview, Certificate, CourseResource,
    Wishlist, CourseAnnouncement
)
from .serializers import (
    UserSerializer, ProfileSerializer, CategorySerializer, CourseSerializer,
    LessonSerializer, EnrollmentSerializer, LessonProgressSerializer, CourseReviewSerializer
)


def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()
            messages.success(
                request, 'Registro exitoso, revisa tu correo para activar.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registro.html', {'form': form})


def iniciar_sesion(request):
    # Detect whether a Google SocialApp is configured for allauth so the
    # template can safely show/hide the provider login link.
    google_provider_enabled = False
    try:
        from allauth.socialaccount.models import SocialApp
        google_provider_enabled = SocialApp.objects.filter(
            provider='google').exists()
    except Exception:
        # allauth may not be available or DB may not have SocialApp entries.
        google_provider_enabled = False

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('perfil')
        else:
            messages.error(request, 'Credenciales incorrectas')
            # Redirect to home so the base template (which contains the login modal)
            # will render the messages and our JS will keep the modal open.
            return redirect('home')
    return render(request, 'usuarios/login.html', {'google_provider_enabled': google_provider_enabled})


@login_required
def perfil(request):
    return render(request, 'usuarios/perfil.html')


def cerrar_sesion(request):
    logout(request)
    return redirect('home')


def index(request):
    # Show up to 20 published courses on the home page
    courses = Course.objects.filter(
        status='published').order_by('-created_at')[:20]
    return render(request, 'index.html', {'courses': courses})


@login_required
def enroll_course(request, course_id):
    """Enroll the current user in a course"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Check if user is already enrolled
    enrollment, created = Enrollment.objects.get_or_create(
        student=request.user,
        course=course,
        defaults={'status': 'active'}
    )
    
    if created:
        messages.success(request, f'Te has inscrito exitosamente en {course.title}')
        return redirect('course_detail', course_id=course_id)
    else:
        messages.info(request, f'Ya estabas inscrito en {course.title}')
        return redirect('course_detail', course_id=course_id)


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined']
    ordering = ['username']


class ProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for Profile model"""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['is_instructor']
    search_fields = ['user__username', 'bio']
    ordering_fields = ['created_at']
    ordering = ['-created_at']


class CategoryViewSet(viewsets.ModelViewSet):
    """Categorias para los cursos ofrecidos"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    # Allow read-only access to anonymous users, but require authentication
    # for create/update/delete operations. We implement get_permissions so
    # it's explicit per-action and also guard destroy to ensure anonymous
    # delete attempts return 403.
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_permissions(self):
        # For write actions, require full authentication.
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            perms = [IsAuthenticated]
        else:
            perms = [IsAuthenticatedOrReadOnly]
        return [p() for p in perms]

    def destroy(self, request, *args, **kwargs):
        # Extra guard: explicitly forbid anonymous delete attempts with 403.
        if not request.user or not request.user.is_authenticated:
            from rest_framework.response import Response
            return Response(status=403)
        return super().destroy(request, *args, **kwargs)
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name']
    ordering = ['name']


class CourseViewSet(viewsets.ModelViewSet):
    """ViewSet for Course model"""
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['difficulty', 'status', 'category', 'instructor']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'created_at', 'price']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(instructor=self.request.user)


class LessonViewSet(viewsets.ModelViewSet):
    """ViewSet for Lesson model"""
    queryset = Lesson.objects.all()
    serializer_class = LessonSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'lesson_type', 'is_published']
    search_fields = ['title', 'description']
    ordering_fields = ['order', 'title', 'created_at']
    ordering = ['course', 'order']


class EnrollmentViewSet(viewsets.ModelViewSet):
    """ViewSet for Enrollment model"""
    queryset = Enrollment.objects.all()
    serializer_class = EnrollmentSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'course', 'student']
    search_fields = ['course__title']
    ordering_fields = ['enrolled_at']
    ordering = ['-enrolled_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class CourseReviewViewSet(viewsets.ModelViewSet):
    """ViewSet for CourseReview model"""
    queryset = CourseReview.objects.all()
    serializer_class = CourseReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['course', 'rating']
    search_fields = ['comment']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class LessonProgressViewSet(viewsets.ModelViewSet):
    """ViewSet for LessonProgress model"""
    queryset = LessonProgress.objects.all()
    serializer_class = LessonProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['student', 'lesson', 'is_completed']
    search_fields = ['lesson__title']
    ordering_fields = ['completed_at', 'created_at']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


def activate_account(request, uidb64, token):
    """Activate user account using token-based activation"""
    from django.contrib.auth.tokens import default_token_generator
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    
    if user is not None and default_token_generator.check_token(user, token):
        if user.is_active:
            messages.info(request, 'Tu cuenta ya está activa. Puedes iniciar sesión.')
        else:
            user.is_active = True
            user.save()
            messages.success(request, '¡Cuenta activada exitosamente! Ya puedes iniciar sesión.')
        return redirect('login')
    else:
        messages.error(request, 'El enlace de activación es inválido o ha expirado.')
        return redirect('registro')


def list_courses_ajax(request):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' and request.method == 'GET':
        courses = list(Course.objects.all().values(
            'id', 'title', 'description'))
        return JsonResponse({'courses': courses})
    return JsonResponse({'error': 'bad request'}, status=400)


def course_detail(request, course_id):
    """Display detailed information about a course"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # Increment view count
    course.view_count += 1
    course.save(update_fields=['view_count'])
    
    # Get lessons for this course
    lessons = course.lessons.filter(is_published=True).order_by('order')
    
    # Get course reviews
    reviews = course.reviews.all().order_by('-created_at', '-helpful_count')[:10]
    
    # Calculate average rating
    avg_rating = reviews.aggregate(
        avg=Avg('rating')
    )['avg'] or 0
    
    # Get course resources
    resources = course.resources.all().order_by('order', 'title')
    
    # Get course announcements
    announcements = course.announcements.all().order_by('-is_pinned', '-created_at')[:5]
    
    # Check if user is enrolled
    is_enrolled = False
    enrollment = None
    has_certificate = False
    certificate = None
    in_wishlist = False
    
    if request.user.is_authenticated:
        try:
            enrollment = Enrollment.objects.get(student=request.user, course=course)
            is_enrolled = enrollment.status == 'active'
            
            # Check for certificate
            if enrollment.status == 'completed':
                try:
                    certificate = Certificate.objects.get(enrollment=enrollment)
                    has_certificate = True
                except Certificate.DoesNotExist:
                    pass
        except Enrollment.DoesNotExist:
            pass
        
        # Check if course is in wishlist
        in_wishlist = Wishlist.objects.filter(user=request.user, course=course).exists()
    
    context = {
        'course': course,
        'lessons': lessons,
        'reviews': reviews,
        'resources': resources,
        'announcements': announcements,
        'avg_rating': round(avg_rating, 1) if avg_rating else 0,
        'is_enrolled': is_enrolled,
        'enrollment': enrollment,
        'has_certificate': has_certificate,
        'certificate': certificate,
        'in_wishlist': in_wishlist,
    }
    
    return render(request, 'courses/course_detail.html', context)


@login_required
def my_courses(request):
    """Display list of courses the user is enrolled in"""
    enrollments = Enrollment.objects.filter(
        student=request.user
    ).select_related('course', 'course__instructor', 'course__category').order_by('-enrolled_at')
    
    # Calculate stats
    total_courses = enrollments.count()
    active_courses = enrollments.filter(status='active').count()
    completed_courses = enrollments.filter(status='completed').count()
    
    context = {
        'enrollments': enrollments,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'completed_courses': completed_courses,
    }
    
    return render(request, 'courses/my_courses.html', context)


@login_required
def toggle_wishlist(request, course_id):
    """Add or remove course from wishlist"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        course=course
    )
    
    if created:
        messages.success(request, f'"{course.title}" agregado a tu lista de deseos')
    else:
        wishlist_item.delete()
        messages.info(request, f'"{course.title}" removido de tu lista de deseos')
    
    return redirect('course_detail', course_id=course_id)


@login_required
def my_wishlist(request):
    """Display user's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related('course', 'course__instructor', 'course__category').order_by('-added_at')
    
    context = {
        'wishlist_items': wishlist_items,
    }
    
    return render(request, 'courses/wishlist.html', context)


@login_required
def download_resource(request, resource_id):
    """Download a course resource"""
    resource = get_object_or_404(CourseResource, id=resource_id)
    
    # Check if user has access (enrolled or resource is free)
    has_access = False
    if resource.is_free:
        has_access = True
    elif request.user.is_authenticated:
        has_access = Enrollment.objects.filter(
            student=request.user,
            course=resource.course,
            status='active'
        ).exists()
    
    if not has_access:
        messages.error(request, 'No tienes acceso a este recurso')
        return redirect('course_detail', course_id=resource.course.id)
    
    if resource.file:
        # Increment download count
        resource.download_count += 1
        resource.save(update_fields=['download_count'])
        
        from django.http import FileResponse
        return FileResponse(resource.file.open(), as_attachment=True, filename=resource.file.name)
    elif resource.external_url:
        return redirect(resource.external_url)
    else:
        messages.error(request, 'Recurso no disponible')
        return redirect('course_detail', course_id=resource.course.id)
