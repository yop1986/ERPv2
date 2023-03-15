# ERPv2
Versión mejorada

## Ambiente de desarrollo

### Dependencias

Se configura un archivo con las dependencias del proyecto en [documentacion/dependencias.txt](/documentacion/dependencias.txt) o se instalan las últimas versiones de los siguientes paquetes con __pip install__

- django 
- crispy-bootstrap5

*dependencias creadas por medio del comando __pip freeze > requirements.txt__*
*dependencias restauradas por mdeio del comando __pip install -r requirements.txt__*

### Configuracion del proyecto

Es necesario crear un nuevo proyecto

    > django-admin startproject Base Base/

Para el ambiente de desarrollo se configura el archivo __Base/settings.py__

Se utiliza para definir urls dinámicas (especificadas al final de esta configuración)

    > from django.urls import reverse_lazy

Se instalan las aplicaciones utilizadas y desarrolladas en el ERP 

    > INSTALLED_APPS = [
        ...
        'crispy_forms',
        'crispy_bootstrap5',
    
        'usuarios',
    ]

Se define la ubicación de las plantillas

    TEMPLATES = [
        {
        ...
        'DIRS': [BASE_DIR / 'templates/',],
        ...
        },
    ]

Se configura la base de datos de acuerdo con la necesidad [Django Databases](https://docs.djangoproject.com/en/4.1/ref/settings/#databases)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

Se configuran las opciones de internacionalización (idioma y otras opciones) [Internationalization](https://docs.djangoproject.com/en/4.1/topics/i18n/)

    LANGUAGE_CODE = 'es-gt'
    TIME_ZONE = 'America/Guatemala'
    USE_I18N = True
    USE_TZ = True

Se configura el servidor de correos de prueba para desarrollo

    ###
    ### Servidor de correos
    ###
    if DEBUG:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        pass
        

Se definen variables globales, utilizadas en toda la aplicacion

    ###
    ### Variables Globales
    ###
    GENERAL_SITE_INFO = {
        'nombre_sitio': 'ERPv2',
    }

Modelo de usuario personalización así como opciones de redireccionamiento utilizadas por las pantallas de logueo.

    AUTH_USER_MODEL = 'usuarios.Usuario'
    LOGIN_URL = reverse_lazy('usuarios:login')
    LOGIN_REDIRECT_URL = reverse_lazy('usuarios:home')
    LOGOUT_REDIRECT_URL = reverse_lazy('usuarios:home')

Plantillas base utilizando bootstrap5

    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

Posterior a esta configuracion es necesario agregar las urls al proyecto base __Base/urls.py__

    path('', include('usuarios.urls')),

Creación de migraciones y super usuario para empezar a utilizar

    Base>python manage.py check
    Base>python manage.py makemigrations
    Base>python manage.py makemigrations usuarios
    Base>python manage.py migrate
    Base>python manage.py createsuperuser
    Base>python manage.py runserver <port>