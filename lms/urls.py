from django.urls import path, include
from . import views

# App URL patterns (site pages). The API router is mounted at project-level
urlpatterns = [
    path('', views.index, name='home'),
    path('registro/', views.registro, name='registro'),
    path('login/', views.iniciar_sesion, name='login'),
    path('logout/', views.cerrar_sesion, name='logout'),
    path('perfil/', views.perfil, name='perfil'),
    path('activate/<str:uidb64>/<str:token>/', views.activate_account, name='activate'),
    path('ajax/courses/', views.list_courses_ajax, name='list_courses_ajax'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/enroll/', views.enroll_course, name='enroll_course'),
    path('course/<int:course_id>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    path('my-courses/', views.my_courses, name='my_courses'),
    path('wishlist/', views.my_wishlist, name='wishlist'),
    path('resource/<int:resource_id>/download/', views.download_resource, name='download_resource'),
]
