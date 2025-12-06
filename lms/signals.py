from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.urls import reverse
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string


@receiver(post_save, sender=User)
def send_activation_email(sender, instance, created, **kwargs):
    """Send activation email when a new user is created (only for regular registration, not OAuth)"""
    if created and not instance.is_active:
        # Generate activation token
        token = default_token_generator.make_token(instance)
        uid = urlsafe_base64_encode(force_bytes(instance.pk))
        
        # Build activation URL
        site_url = getattr(settings, 'SITE_URL', 'http://localhost:8500')
        activation_link = f"{site_url}/activate/{uid}/{token}/"
        
        # Email subject and message
        subject = "Bienvenido - Activa tu cuenta"
        
        # Create email message with HTML support
        message = f"""
Hola {instance.get_full_name() or instance.username},

¡Bienvenido a nuestra plataforma de aprendizaje!

Para activar tu cuenta y comenzar a disfrutar de nuestros cursos, por favor haz clic en el siguiente enlace:

{activation_link}

Este enlace expirará en 7 días.

Si no creaste esta cuenta, puedes ignorar este correo.

¡Esperamos verte pronto!

Saludos,
El equipo de LMS
        """
        
        # Send welcome/activation email
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [instance.email],
                fail_silently=False,
            )
        except Exception as e:
            # Log error but don't fail user creation
            print(f"Error sending activation email: {e}")


# Send welcome email for OAuth users when social account is created
try:
    from allauth.socialaccount.signals import social_account_added
    from django.dispatch import receiver as signal_receiver
    
    @signal_receiver(social_account_added)
    def send_welcome_email_oauth(sender, request, sociallogin, **kwargs):
        """Send welcome email when a user signs up via OAuth"""
        user = sociallogin.user
        if user and user.email:
            subject = "¡Bienvenido a nuestra plataforma!"
            message = f"""
Hola {user.get_full_name() or user.username},

¡Bienvenido a nuestra plataforma de aprendizaje!

Tu cuenta ha sido creada exitosamente y ya está activa. Puedes comenzar a explorar nuestros cursos inmediatamente.

¡Esperamos que disfrutes aprendiendo con nosotros!

Saludos,
El equipo de LMS
            """
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Error sending welcome email: {e}")
except ImportError:
    # allauth signals not available - OAuth welcome emails will be skipped
    pass
