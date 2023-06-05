from django.contrib import admin

from .models import (Usuario, ParametriaArchivoEncabezado, ParametriaArchivoExtension, 
   ParametriaArchivoDetalle)



class ParametriaArchivoDetalleInline(admin.TabularInline):
    model = ParametriaArchivoDetalle

class ParametriaArchivoExtensionInline(admin.TabularInline):
    model = ParametriaArchivoExtension

class ParametriaArchivoEncabezadoAdmin(admin.ModelAdmin):
   inlines = [ParametriaArchivoExtensionInline, ParametriaArchivoDetalleInline,]



admin.site.register(Usuario)
admin.site.register(ParametriaArchivoEncabezado,ParametriaArchivoEncabezadoAdmin)
