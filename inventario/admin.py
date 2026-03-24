from django.contrib import admin
from .models import Producto, MovimientoStock


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'codigo_barras', 'categoria', 'precio', 'stock', 'unidad', 'fecha_registro']
    list_filter = ['categoria', 'unidad']
    search_fields = ['nombre', 'codigo_barras', 'proveedor']
    readonly_fields = ['fecha_registro', 'fecha_actualizacion']


@admin.register(MovimientoStock)
class MovimientoAdmin(admin.ModelAdmin):
    list_display = ['producto', 'tipo', 'cantidad', 'motivo', 'fecha']
    list_filter = ['tipo']
    readonly_fields = ['fecha']
