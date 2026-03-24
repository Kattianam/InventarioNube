from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('api/categorias/', views.api_categorias),
    path('api/categorias/crear/', views.api_categoria_crear),
    path('api/categorias/<int:pk>/eliminar/', views.api_categoria_eliminar),
    path('api/productos/', views.api_productos),
    path('api/productos/crear/', views.api_producto_crear),
    path('api/productos/<int:pk>/', views.api_producto_detalle),
    path('api/productos/<int:pk>/foto/', views.api_foto_producto),
    path('api/buscar/<str:codigo>/', views.api_buscar_codigo),
    path('api/scan/', views.api_scan_imagen),
    path('api/mas-vendidos/', views.api_mas_vendidos),
    path('api/clientes/', views.api_clientes),
    path('api/clientes/crear/', views.api_cliente_crear),
    path('api/clientes/<int:pk>/', views.api_cliente_detalle),
    path('api/clientes/<int:pk>/historial/', views.api_historial_cliente),
    path('api/ventas/', views.api_ventas),
    path('api/ventas/crear/', views.api_venta_crear),
    path('api/ventas/<int:pk>/', views.api_venta_detalle),
    path('api/ventas/<int:venta_id>/pago/', views.api_pago_crear),
    path('api/reportes/', views.api_reportes),
    path('api/reportes/ventas/', views.api_reportes_ventas),
    path('api/buscar-voz/', views.api_buscar_voz),
    path('api/config/', views.api_config_get),
    path('api/config/guardar/', views.api_config_save),
]
