# Sistema de Gestión de Aprendizaje (LMS)

Sistema de gestión de aprendizaje desarrollado con Django y Django REST Framework. Permite la gestión completa de cursos, estudiantes, instructores, inscripciones y seguimiento de progreso.

## Características Principales

- Autenticación OAuth2 con Google
- Gestión completa de cursos y categorías
- Sistema de inscripciones y seguimiento de progreso
- Sistema de reseñas y calificaciones
- Certificados de finalización
- Recursos adicionales para cursos
- Lista de deseos
- Anuncios de instructores
- Sistema de etiquetas (tags) para búsqueda mejorada
- API REST completa con documentación Swagger

## Requisitos Previos

- Docker y Docker Compose instalados
- Git
- Cuenta de Google Cloud (opcional, para OAuth2)

## Instalación y Configuración

### 1. Clonar el Repositorio

```bash
git clone <url-del-repositorio>
cd django_docker
```

### 2. Crear Archivo de Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con el siguiente contenido:

```env
# Configuración de Django
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos (Docker Compose usará estos valores)
DATABASE_NAME=mydatabase
DATABASE_USER=user
DATABASE_PASSWORD=password
DATABASE_HOST=db
DATABASE_PORT=5432

# Configuración del Sitio
SITE_URL=http://localhost:8500
SITE_ID=1

# Configuración de Email (para desarrollo, usar consola)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-aplicacion
DEFAULT_FROM_EMAIL=tu-email@gmail.com

# Swagger
SWAGGER_SCHEMA_URL=http://localhost:8500
```

**Generar una Clave Secreta:**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia la salida y reemplaza `tu-clave-secreta-aqui` en el archivo `.env`.

### 3. Construir y Iniciar Contenedores Docker

```bash
docker-compose up -d --build
```

Este comando construirá las imágenes Docker e iniciará los servicios:
- Base de datos PostgreSQL
- Aplicación Django

### 4. Ejecutar Migraciones

```bash
docker-compose exec web python manage.py migrate
```

Este comando aplicará todas las migraciones necesarias para crear las tablas en la base de datos.

### 5. Crear Usuario Administrador

```bash
docker-compose exec web python manage.py createsuperuser
```

Sigue las instrucciones para crear un usuario administrador.

### 6. Poblar la Base de Datos con Datos de Prueba (Opcional)

El proyecto incluye un comando de seeder para generar cursos de ejemplo:

```bash
# Crear 30 cursos con lecciones (configuración básica)
docker-compose exec web python manage.py seed_courses --with-lessons

# Crear 50 cursos con todas las características
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags

# Crear 100 cursos con configuración personalizada
docker-compose exec web python manage.py seed_courses --count 100 --with-lessons --min-lessons 8 --max-lessons 20 --with-resources --with-announcements --with-tags
```

**Opciones del Seeder:**

- `--count`: Número de cursos a crear (por defecto: 30)
- `--with-lessons`: Crear lecciones para cada curso
- `--min-lessons`: Número mínimo de lecciones por curso (por defecto: 5)
- `--max-lessons`: Número máximo de lecciones por curso (por defecto: 15)
- `--with-resources`: Crear recursos adicionales para cada curso
- `--with-announcements`: Crear anuncios para cada curso
- `--with-tags`: Agregar etiquetas a los cursos

### 7. Acceder a la Aplicación

Una vez que los contenedores estén en ejecución:

- **Aplicación Web**: http://localhost:8500
- **Panel de Administración**: http://localhost:8500/admin
- **Documentación API (Swagger)**: http://localhost:8500/swagger/
- **Documentación API (ReDoc)**: http://localhost:8500/redoc/

## Comandos Útiles

### Gestión de Contenedores

```bash
# Iniciar servicios
docker-compose up -d

# Detener servicios
docker-compose down

# Ver logs
docker-compose logs -f web

# Reiniciar servicios
docker-compose restart

# Reconstruir contenedores
docker-compose up -d --build
```

### Comandos Django

```bash
# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear migraciones (después de cambios en modelos)
docker-compose exec web python manage.py makemigrations

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput

# Acceder a la shell de Django
docker-compose exec web python manage.py shell

# Ejecutar el seeder de cursos
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags
```

## Estructura del Proyecto

```
django_docker/
├── lms/                    # Aplicación principal
│   ├── models.py          # Modelos de base de datos
│   ├── views.py           # Vistas y ViewSets
│   ├── urls.py            # Rutas de la aplicación
│   ├── serializers.py     # Serializadores para la API
│   ├── admin.py           # Configuración del admin
│   ├── forms.py           # Formularios
│   ├── signals.py         # Señales de Django
│   ├── templates/         # Plantillas HTML
│   ├── management/        # Comandos de gestión
│   │   └── commands/
│   │       └── seed_courses.py
│   └── migrations/        # Migraciones de base de datos
├── project/               # Configuración del proyecto Django
│   ├── settings.py        # Configuración
│   └── urls.py            # URLs principales
├── docker-compose.yaml     # Configuración de Docker Compose
├── Dockerfile             # Imagen Docker para desarrollo
├── requirements.txt       # Dependencias Python
└── .env                   # Variables de entorno (crear manualmente)
```

