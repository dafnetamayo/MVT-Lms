# Comandos para Resetear Docker Completamente

## Resetear Todo y Empezar desde Cero

Este proceso eliminará todos los contenedores, volúmenes y datos, y recreará todo desde cero.

### Paso 1: Detener y Eliminar Todo

```bash
# Detener y eliminar contenedores, redes y volúmenes
docker-compose down -v
```

El flag `-v` elimina los volúmenes, lo que borra toda la base de datos.

### Paso 2: Reconstruir y Iniciar Contenedores

```bash
# Reconstruir las imágenes y crear nuevos contenedores
docker-compose up -d --build
```

### Paso 3: Esperar a que los Servicios Estén Listos

Espera unos segundos para que PostgreSQL esté completamente iniciado:

```bash
# Verificar que los contenedores estén corriendo
docker-compose ps
```

### Paso 4: Ejecutar Migraciones

```bash
# Crear y aplicar todas las migraciones
docker-compose exec web python manage.py migrate
```

### Paso 5: Crear Usuario Administrador

```bash
# Crear superusuario (sigue las instrucciones)
docker-compose exec web python manage.py createsuperuser
```

### Paso 6: Ejecutar Seeder

```bash
# Poblar la base de datos con cursos de ejemplo
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags
```

## Comando Completo en una Línea (Script)

Puedes ejecutar todos los pasos en secuencia:

```bash
docker-compose down -v && \
docker-compose up -d --build && \
sleep 5 && \
docker-compose exec web python manage.py migrate && \
docker-compose exec web python manage.py createsuperuser && \
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags
```

**Nota**: El comando `sleep 5` da tiempo a PostgreSQL para iniciar completamente.

## Verificar que Todo Funciona

```bash
# Ver logs para verificar que no hay errores
docker-compose logs web

# Verificar estado de contenedores
docker-compose ps

# Acceder a la aplicación
# http://localhost:8500
```

## Solo Resetear Base de Datos (Mantener Contenedores)

Si solo quieres resetear la base de datos pero mantener los contenedores:

```bash
# Detener contenedores
docker-compose stop

# Eliminar solo el volumen de la base de datos
docker volume rm django_docker_postgres_data

# Iniciar contenedores de nuevo
docker-compose up -d

# Ejecutar migraciones
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar seeder
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags
```

## Limpiar Todo (Incluyendo Imágenes)

Si quieres una limpieza completa incluyendo las imágenes Docker:

```bash
# Detener y eliminar todo
docker-compose down -v

# Eliminar imágenes (opcional)
docker-compose rm -f

# Reconstruir desde cero
docker-compose up -d --build

# Esperar y ejecutar migraciones
sleep 5
docker-compose exec web python manage.py migrate

# Crear superusuario
docker-compose exec web python manage.py createsuperuser

# Ejecutar seeder
docker-compose exec web python manage.py seed_courses --count 50 --with-lessons --with-resources --with-announcements --with-tags
```

