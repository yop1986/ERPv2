from django.contrib import admin

from .models import Usuario, ParametriaArchivoEncabezado, ParametriaArchivoDetalle



class ParametriaArchivoDetalleInline(admin.TabularInline):
    model = ParametriaArchivoDetalle


class ParametriaArchivoEncabezadoAdmin(admin.ModelAdmin):
   inlines = [ParametriaArchivoDetalleInline,]



admin.site.register(Usuario)
admin.site.register(ParametriaArchivoEncabezado,ParametriaArchivoEncabezadoAdmin)