## Modelos de Base de Datos

### Esquema de Modelos

#### Profile
Extiende el modelo de usuario de Django con información adicional.

```
Profile
├── user (OneToOne -> User)
├── bio (TextField)
├── birth_date (DateField, nullable)
├── phone (CharField)
├── avatar (ImageField, nullable)
├── is_instructor (BooleanField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

#### Category
Categorías para organizar los cursos.

```
Category
├── name (CharField, unique)
├── description (TextField)
├── color (CharField) - Código hexadecimal de color
├── icon (CharField) - Nombre de clase de icono
├── is_active (BooleanField) - Mostrar/ocultar en listados
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

#### Tag
Etiquetas para mejorar la búsqueda y categorización de cursos.

```
Tag
├── name (CharField, unique)
├── slug (SlugField, unique)
└── created_at (DateTimeField)
```

#### Course
Modelo principal para los cursos.

```
Course
├── title (CharField)
├── slug (SlugField, unique)
├── description (TextField)
├── short_description (CharField)
├── instructor (ForeignKey -> User)
├── category (ForeignKey -> Category, nullable)
├── tags (ManyToMany -> Tag)
├── difficulty (CharField) - beginner/intermediate/advanced
├── status (CharField) - draft/published/archived
├── language (CharField) - es/en/fr/de/pt/it
├── price (DecimalField)
├── original_price (DecimalField, nullable) - Para cálculos de descuento
├── thumbnail (ImageField, nullable)
├── duration_hours (PositiveIntegerField)
├── max_students (PositiveIntegerField, nullable)
├── prerequisites (TextField)
├── learning_objectives (TextField)
├── is_featured (BooleanField)
├── is_certificate_available (BooleanField)
├── view_count (PositiveIntegerField)
├── created_at (DateTimeField)
├── updated_at (DateTimeField)
└── published_at (DateTimeField, nullable)
```

#### Lesson
Lecciones dentro de un curso.

