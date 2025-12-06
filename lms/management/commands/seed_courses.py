"""
Django management command to seed the database with sample courses.
This command creates categories, instructors (if needed), and lots of courses with lessons.

Usage:
    python manage.py seed_courses
    python manage.py seed_courses --count 50
    python manage.py seed_courses --count 100 --with-lessons
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils import timezone
from decimal import Decimal
import random
from lms.models import (
    Category, Tag, Course, Lesson, CourseResource,
    CourseAnnouncement
)


class Command(BaseCommand):
    help = 'Seed the database with sample courses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Number of courses to create (default: 30)',
        )
        parser.add_argument(
            '--with-lessons',
            action='store_true',
            help='Create lessons for each course',
        )
        parser.add_argument(
            '--min-lessons',
            type=int,
            default=5,
            help='Minimum number of lessons per course (default: 5)',
        )
        parser.add_argument(
            '--max-lessons',
            type=int,
            default=15,
            help='Maximum number of lessons per course (default: 15)',
        )
        parser.add_argument(
            '--with-resources',
            action='store_true',
            help='Create resources for each course',
        )
        parser.add_argument(
            '--with-announcements',
            action='store_true',
            help='Create announcements for each course',
        )
        parser.add_argument(
            '--with-tags',
            action='store_true',
            help='Add tags to courses',
        )

    def handle(self, *args, **options):
        count = options['count']
        with_lessons = options['with_lessons']
        min_lessons = options['min_lessons']
        max_lessons = options['max_lessons']
        with_resources = options['with_resources']
        with_announcements = options['with_announcements']
        with_tags = options['with_tags']

        self.stdout.write(self.style.SUCCESS(f'Starting to seed {count} courses...'))

        # Create or get categories
        categories = self.create_categories()

        # Create or get tags
        tags = self.create_tags()

        # Get or create instructors
        instructors = self.get_or_create_instructors()

        # Course data templates
        course_templates = self.get_course_templates()

        created_count = 0
        for i in range(count):
            # Select random template or generate generic course
            if i < len(course_templates):
                template = course_templates[i]
            else:
                template = self.generate_random_course_template(i)

            # Create course
            course = self.create_course(
                template=template,
                categories=categories,
                instructors=instructors,
                tags=tags if with_tags else []
            )

            # Create lessons if requested
            if with_lessons:
                num_lessons = random.randint(min_lessons, max_lessons)
                self.create_lessons(course, num_lessons, template)

            # Create resources if requested
            if with_resources:
                num_resources = random.randint(2, 6)
                self.create_resources(course, num_resources)

            # Create announcements if requested
            if with_announcements:
                num_announcements = random.randint(1, 3)
                self.create_announcements(course, instructors, num_announcements)

            created_count += 1
            if created_count % 10 == 0:
                self.stdout.write(f'Created {created_count} courses...')

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully created {created_count} courses!'
            )
        )
        if with_lessons:
            self.stdout.write(
                self.style.SUCCESS('✅ Lessons were also created for each course!')
            )
        if with_resources:
            self.stdout.write(
                self.style.SUCCESS('✅ Resources were also created for each course!')
            )
        if with_announcements:
            self.stdout.write(
                self.style.SUCCESS('✅ Announcements were also created for each course!')
            )
        if with_tags:
            self.stdout.write(
                self.style.SUCCESS('✅ Tags were added to courses!')
            )

    def create_categories(self):
        """Create or get course categories"""
        categories_data = [
            {'name': 'Web Development', 'description': 'Learn to build modern web applications', 'color': '#007bff'},
            {'name': 'Data Science', 'description': 'Master data analysis and machine learning', 'color': '#28a745'},
            {'name': 'Mobile Development', 'description': 'Build iOS and Android apps', 'color': '#ffc107'},
            {'name': 'Programming', 'description': 'Learn programming languages and concepts', 'color': '#dc3545'},
            {'name': 'Design', 'description': 'UI/UX design and graphic design courses', 'color': '#6f42c1'},
            {'name': 'Business', 'description': 'Business and entrepreneurship courses', 'color': '#20c997'},
            {'name': 'Marketing', 'description': 'Digital marketing and SEO courses', 'color': '#fd7e14'},
            {'name': 'Photography', 'description': 'Learn photography techniques and editing', 'color': '#e83e8c'},
            {'name': 'Music', 'description': 'Music production and theory courses', 'color': '#17a2b8'},
            {'name': 'Language', 'description': 'Learn new languages', 'color': '#6610f2'},
            {'name': 'DevOps', 'description': 'Infrastructure and deployment courses', 'color': '#343a40'},
            {'name': 'Cybersecurity', 'description': 'Security and ethical hacking courses', 'color': '#f8f9fa'},
        ]

        categories = []
        for cat_data in categories_data:
            category, created = Category.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'color': cat_data['color']
                }
            )
            categories.append(category)
            if created:
                self.stdout.write(f'  Created category: {category.name}')

        return categories

    def create_tags(self):
        """Create or get course tags"""
        tags_data = [
            'Python', 'JavaScript', 'React', 'Django', 'Node.js', 'Vue.js',
            'Angular', 'TypeScript', 'HTML', 'CSS', 'Bootstrap', 'Tailwind',
            'SQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Docker', 'Kubernetes',
            'AWS', 'Azure', 'GCP', 'Linux', 'Git', 'GitHub', 'CI/CD',
            'Machine Learning', 'Deep Learning', 'Data Science', 'AI',
            'Web Development', 'Mobile Development', 'iOS', 'Android',
            'Flutter', 'React Native', 'Swift', 'Kotlin', 'Java', 'C++',
            'UI Design', 'UX Design', 'Figma', 'Adobe XD', 'Photoshop',
            'DevOps', 'Cybersecurity', 'Ethical Hacking', 'Blockchain',
            'GraphQL', 'REST API', 'Microservices', 'System Design',
            'Agile', 'Scrum', 'Project Management', 'Business',
            'Marketing', 'SEO', 'Content Writing', 'Photography',
            'Video Editing', 'Music Production', '3D Modeling', 'Animation',
        ]

        tags = []
        for tag_name in tags_data:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': slugify(tag_name)}
            )
            tags.append(tag)
            if created:
                self.stdout.write(f'  Created tag: {tag.name}')

        return tags

    def get_or_create_instructors(self):
        """Get existing users or create instructor users"""
        # Try to get existing users with instructor profiles
        instructors = list(User.objects.filter(profile__is_instructor=True))

        # If no instructors exist, create some or use existing users
        if not instructors:
            # Get any existing users
            existing_users = list(User.objects.all()[:5])
            if existing_users:
                instructors = existing_users
                # Mark them as instructors
                for user in instructors:
                    if hasattr(user, 'profile'):
                        user.profile.is_instructor = True
                        user.profile.save()
            else:
                # Create instructor users
                instructor_names = [
                    ('John', 'Smith', 'john.smith'),
                    ('Sarah', 'Johnson', 'sarah.johnson'),
                    ('Michael', 'Chen', 'michael.chen'),
                    ('Emily', 'Davis', 'emily.davis'),
                    ('David', 'Wilson', 'david.wilson'),
                    ('Lisa', 'Anderson', 'lisa.anderson'),
                    ('Robert', 'Martinez', 'robert.martinez'),
                    ('Jennifer', 'Taylor', 'jennifer.taylor'),
                ]

                for first_name, last_name, username in instructor_names:
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'first_name': first_name,
                            'last_name': last_name,
                            'email': f'{username}@example.com',
                            'is_active': True,
                        }
                    )
                    if created:
                        user.set_password('instructor123')
                        user.save()
                        if hasattr(user, 'profile'):
                            user.profile.is_instructor = True
                            user.profile.bio = f'Experienced instructor in {random.choice(["Web Development", "Data Science", "Design"])}'
                            user.profile.save()
                    instructors.append(user)

        return instructors

    def get_course_templates(self):
        """Get predefined course templates"""
        return [
            {
                'title': 'Complete Python Bootcamp: From Zero to Hero',
                'description': 'Master Python programming from basics to advanced topics. Learn data structures, OOP, web scraping, and more.',
                'short_description': 'Learn Python programming from scratch to advanced level',
                'difficulty': 'beginner',
                'price': 49.99,
                'duration_hours': 40,
                'prerequisites': 'No prior programming experience required',
                'learning_objectives': '• Master Python fundamentals\n• Build real-world projects\n• Understand OOP concepts\n• Work with APIs and databases',
            },
            {
                'title': 'React - The Complete Guide',
                'description': 'Dive deep into React.js. Learn hooks, context API, routing, and build modern web applications.',
                'short_description': 'Master React.js and build modern web applications',
                'difficulty': 'intermediate',
                'price': 59.99,
                'duration_hours': 50,
                'prerequisites': 'Basic knowledge of JavaScript and HTML',
                'learning_objectives': '• Master React hooks and components\n• Build single-page applications\n• Understand state management\n• Deploy React apps',
            },
            {
                'title': 'Machine Learning A-Z: Hands-On Python',
                'description': 'Learn machine learning algorithms and implement them in Python. From regression to deep learning.',
                'short_description': 'Complete machine learning course with Python',
                'difficulty': 'advanced',
                'price': 79.99,
                'duration_hours': 60,
                'prerequisites': 'Python programming and basic math knowledge',
                'learning_objectives': '• Understand ML algorithms\n• Implement models in Python\n• Work with real datasets\n• Deploy ML models',
            },
            {
                'title': 'Complete Web Development Bootcamp',
                'description': 'Full-stack web development course covering HTML, CSS, JavaScript, Node.js, and databases.',
                'short_description': 'Become a full-stack web developer',
                'difficulty': 'beginner',
                'price': 69.99,
                'duration_hours': 80,
                'prerequisites': 'No prior experience needed',
                'learning_objectives': '• Build responsive websites\n• Create backend APIs\n• Work with databases\n• Deploy applications',
            },
            {
                'title': 'iOS App Development with Swift',
                'description': 'Learn to build iOS applications using Swift and Xcode. Create beautiful, functional apps.',
                'short_description': 'Build iOS apps with Swift',
                'difficulty': 'intermediate',
                'price': 64.99,
                'duration_hours': 45,
                'prerequisites': 'Basic programming knowledge',
                'learning_objectives': '• Master Swift programming\n• Build iOS apps\n• Use Xcode effectively\n• Publish to App Store',
            },
            {
                'title': 'Advanced JavaScript: Patterns and Best Practices',
                'description': 'Deep dive into advanced JavaScript concepts, design patterns, and modern development practices.',
                'short_description': 'Master advanced JavaScript concepts',
                'difficulty': 'advanced',
                'price': 54.99,
                'duration_hours': 35,
                'prerequisites': 'Strong JavaScript fundamentals',
                'learning_objectives': '• Understand design patterns\n• Master async programming\n• Optimize performance\n• Write clean code',
            },
            {
                'title': 'Django for Beginners: Build Real-World Projects',
                'description': 'Learn Django framework by building real-world projects. Master models, views, templates, and deployment.',
                'short_description': 'Master Django web framework',
                'difficulty': 'beginner',
                'price': 49.99,
                'duration_hours': 30,
                'prerequisites': 'Python basics',
                'learning_objectives': '• Build Django applications\n• Work with databases\n• Create REST APIs\n• Deploy Django apps',
            },
            {
                'title': 'Data Science with Python and Pandas',
                'description': 'Learn data analysis, visualization, and manipulation using Python, Pandas, and NumPy.',
                'short_description': 'Master data science with Python',
                'difficulty': 'intermediate',
                'price': 59.99,
                'duration_hours': 40,
                'prerequisites': 'Python basics',
                'learning_objectives': '• Analyze datasets\n• Create visualizations\n• Clean and transform data\n• Build data pipelines',
            },
            {
                'title': 'UI/UX Design Masterclass',
                'description': 'Learn user interface and user experience design principles. Create beautiful, functional designs.',
                'short_description': 'Master UI/UX design principles',
                'difficulty': 'beginner',
                'price': 44.99,
                'duration_hours': 25,
                'prerequisites': 'No prior experience needed',
                'learning_objectives': '• Design user interfaces\n• Understand UX principles\n• Use design tools\n• Create prototypes',
            },
            {
                'title': 'Docker and Kubernetes: Complete Guide',
                'description': 'Master containerization with Docker and orchestration with Kubernetes. Deploy scalable applications.',
                'short_description': 'Learn Docker and Kubernetes',
                'difficulty': 'intermediate',
                'price': 69.99,
                'duration_hours': 35,
                'prerequisites': 'Basic Linux and command line knowledge',
                'learning_objectives': '• Containerize applications\n• Use Docker effectively\n• Deploy with Kubernetes\n• Scale applications',
            },
        ]

    def generate_random_course_template(self, index):
        """Generate a random course template"""
        topics = [
            'JavaScript', 'Python', 'React', 'Node.js', 'Vue.js', 'Angular',
            'Django', 'Flask', 'Spring Boot', 'Laravel', 'Ruby on Rails',
            'Swift', 'Kotlin', 'Go', 'Rust', 'C++', 'Java', 'C#',
            'Machine Learning', 'Deep Learning', 'Data Science', 'AI',
            'Blockchain', 'Cryptocurrency', 'Web3', 'Solidity',
            'DevOps', 'AWS', 'Azure', 'GCP', 'Linux', 'Docker',
            'GraphQL', 'REST API', 'Microservices', 'System Design',
            'Cybersecurity', 'Ethical Hacking', 'Penetration Testing',
            'Mobile Development', 'Flutter', 'React Native',
            'UI Design', 'UX Design', 'Figma', 'Adobe XD',
            'Photography', 'Video Editing', '3D Modeling', 'Animation',
        ]

        adjectives = [
            'Complete', 'Advanced', 'Master', 'Ultimate', 'Comprehensive',
            'Professional', 'Expert', 'Beginner', 'Intermediate', 'Practical',
            'Hands-On', 'Real-World', 'Modern', 'Essential', 'Fundamental',
        ]

        topic = random.choice(topics)
        adjective = random.choice(adjectives)
        title = f'{adjective} {topic} Course'

        difficulties = ['beginner', 'intermediate', 'advanced']
        difficulty = random.choice(difficulties)

        prices = [0, 19.99, 29.99, 39.99, 49.99, 59.99, 69.99, 79.99]
        price = random.choice(prices)

        duration = random.randint(10, 100)

        return {
            'title': title,
            'description': f'Learn {topic} from scratch. This comprehensive course covers all essential topics and best practices. Perfect for {difficulty} level students.',
            'short_description': f'Master {topic} with this comprehensive course',
            'difficulty': difficulty,
            'price': Decimal(str(price)),
            'duration_hours': duration,
            'prerequisites': 'Basic knowledge recommended' if difficulty != 'beginner' else 'No prior experience required',
            'learning_objectives': f'• Understand {topic} fundamentals\n• Build practical projects\n• Apply best practices\n• Master advanced concepts',
        }

    def create_course(self, template, categories, instructors, tags):
        """Create a course from template"""
        # Generate unique slug
        base_slug = slugify(template['title'])
        slug = base_slug
        counter = 1
        while Course.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        # Determine price and original price (for discounts)
        # Ensure price is always a Decimal - convert from template
        template_price = template.get('price', None)
        if template_price is None:
            price = Decimal(str(random.choice([0, 19.99, 29.99, 39.99, 49.99, 59.99, 69.99, 79.99])))
        else:
            # Convert to Decimal if it's not already (templates have float prices)
            if isinstance(template_price, Decimal):
                price = template_price
            elif isinstance(template_price, (int, float)):
                price = Decimal(str(template_price))
            else:
                price = Decimal(str(template_price))
        
        original_price = None
        if price > 0 and random.choice([True, False, False]):  # 33% chance of discount
            discount_percentage = random.choice([10, 15, 20, 25, 30, 40, 50])
            # Use Decimal for all calculations
            discount_decimal = Decimal(str(discount_percentage)) / Decimal('100')
            original_price = price / (Decimal('1') - discount_decimal)
            original_price = original_price.quantize(Decimal('0.01'))

        # Language selection
        languages = ['es', 'en', 'fr', 'de', 'pt', 'it']
        language = random.choice(languages)

        course = Course.objects.create(
            title=template['title'],
            slug=slug,
            description=template['description'],
            short_description=template.get('short_description', template['description'][:300]),
            instructor=random.choice(instructors),
            category=random.choice(categories),
            difficulty=template['difficulty'],
            status='published',
            language=language,
            price=price,
            original_price=original_price,
            duration_hours=template.get('duration_hours', random.randint(10, 80)),
            max_students=random.choice([None, 50, 100, 200, 500]),
            prerequisites=template.get('prerequisites', ''),
            learning_objectives=template.get('learning_objectives', ''),
            is_featured=random.choice([True, False, False, False]),  # 25% chance
            is_certificate_available=random.choice([True, False, False]),  # 33% chance
            view_count=random.randint(0, 1000),  # Random view count
            published_at=timezone.now(),
        )

        # Add tags if provided
        if tags:
            num_tags = random.randint(2, 5)
            selected_tags = random.sample(tags, min(num_tags, len(tags)))
            course.tags.set(selected_tags)

        return course

    def create_lessons(self, course, num_lessons, template):
        """Create lessons for a course"""
        lesson_types = ['video', 'text', 'quiz', 'assignment']
        lesson_titles = [
            'Introduction', 'Getting Started', 'Setup and Installation',
            'Basic Concepts', 'Core Fundamentals', 'Advanced Topics',
            'Practical Examples', 'Real-World Projects', 'Best Practices',
            'Common Pitfalls', 'Tips and Tricks', 'Next Steps',
            'Overview', 'Deep Dive', 'Hands-On Practice',
            'Theory and Concepts', 'Implementation', 'Testing',
            'Deployment', 'Optimization', 'Troubleshooting',
        ]

        # Generate course-specific lesson titles
        topic = template.get('title', 'Course').split()[0] if template.get('title') else 'Topic'
        custom_lessons = [
            f'{topic} Basics',
            f'{topic} Fundamentals',
            f'Advanced {topic}',
            f'{topic} Best Practices',
            f'{topic} Projects',
        ]

        all_lessons = lesson_titles + custom_lessons

        for i in range(num_lessons):
            # Select lesson title
            if i < len(all_lessons):
                title = f"{all_lessons[i]} - Part {i+1}"
            else:
                title = f"Lesson {i+1}: {random.choice(['Introduction', 'Deep Dive', 'Practice', 'Project'])}"

            lesson_type = random.choice(lesson_types)
            duration = random.randint(5, 60)  # 5 to 60 minutes

            Lesson.objects.create(
                course=course,
                title=title,
                description=f'In this lesson, you will learn about {title.lower()}. This is an essential part of the course.',
                lesson_type=lesson_type,
                content=f'This is the content for {title}. Learn and practice the concepts covered in this lesson.',
                video_url=f'https://example.com/video/{course.slug}-lesson-{i+1}' if lesson_type == 'video' else '',
                duration_minutes=duration,
                order=i + 1,
                is_published=True,
                is_free=random.choice([True, False, False, False]),  # 25% chance
            )

    def create_resources(self, course, num_resources):
        """Create resources for a course"""
        resource_types = ['pdf', 'video', 'link', 'code', 'other']
        resource_titles = [
            'Course Materials PDF',
            'Additional Reading',
            'Code Repository',
            'Video Tutorial',
            'Practice Exercises',
            'Cheat Sheet',
            'Project Files',
            'Reference Documentation',
            'External Resources',
            'Bonus Content',
        ]

        for i in range(num_resources):
            resource_type = random.choice(resource_types)
            title = random.choice(resource_titles) if i < len(resource_titles) else f'Resource {i+1}'
            
            # Determine if resource has file or external URL
            has_file = resource_type in ['pdf', 'video', 'other'] and random.choice([True, False])
            has_url = resource_type == 'link' or (not has_file and random.choice([True, False]))

            CourseResource.objects.create(
                course=course,
                title=title,
                description=f'Additional {resource_type} resource for {course.title}. This will help you deepen your understanding.',
                resource_type=resource_type,
                external_url=f'https://example.com/resource/{course.slug}-{i+1}' if has_url else '',
                is_free=random.choice([True, False, False]),  # 33% chance of free
                order=i + 1,
                download_count=random.randint(0, 100) if has_file else 0,
            )

    def create_announcements(self, course, instructors, num_announcements):
        """Create announcements for a course"""
        announcement_templates = [
            {
                'title': 'Bienvenida al Curso',
                'content': f'¡Bienvenidos a {course.title}! Estoy emocionado de tenerlos aquí. Este curso está diseñado para ayudarlos a dominar los conceptos fundamentales.',
            },
            {
                'title': 'Nuevo Contenido Disponible',
                'content': 'He agregado nuevas lecciones al curso. Asegúrense de revisar el contenido actualizado y completar los ejercicios prácticos.',
            },
            {
                'title': 'Recordatorio Importante',
                'content': 'Recuerden que tienen acceso de por vida a este curso. Tómense su tiempo para practicar y no duden en hacer preguntas en los comentarios.',
            },
            {
                'title': 'Proyecto Final Disponible',
                'content': 'El proyecto final del curso ya está disponible. Este proyecto les permitirá aplicar todos los conceptos aprendidos. ¡Buena suerte!',
            },
            {
                'title': 'Actualización del Curso',
                'content': 'He actualizado algunas lecciones con contenido más reciente y mejores ejemplos. Revisen las lecciones actualizadas cuando tengan tiempo.',
            },
        ]

        instructor = course.instructor

        for i in range(num_announcements):
            if i < len(announcement_templates):
                template = announcement_templates[i]
            else:
                template = {
                    'title': f'Anuncio {i+1}',
                    'content': f'Información importante sobre {course.title}. Manténganse al día con las últimas actualizaciones.',
                }

            CourseAnnouncement.objects.create(
                course=course,
                instructor=instructor,
                title=template['title'],
                content=template['content'],
                is_pinned=(i == 0),  # First announcement is pinned
            )

