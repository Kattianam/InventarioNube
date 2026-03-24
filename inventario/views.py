# ═══════════════════════════════════════════════════════════════
# InventarioNube — Sistema de inventario, ventas y facturación
# Desarrollado con la asistencia de Claude (Anthropic)
# https://claude.ai · https://github.com/anthropics/claude
#
# Autora del proyecto: ver perfil de GitHub del repositorio
# Versión: 11.0 · Django 4.2 · Python 3.12
# ═══════════════════════════════════════════════════════════════

import json
import base64
from datetime import date, timedelta
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Sum, Count
from django.utils import timezone
from .models import (Producto, MovimientoStock, Cliente, Venta, DetalleVenta,
                     Pago, ConfigNegocio, CategoriaProducto)


def index(request):
    ConfigNegocio.get()  # ensures defaults created
    return render(request, 'inventario/index.html')


# ─── CATEGORÍAS ───────────────────────────────────────────────

def api_categorias(request):
    cats = CategoriaProducto.objects.filter(activa=True)
    return JsonResponse({'categorias': [{'id': c.id, 'nombre': c.nombre, 'emoji': c.emoji} for c in cats]})


@csrf_exempt
def api_categoria_crear(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    data = json.loads(request.body)
    nombre = data.get('nombre', '').strip()
    emoji = data.get('emoji', '📦').strip()
    if not nombre:
        return JsonResponse({'error': 'Nombre requerido'}, status=400)
    cat, created = CategoriaProducto.objects.get_or_create(nombre=nombre, defaults={'emoji': emoji})
    if not created:
        cat.emoji = emoji
        cat.activa = True
        cat.save()
    return JsonResponse({'ok': True, 'id': cat.id, 'nombre': cat.nombre, 'emoji': cat.emoji, 'created': created})


@csrf_exempt
def api_categoria_eliminar(request, pk):
    cat = get_object_or_404(CategoriaProducto, pk=pk)
    cat.activa = False
    cat.save()
    return JsonResponse({'ok': True})


# ─── PRODUCTOS ────────────────────────────────────────────────

def api_productos(request):
    q = request.GET.get('q', '')
    categoria = request.GET.get('categoria', '')
    productos = Producto.objects.all()
    if q:
        productos = productos.filter(Q(nombre__icontains=q) | Q(codigo_barras__icontains=q) | Q(proveedor__icontains=q))
    if categoria:
        productos = productos.filter(categoria__icontains=categoria)
    data = []
    for p in productos:
        data.append({
            'id': p.id, 'indice': p.indice, 'codigo_barras': p.codigo_barras, 'nombre': p.nombre,
            'categoria': p.categoria, 'precio': float(p.precio), 'stock': p.stock,
            'unidad': p.unidad, 'unidad_display': p.get_unidad_display(),
            'proveedor': p.proveedor, 'ubicacion': p.ubicacion, 'notas': p.notas,
            'valor_total': float(p.valor_total),
            'imagen': p.imagen.url if p.imagen else None,
            'fecha_registro': p.fecha_registro.strftime('%d/%m/%Y %H:%M'),
            'fecha_actualizacion': p.fecha_actualizacion.strftime('%d/%m/%Y %H:%M'),
        })
    return JsonResponse({'productos': data, 'total': len(data)})


@csrf_exempt
def api_producto_detalle(request, pk):
    producto = get_object_or_404(Producto, pk=pk)
    if request.method == 'GET':
        movimientos = list(producto.movimientos.values('tipo', 'cantidad', 'motivo', 'fecha').order_by('-fecha')[:10])
        for m in movimientos:
            m['fecha'] = m['fecha'].strftime('%d/%m/%Y %H:%M')
        return JsonResponse({
            'id': producto.id, 'codigo_barras': producto.codigo_barras, 'nombre': producto.nombre,
            'categoria': producto.categoria, 'precio': float(producto.precio), 'stock': producto.stock,
            'unidad': producto.unidad, 'proveedor': producto.proveedor, 'ubicacion': producto.ubicacion,
            'notas': producto.notas, 'valor_total': float(producto.valor_total),
            'imagen': producto.imagen.url if producto.imagen else None,
            'fecha_registro': producto.fecha_registro.strftime('%d/%m/%Y %H:%M'), 'movimientos': movimientos,
        })
    elif request.method == 'DELETE':
        producto.delete()
        return JsonResponse({'ok': True})


@csrf_exempt
def api_producto_crear(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    data = json.loads(request.body)
    codigo = data.get('codigo_barras', '').strip()
    nombre = data.get('nombre', '').strip()
    if not codigo or not nombre:
        return JsonResponse({'error': 'Código y nombre son obligatorios'}, status=400)
    # Generate unique indice
    ultimo = Producto.objects.count()
    indice_nuevo = str(ultimo + 1).zfill(4)
    while Producto.objects.filter(indice=indice_nuevo).exists():
        ultimo += 1
        indice_nuevo = str(ultimo + 1).zfill(4)

    producto, created = Producto.objects.get_or_create(
        codigo_barras=codigo,
        defaults={
            'indice': indice_nuevo,
            'nombre': nombre, 'categoria': data.get('categoria', 'Otro'),
            'precio': data.get('precio', 0), 'stock': data.get('stock', 0),
            'unidad': data.get('unidad', 'unidad'), 'proveedor': data.get('proveedor', ''),
            'ubicacion': data.get('ubicacion', ''), 'notas': data.get('notas', ''),
        }
    )
    # Assign indice if missing (old products)
    if not producto.indice:
        producto.indice = indice_nuevo
        producto.save()
    if not created:
        producto.nombre = nombre
        producto.categoria = data.get('categoria', producto.categoria)
        producto.precio = data.get('precio', producto.precio)
        producto.unidad = data.get('unidad', producto.unidad)
        producto.proveedor = data.get('proveedor', producto.proveedor)
        producto.ubicacion = data.get('ubicacion', producto.ubicacion)
        producto.notas = data.get('notas', producto.notas)
        nuevo_stock = int(data.get('stock', producto.stock))
        if nuevo_stock != producto.stock:
            MovimientoStock.objects.create(producto=producto, tipo='ajuste', cantidad=nuevo_stock - producto.stock, motivo='Actualización')
            producto.stock = nuevo_stock
        producto.save()
    return JsonResponse({'ok': True, 'created': created, 'id': producto.id, 'mensaje': 'Producto creado' if created else 'Producto actualizado'})


def api_buscar_codigo(request, codigo):
    try:
        p = Producto.objects.get(codigo_barras=codigo)
        return JsonResponse({
            'encontrado': True, 'id': p.id, 'indice': p.indice, 'nombre': p.nombre, 'categoria': p.categoria,
            'precio': float(p.precio), 'stock': p.stock, 'unidad': p.unidad,
            'proveedor': p.proveedor, 'ubicacion': p.ubicacion, 'notas': p.notas,
            'imagen': p.imagen.url if p.imagen else None,
        })
    except Producto.DoesNotExist:
        return JsonResponse({'encontrado': False})


@csrf_exempt
def api_foto_producto(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    producto = get_object_or_404(Producto, pk=pk)
    try:
        from django.core.files.base import ContentFile
        data = json.loads(request.body)
        img_data = data.get('foto', '')
        if ',' in img_data:
            img_data = img_data.split(',')[1]
        img_bytes = base64.b64decode(img_data)
        filename = f'producto_{pk}.jpg'
        producto.imagen.save(filename, ContentFile(img_bytes), save=True)
        return JsonResponse({'ok': True, 'url': producto.imagen.url})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_mas_vendidos(request):
    top = (DetalleVenta.objects
           .values('producto__id', 'producto__nombre', 'producto__precio',
                   'producto__categoria', 'producto__stock', 'producto__imagen')
           .annotate(total_vendido=Sum('cantidad'))
           .order_by('-total_vendido')[:12])
    data = []
    for p in top:
        img_url = ('/media/' + p['producto__imagen']) if p['producto__imagen'] else None
        data.append({'id': p['producto__id'], 'indice': '', 'nombre': p['producto__nombre'],
                     'precio': float(p['producto__precio']), 'categoria': p['producto__categoria'],
                     'stock': p['producto__stock'], 'total_vendido': p['total_vendido'], 'imagen': img_url})
    if not data:
        for p in Producto.objects.order_by('-fecha_registro')[:12]:
            data.append({'id': p.id, 'nombre': p.nombre, 'precio': float(p.precio),
                         'categoria': p.categoria, 'stock': p.stock, 'total_vendido': 0,
                         'imagen': p.imagen.url if p.imagen else None})
    return JsonResponse({'productos': data})


@csrf_exempt
def api_scan_imagen(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    try:
        import cv2, numpy as np
        from pyzbar.pyzbar import decode
        data = json.loads(request.body)
        img_data = data.get('imagen', '')
        if ',' in img_data:
            img_data = img_data.split(',')[1]
        img_bytes = base64.b64decode(img_data)
        np_arr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        codigos = decode(img)
        if codigos:
            return JsonResponse({'encontrado': True, 'codigo': codigos[0].data.decode('utf-8')})
        return JsonResponse({'encontrado': False})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ─── CLIENTES ────────────────────────────────────────────────

def api_clientes(request):
    q = request.GET.get('q', '')
    clientes = Cliente.objects.all()
    if q:
        clientes = clientes.filter(Q(nombre__icontains=q) | Q(cedula__icontains=q) | Q(telefono__icontains=q))
    data = []
    for c in clientes:
        saldo = c.ventas.filter(estado='credito').aggregate(t=Sum('saldo'))['t'] or 0
        data.append({
            'id': c.id, 'nombre': c.nombre, 'cedula': c.cedula, 'telefono': c.telefono,
            'whatsapp': c.whatsapp, 'direccion': c.direccion,
            'saldo_pendiente': float(saldo), 'total_ventas': c.ventas.count(),
            'fecha_registro': c.fecha_registro.strftime('%d/%m/%Y'),
        })
    return JsonResponse({'clientes': data, 'total': len(data)})


@csrf_exempt
def api_cliente_crear(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    data = json.loads(request.body)
    nombre = data.get('nombre', '').strip()
    cedula = data.get('cedula', '').strip()
    if not nombre or not cedula:
        return JsonResponse({'error': 'Nombre y cédula son obligatorios'}, status=400)
    cliente, created = Cliente.objects.get_or_create(
        cedula=cedula,
        defaults={'nombre': nombre, 'telefono': data.get('telefono', ''),
                  'whatsapp': data.get('whatsapp', ''), 'direccion': data.get('direccion', '')}
    )
    if not created:
        cliente.nombre = nombre
        cliente.telefono = data.get('telefono', cliente.telefono)
        cliente.whatsapp = data.get('whatsapp', cliente.whatsapp)
        cliente.direccion = data.get('direccion', cliente.direccion)
        cliente.save()
    return JsonResponse({'ok': True, 'id': cliente.id, 'created': created,
                         'nombre': cliente.nombre, 'cedula': cliente.cedula,
                         'telefono': cliente.telefono, 'whatsapp': cliente.whatsapp})


@csrf_exempt
def api_cliente_detalle(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'DELETE':
        cliente.delete()
        return JsonResponse({'ok': True})
    ventas = []
    for v in cliente.ventas.all()[:30]:
        ventas.append({'id': v.id, 'numero': v.numero, 'total': float(v.total),
                       'saldo': float(v.saldo), 'estado': v.estado,
                       'tipo_pago': v.tipo_pago, 'fecha': v.fecha.strftime('%d/%m/%Y %H:%M')})
    saldo = cliente.ventas.filter(estado='credito').aggregate(t=Sum('saldo'))['t'] or 0
    return JsonResponse({
        'id': cliente.id, 'nombre': cliente.nombre, 'cedula': cliente.cedula,
        'telefono': cliente.telefono, 'whatsapp': cliente.whatsapp, 'direccion': cliente.direccion,
        'saldo_pendiente': float(saldo), 'ventas': ventas,
        'fecha_registro': cliente.fecha_registro.strftime('%d/%m/%Y'),
    })


def api_historial_cliente(request, pk):
    """Historial detallado de consumos, pagos y fotos por cliente"""
    cliente = get_object_or_404(Cliente, pk=pk)
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    estado_filtro = request.GET.get('estado', '')

    ventas_qs = cliente.ventas.prefetch_related('detalles__producto', 'pagos').order_by('-fecha')
    if fecha_desde:
        ventas_qs = ventas_qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas_qs = ventas_qs.filter(fecha__date__lte=fecha_hasta)
    if estado_filtro:
        ventas_qs = ventas_qs.filter(estado=estado_filtro)

    historial = []
    for v in ventas_qs:
        detalles = []
        for d in v.detalles.all():
            detalles.append({
                'producto': d.producto.nombre,
                'codigo': d.producto.codigo_barras,
                'categoria': d.producto.categoria,
                'cantidad': d.cantidad,
                'precio_unitario': float(d.precio_unitario),
                'subtotal': float(d.subtotal),
                'imagen': d.producto.imagen.url if d.producto.imagen else None,
            })
        pagos = [{'monto': float(p.monto), 'metodo': p.metodo,
                  'referencia': p.referencia, 'fecha': p.fecha.strftime('%d/%m/%Y %H:%M')} for p in v.pagos.all()]
        historial.append({
            'id': v.id, 'numero': v.numero, 'fecha': v.fecha.strftime('%d/%m/%Y %H:%M'),
            'tipo_pago': v.tipo_pago, 'estado': v.estado,
            'subtotal': float(v.subtotal), 'descuento': float(v.descuento),
            'total': float(v.total), 'total_pagado': float(v.total_pagado), 'saldo': float(v.saldo),
            'detalles': detalles, 'pagos': pagos, 'notas': v.notas,
        })

    total_comprado = sum(h['total'] for h in historial)
    total_pagado = sum(h['total_pagado'] for h in historial)
    total_saldo = sum(h['saldo'] for h in historial)

    return JsonResponse({
        'cliente': {'id': cliente.id, 'nombre': cliente.nombre, 'cedula': cliente.cedula,
                    'telefono': cliente.telefono, 'whatsapp': cliente.whatsapp},
        'resumen': {'total_comprado': round(total_comprado, 2), 'total_pagado': round(total_pagado, 2),
                    'total_saldo': round(total_saldo, 2), 'num_ventas': len(historial)},
        'historial': historial,
    })


# ─── VENTAS ──────────────────────────────────────────────────

def _gen_numero():
    hoy = timezone.now()
    prefijo = hoy.strftime('F%Y%m%d')
    ultimo = Venta.objects.filter(numero__startswith=prefijo).count()
    return f'{prefijo}{str(ultimo + 1).zfill(3)}'


@csrf_exempt
def api_venta_crear(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    data = json.loads(request.body)
    cliente_id = data.get('cliente_id')
    items = data.get('items', [])
    tipo_pago = data.get('tipo_pago', 'contado')
    plazo_dias = int(data.get('plazo_dias', 0))
    cuotas = int(data.get('cuotas', 1))
    descuento = float(data.get('descuento', 0))
    notas = data.get('notas', '')
    if not cliente_id or not items:
        return JsonResponse({'error': 'Cliente e items son obligatorios'}, status=400)
    cliente = get_object_or_404(Cliente, pk=cliente_id)
    subtotal = sum(float(i['precio']) * int(i['cantidad']) for i in items)
    total = subtotal - descuento
    fecha_venc = date.today() + timedelta(days=plazo_dias) if plazo_dias > 0 else None
    venta = Venta.objects.create(
        numero=_gen_numero(), cliente=cliente, tipo_pago=tipo_pago,
        estado='credito' if tipo_pago == 'credito' else 'pagada',
        subtotal=subtotal, descuento=descuento, total=total,
        saldo=total if tipo_pago == 'credito' else 0,
        total_pagado=total if tipo_pago == 'contado' else 0,
        plazo_dias=plazo_dias, fecha_vencimiento=fecha_venc, cuotas=cuotas, notas=notas,
    )
    for item in items:
        producto = get_object_or_404(Producto, pk=item['producto_id'])
        cantidad = int(item['cantidad'])
        precio = float(item['precio'])
        DetalleVenta.objects.create(venta=venta, producto=producto, cantidad=cantidad,
                                    precio_unitario=precio, subtotal=cantidad * precio)
        producto.stock -= cantidad
        producto.save()
        MovimientoStock.objects.create(producto=producto, tipo='salida', cantidad=cantidad, motivo=f'Venta {venta.numero}')
    if tipo_pago == 'contado':
        Pago.objects.create(venta=venta, monto=total, metodo=data.get('metodo_pago', 'efectivo'), notas='Pago contado')
    return JsonResponse({'ok': True, 'venta_id': venta.id, 'numero': venta.numero, 'total': float(total),
                         'cliente_whatsapp': cliente.whatsapp, 'cliente_nombre': cliente.nombre})


def api_ventas(request):
    q = request.GET.get('q', '')
    estado = request.GET.get('estado', '')
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    ventas = Venta.objects.select_related('cliente').all()
    if q:
        ventas = ventas.filter(Q(numero__icontains=q) | Q(cliente__nombre__icontains=q) | Q(cliente__cedula__icontains=q))
    if estado:
        ventas = ventas.filter(estado=estado)
    if fecha_desde:
        ventas = ventas.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas = ventas.filter(fecha__date__lte=fecha_hasta)
    data = [{'id': v.id, 'numero': v.numero, 'cliente_nombre': v.cliente.nombre,
              'cliente_cedula': v.cliente.cedula, 'cliente_whatsapp': v.cliente.whatsapp,
              'tipo_pago': v.tipo_pago, 'estado': v.estado, 'total': float(v.total),
              'saldo': float(v.saldo), 'total_pagado': float(v.total_pagado),
              'fecha': v.fecha.strftime('%d/%m/%Y %H:%M'),
              'fecha_vencimiento': v.fecha_vencimiento.strftime('%d/%m/%Y') if v.fecha_vencimiento else ''} for v in ventas[:200]]
    return JsonResponse({'ventas': data, 'total': len(data)})


def api_venta_detalle(request, pk):
    v = get_object_or_404(Venta, pk=pk)
    detalles = [{'producto': d.producto.nombre, 'codigo': d.producto.codigo_barras,
                 'categoria': d.producto.categoria, 'cantidad': d.cantidad,
                 'precio_unitario': float(d.precio_unitario), 'subtotal': float(d.subtotal),
                 'imagen': d.producto.imagen.url if d.producto.imagen else None} for d in v.detalles.all()]
    pagos = [{'id': p.id, 'monto': float(p.monto), 'metodo': p.metodo,
               'referencia': p.referencia, 'notas': p.notas,
               'fecha': p.fecha.strftime('%d/%m/%Y %H:%M')} for p in v.pagos.all()]
    cuota_monto = round(float(v.saldo) / v.cuotas, 2) if v.cuotas > 0 and float(v.saldo) > 0 else 0
    return JsonResponse({
        'id': v.id, 'numero': v.numero,
        'cliente': {'id': v.cliente.id, 'nombre': v.cliente.nombre, 'cedula': v.cliente.cedula,
                    'telefono': v.cliente.telefono, 'whatsapp': v.cliente.whatsapp, 'direccion': v.cliente.direccion},
        'tipo_pago': v.tipo_pago, 'estado': v.estado,
        'subtotal': float(v.subtotal), 'descuento': float(v.descuento), 'total': float(v.total),
        'total_pagado': float(v.total_pagado), 'saldo': float(v.saldo),
        'plazo_dias': v.plazo_dias, 'cuotas': v.cuotas, 'cuota_monto': cuota_monto,
        'fecha_vencimiento': v.fecha_vencimiento.strftime('%d/%m/%Y') if v.fecha_vencimiento else '',
        'notas': v.notas, 'fecha': v.fecha.strftime('%d/%m/%Y %H:%M'),
        'detalles': detalles, 'pagos': pagos,
    })


# ─── PAGOS ───────────────────────────────────────────────────

@csrf_exempt
def api_pago_crear(request, venta_id):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    venta = get_object_or_404(Venta, pk=venta_id)
    data = json.loads(request.body)
    monto = float(data.get('monto', 0))
    if monto <= 0:
        return JsonResponse({'error': 'Monto inválido'}, status=400)
    if monto > float(venta.saldo):
        return JsonResponse({'error': f'Monto supera el saldo (${venta.saldo})'}, status=400)
    Pago.objects.create(venta=venta, monto=monto, metodo=data.get('metodo', 'efectivo'),
                        referencia=data.get('referencia', ''), notas=data.get('notas', ''))
    venta.actualizar_saldo()
    return JsonResponse({'ok': True, 'saldo_actual': float(venta.saldo), 'estado': venta.estado})


# ─── REPORTES ────────────────────────────────────────────────

def api_reportes(request):
    productos = Producto.objects.all()
    total_productos = productos.count()
    total_unidades = productos.aggregate(t=Sum('stock'))['t'] or 0
    valor_total = sum(float(p.valor_total) for p in productos)

    # Por categoría configurable
    cats = CategoriaProducto.objects.filter(activa=True)
    por_categoria = []
    for cat in cats:
        qs = productos.filter(categoria__icontains=cat.nombre)
        cnt = qs.count()
        if cnt > 0:
            por_categoria.append({
                'categoria': cat.nombre, 'emoji': cat.emoji, 'cantidad': cnt,
                'valor': round(sum(float(p.valor_total) for p in qs), 2),
                'stock_total': sum(p.stock for p in qs),
                'productos': [{'nombre': p.nombre, 'stock': p.stock, 'precio': float(p.precio),
                                'imagen': p.imagen.url if p.imagen else None} for p in qs[:5]]
            })
    stock_bajo = list(productos.filter(stock__lte=5).values('id', 'nombre', 'stock', 'unidad', 'codigo_barras', 'categoria')[:15])
    recientes = [{'id': p.id, 'indice': p.indice, 'nombre': p.nombre, 'categoria': p.categoria,
                  'fecha_registro': p.fecha_registro.strftime('%d/%m/%Y'), 'precio': float(p.precio),
                  'stock': p.stock, 'imagen': p.imagen.url if p.imagen else None}
                 for p in productos.order_by('-fecha_registro')[:10]]
    return JsonResponse({'resumen': {'total_productos': total_productos, 'total_unidades': total_unidades,
                                      'valor_total': round(valor_total, 2)},
                          'por_categoria': por_categoria, 'stock_bajo': stock_bajo, 'recientes': recientes})


def api_reportes_ventas(request):
    hoy = timezone.now().date()
    mes_inicio = hoy.replace(day=1)
    fecha_desde = request.GET.get('desde', '')
    fecha_hasta = request.GET.get('hasta', '')
    estado_f = request.GET.get('estado', '')

    ventas_qs = Venta.objects.select_related('cliente').all()
    if fecha_desde:
        ventas_qs = ventas_qs.filter(fecha__date__gte=fecha_desde)
    if fecha_hasta:
        ventas_qs = ventas_qs.filter(fecha__date__lte=fecha_hasta)
    if estado_f:
        ventas_qs = ventas_qs.filter(estado=estado_f)

    ventas_hoy = Venta.objects.filter(fecha__date=hoy)
    ventas_mes = Venta.objects.filter(fecha__date__gte=mes_inicio)
    creditos = Venta.objects.filter(estado='credito')

    return JsonResponse({
        'hoy': {'ventas': ventas_hoy.count(), 'total': float(ventas_hoy.aggregate(t=Sum('total'))['t'] or 0)},
        'mes': {'ventas': ventas_mes.count(), 'total': float(ventas_mes.aggregate(t=Sum('total'))['t'] or 0)},
        'creditos': {'cantidad': creditos.count(), 'saldo_total': float(creditos.aggregate(t=Sum('saldo'))['t'] or 0)},
        'filtradas': {
            'ventas': ventas_qs.count(),
            'total': float(ventas_qs.aggregate(t=Sum('total'))['t'] or 0),
            'pagadas': ventas_qs.filter(estado='pagada').count(),
            'credito': ventas_qs.filter(estado='credito').count(),
        },
        'lista': [{'id': v.id, 'numero': v.numero, 'cliente': v.cliente.nombre,
                   'cedula': v.cliente.cedula, 'whatsapp': v.cliente.whatsapp,
                   'total': float(v.total), 'saldo': float(v.saldo), 'estado': v.estado,
                   'tipo_pago': v.tipo_pago, 'fecha': v.fecha.strftime('%d/%m/%Y %H:%M')} for v in ventas_qs[:200]],
        'creditos_lista': [{'id': v.id, 'numero': v.numero, 'cliente': v.cliente.nombre,
                             'cedula': v.cliente.cedula, 'telefono': v.cliente.telefono,
                             'whatsapp': v.cliente.whatsapp, 'total': float(v.total), 'saldo': float(v.saldo),
                             'cuotas': v.cuotas,
                             'vencimiento': v.fecha_vencimiento.strftime('%d/%m/%Y') if v.fecha_vencimiento else 'Sin plazo',
                             'fecha': v.fecha.strftime('%d/%m/%Y')} for v in creditos.all()],
        'ultimas_ventas': [{'numero': v.numero, 'cliente': v.cliente.nombre, 'total': float(v.total),
                             'estado': v.estado, 'fecha': v.fecha.strftime('%d/%m/%Y %H:%M')}
                            for v in Venta.objects.select_related('cliente').all()[:10]],
    })




# ─── BÚSQUEDA POR VOZ ─────────────────────────────────────────

def api_buscar_voz(request):
    """Búsqueda fuzzy de productos para reconocimiento de voz"""
    q = request.GET.get('q', '').strip().lower()
    if not q:
        return JsonResponse({'productos': []})

    productos = Producto.objects.filter(stock__gt=0)
    resultados = []

    # Exact and partial matches
    for p in productos:
        nombre_lower = p.nombre.lower()
        score = 0
        # Exact match
        if q == nombre_lower:
            score = 100
        # Starts with
        elif nombre_lower.startswith(q):
            score = 90
        # Contains full query
        elif q in nombre_lower:
            score = 80
        else:
            # Word matching
            palabras_q = q.split()
            palabras_p = nombre_lower.split()
            matches = sum(1 for pw in palabras_q if any(pw in pp or pp.startswith(pw) for pp in palabras_p))
            if matches > 0:
                score = int(70 * matches / len(palabras_q))

        if score > 30:
            resultados.append({
                'id': p.id, 'indice': p.indice, 'nombre': p.nombre,
                'categoria': p.categoria, 'precio': float(p.precio),
                'stock': p.stock, 'unidad': p.unidad,
                'imagen': p.imagen.url if p.imagen else None,
                'score': score,
            })

    resultados.sort(key=lambda x: x['score'], reverse=True)
    return JsonResponse({'productos': resultados[:6], 'query': q})

# ─── CONFIG ──────────────────────────────────────────────────

def api_config_get(request):
    c = ConfigNegocio.get()
    cats = list(CategoriaProducto.objects.filter(activa=True).values('id', 'nombre', 'emoji', 'orden'))
    return JsonResponse({'nombre': c.nombre, 'ruc': c.ruc, 'telefono': c.telefono,
                         'direccion': c.direccion, 'pie_pagina': c.pie_pagina,
                         'logo_texto': c.logo_texto, 'whatsapp_admin': c.whatsapp_admin,
                         'email_admin': c.email_admin, 'categorias': cats})


@csrf_exempt
def api_config_save(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST requerido'}, status=405)
    data = json.loads(request.body)
    c = ConfigNegocio.get()
    c.nombre = data.get('nombre', c.nombre)
    c.ruc = data.get('ruc', c.ruc)
    c.telefono = data.get('telefono', c.telefono)
    c.direccion = data.get('direccion', c.direccion)
    c.pie_pagina = data.get('pie_pagina', c.pie_pagina)
    c.logo_texto = data.get('logo_texto', c.logo_texto)
    c.whatsapp_admin = data.get('whatsapp_admin', c.whatsapp_admin)
    c.email_admin = data.get('email_admin', c.email_admin)
    c.save()
    return JsonResponse({'ok': True})