```
Lesson
├── course (ForeignKey -> Course)
├── title (CharField)
├── description (TextField)
├── lesson_type (CharField) - video/text/quiz/assignment/live
├── content (TextField)
├── video_url (URLField)
├── duration_minutes (PositiveIntegerField)
├── order (PositiveIntegerField)
├── is_published (BooleanField)
├── is_free (BooleanField)
├── attachments (FileField, nullable)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

#### Enrollment
Inscripciones de estudiantes en cursos.

```
Enrollment
├── student (ForeignKey -> User)
├── course (ForeignKey -> Course)
├── status (CharField) - active/completed/dropped/suspended
├── enrolled_at (DateTimeField)
├── completed_at (DateTimeField, nullable)
├── progress_percentage (PositiveIntegerField) - 0-100
├── last_accessed (DateTimeField, nullable)
└── notes (TextField)
```

#### LessonProgress
Seguimiento del progreso de estudiantes en lecciones individuales.

```
LessonProgress
├── student (ForeignKey -> User)
├── lesson (ForeignKey -> Lesson)
├── is_completed (BooleanField)
├── completed_at (DateTimeField, nullable)
├── time_spent_minutes (PositiveIntegerField)
├── last_position (PositiveIntegerField) - Para videos
└── notes (TextField)
```

#### CourseReview
Reseñas y calificaciones de estudiantes para cursos.

```
CourseReview
├── student (ForeignKey -> User)
├── course (ForeignKey -> Course)
├── rating (PositiveIntegerField) - 1-5 estrellas
├── comment (TextField)
├── is_anonymous (BooleanField)
├── is_verified_purchase (BooleanField)
├── helpful_count (PositiveIntegerField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

#### Certificate
Certificados emitidos a estudiantes al completar cursos.

```
Certificate
├── student (ForeignKey -> User)
├── course (ForeignKey -> Course)
├── enrollment (OneToOne -> Enrollment)
├── certificate_number (CharField, unique) - Generado automáticamente
├── issued_at (DateTimeField)
├── pdf_file (FileField, nullable)
└── verification_url (URLField)
```

#### CourseResource
Recursos adicionales para cursos (PDFs, archivos, enlaces, etc.).

```
CourseResource
├── course (ForeignKey -> Course)
├── title (CharField)
├── description (TextField)
├── resource_type (CharField) - pdf/video/audio/link/code/other
├── file (FileField, nullable)
├── external_url (URLField)
├── is_free (BooleanField) - Disponible para todos o solo inscritos
├── order (PositiveIntegerField)
├── download_count (PositiveIntegerField)
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

#### Wishlist
Lista de deseos de usuarios para cursos que quieren tomar más tarde.

```
Wishlist
├── user (ForeignKey -> User)
├── course (ForeignKey -> Course)
└── added_at (DateTimeField)
```

#### CourseAnnouncement
Anuncios publicados por instructores para sus cursos.

```
CourseAnnouncement
├── course (ForeignKey -> Course)
├── instructor (ForeignKey -> User)
├── title (CharField)
├── content (TextField)
├── is_pinned (BooleanField) - Fijar anuncio al inicio
├── created_at (DateTimeField)
└── updated_at (DateTimeField)
```

## Configuración de OAuth2 con Google

### 1. Crear Credenciales de Google OAuth

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **API de Google+**:
   - Ve a "APIs & Services" → "Library"
   - Busca "Google+ API"
   - Haz clic en "Enable"
4. Crea Credenciales OAuth 2.0:
   - Ve a "APIs & Services" → "Credentials"
   - Haz clic en "Create Credentials" → "OAuth client ID"
   - Elige "Web application"
   - Agrega URIs de redirección autorizadas:
     - `http://localhost:8500/accounts/google/login/callback/` (desarrollo)
     - `https://tudominio.com/accounts/google/login/callback/` (producción)
   - Haz clic en "Create"
   - **Guarda el Client ID y Client Secret**

### 2. Configurar Sitio en Django Admin

1. Accede al panel de administración: http://localhost:8500/admin
2. Ve a **Sites** → **Sites**
3. Edita el sitio por defecto:
   - **Domain name**: `localhost:8500` (o tu dominio)
   - **Display name**: `LMS Site`
4. Guarda

### 3. Agregar Aplicación Social de Google

1. En Django admin, ve a **Social applications** → **Social applications**
2. Haz clic en **Add social application**
3. Completa:
   - **Provider**: `Google`
   - **Name**: `Google OAuth`
   - **Client id**: Tu Google Client ID
   - **Secret key**: Tu Google Client Secret
   - **Sites**: Selecciona tu sitio y muévelo a "Chosen sites"
4. Haz clic en **Save**

## Configuración de Email

### Desarrollo (Consola)

Para desarrollo, los emails se imprimirán en la consola:

```env
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### Producción (Gmail SMTP)

1. **Habilita la Autenticación de 2 Factores** en tu cuenta de Gmail
2. **Genera una Contraseña de Aplicación**:
   - Ve a Cuenta de Google → Seguridad
   - En "Verificación en 2 pasos", haz clic en "Contraseñas de aplicaciones"
   - Genera una nueva contraseña de aplicación para "Correo"
   - Copia la contraseña de 16 caracteres

3. Actualiza `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-contraseña-de-16-caracteres
DEFAULT_FROM_EMAIL=tu-email@gmail.com
```

## Solución de Problemas

### Error de Conexión a la Base de Datos

**Error: "could not connect to server"**

- Verifica que el contenedor de la base de datos esté en ejecución: `docker-compose ps`
- Reinicia los servicios: `docker-compose restart`

### Problemas con Migraciones

**Error: "No such table"**

```bash
# Recrear base de datos (ADVERTENCIA: Esto elimina datos)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### OAuth2 No Funciona

**El botón de login de Google no aparece:**
- Verifica que SocialApp esté configurado en el admin
- Verifica que el sitio esté configurado correctamente
- Revisa la consola del navegador para errores

**Error de URI de redirección:**
- Asegúrate de que la URI de redirección en Google Console coincida exactamente: `http://localhost:8500/accounts/google/login/callback/`
- Verifica que SITE_URL en settings coincida con tu dominio

### Archivos Estáticos No Se Cargan

```bash
# Recolectar archivos estáticos
docker-compose exec web python manage.py collectstatic --noinput
```

## API REST

El proyecto incluye una API REST completa documentada con Swagger. Accede a la documentación en:

- **Swagger UI**: http://localhost:8500/swagger/
- **ReDoc**: http://localhost:8500/redoc/

### Endpoints Principales

- `/api/lms/users/` - Gestión de usuarios
- `/api/lms/profiles/` - Perfiles de usuario
- `/api/lms/categories/` - Categorías
- `/api/lms/courses/` - Cursos
- `/api/lms/lessons/` - Lecciones
- `/api/lms/enrollments/` - Inscripciones
- `/api/lms/reviews/` - Reseñas
- `/api/lms/lesson-progress/` - Progreso de lecciones

## Desarrollo

### Estructura de Características Implementadas

- **Autenticación OAuth2**: Login con Google completamente funcional
- **Página de Detalles de Curso**: Vista completa con toda la información del curso
- **Listado de Cursos Inscritos**: Página para ver todos los cursos en los que el usuario está inscrito
- **Sistema de Email y Activación**: Envío de emails de bienvenida y activación con tokens seguros
- **Sistema de Etiquetas**: Etiquetas para mejorar la búsqueda
- **Recursos de Curso**: Archivos y enlaces adicionales
- **Anuncios**: Anuncios de instructores para cursos
- **Lista de Deseos**: Guardar cursos para más tarde
- **Certificados**: Sistema de certificados de finalización

## Licencia

Este proyecto está bajo la Licencia MIT.

## Revisar los LOGS
`docker-compose logs web`
