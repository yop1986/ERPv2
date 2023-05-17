# ERPv2
Versión mejorada

## Ambiente de desarrollo

### Dependencias

Se crea un ambiente virtual para mantener independencia en las configuraciones

    ERPv2>virtualenv .venv
    ERPv2>.venv\Scripts\activate.bat

Se configura un archivo con las dependencias del proyecto en [documentacion/dependencias.txt](/documentacion/dependencias.txt) o se instalan las últimas versiones de los siguientes paquetes con __pip install__

- django 
- crispy-bootstrap5
- openpyxl
- mysqlclient

*dependencias creadas por medio del comando __pip freeze > requirements.txt__*

*dependencias restauradas por mdeio del comando __pip install -r requirements.txt__*

### Configuracion del proyecto

Es necesario crear un nuevo proyecto

    (.venv) ERPv2> django-admin startproject Base Base/

Para el ambiente de desarrollo se configura el archivo __Base/Base/settings.py__

Se utiliza para definir urls dinámicas (especificadas al final de esta configuración)

    from django.urls import reverse_lazy

Se instalan las aplicaciones utilizadas y desarrolladas en el ERP 

    INSTALLED_APPS = [
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
            'ENGINE': 'django.db.backends.mysql',
            'NAME': '<db_name>',
            'USER': '<db_username>',
            'PASSWORD': '<db_password>',
            'HOST': '127.0.0.1',
            'PORT': '3306',
        }
    }

Se configuran las opciones de internacionalización (idioma y otras opciones) [Internationalization](https://docs.djangoproject.com/en/4.1/topics/i18n/)

    LANGUAGE_CODE = 'es-gt'
    TIME_ZONE = 'America/Guatemala'
    USE_I18N = True
    USE_TZ = False

Se configura la ruta general de archivos static, se puede utilizar cualquiera de las siguientes opciones

    STATIC_ROOT = BASE_DIR / "static"
    #STATIC_ROOT = os.path.join(BASE_DIR, 'static')
    #STATICFILES_DIRS = [ BASE_DIR / "static", ]

Se configura el servidor de correos de prueba para desarrollo

    ###
    ### Servidor de correos
    ###
    if DEBUG:
        EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
    else:
        pass

Existe un archivo de configuracion en el directorio Base\Static, en el cual es necesario validar elementos utilizados para la aplicacion en general bajo el formato 

    [sección]
    # Comentarios
    variable = valor

Se definen variables globales, utilizadas en toda la aplicacion

    # esta información para cada una de las apps instaladas
    INFORMACION_APLICACIONES = {
        'app': {
            'nombre': _(''),
            'descripcion': _(''),
            'imagen': _(''),
        }
    }

Modelo de usuario personalización así como opciones de redireccionamiento utilizadas por las pantallas de logueo.

    AUTH_USER_MODEL = 'usuarios.Usuario'
    LOGIN_URL = reverse_lazy('usuarios:login')
    LOGIN_REDIRECT_URL = reverse_lazy('usuarios:home')
    LOGOUT_REDIRECT_URL = reverse_lazy('usuarios:home')

Plantillas base utilizando bootstrap5

    CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
    CRISPY_TEMPLATE_PACK = "bootstrap5"

Manejador de carga de archivos excel

    FILE_UPLOAD_HANDLERS = ("django_excel.ExcelMemoryFileUploadHandler",
                            "django_excel.TemporaryExcelFileUploadHandler")

Posterior a esta configuracion es necesario agregar las urls al proyecto base __Base/urls.py__

    path('', include('usuarios.urls')),

Creación de migraciones y super usuario para empezar a utilizar

    Base>python manage.py check
    Base>python manage.py makemigrations
    Base>python manage.py makemigrations usuarios
    Base>python manage.py migrate
    Base>python manage.py createsuperuser
    Base>python manage.py runserver <port>