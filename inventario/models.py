from django.db import models


UNIDADES = [
    ('unidad', 'Unidad'), ('kg', 'Kilogramo'), ('litro', 'Litro'),
    ('caja', 'Caja'), ('paquete', 'Paquete'), ('metro', 'Metro'), ('docena', 'Docena'),
]


class CategoriaProducto(models.Model):
    """Categorías configurables por el usuario"""
    nombre = models.CharField(max_length=100, unique=True)
    emoji = models.CharField(max_length=10, default='📦')
    orden = models.IntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ['orden', 'nombre']

    def __str__(self):
        return f'{self.emoji} {self.nombre}'

    @classmethod
    def get_defaults(cls):
        defaults = [
            ('alimentos', 'Alimentos / Comestibles', '🍎'),
            ('bebidas', 'Bebidas', '🥤'),
            ('vegetales', 'Vegetales / Frutas', '🥦'),
            ('artesanal', 'Artesanal / Hecho a mano', '🎨'),
            ('limpieza', 'Químicos / Limpieza', '🧼'),
            ('farmacia', 'Farmacia / Medicamentos', '💊'),
            ('electronica', 'Electrónica', '💻'),
            ('ropa', 'Ropa / Textiles', '👕'),
            ('otro', 'Otro', '📦'),
        ]
        for i, (slug, nombre, emoji) in enumerate(defaults):
            cls.objects.get_or_create(nombre=nombre, defaults={'emoji': emoji, 'orden': i})


class Producto(models.Model):
    indice = models.CharField(max_length=20, unique=True, blank=True, verbose_name='Índice')
    codigo_barras = models.CharField(max_length=100, unique=True, verbose_name='Código de barras')
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    categoria = models.CharField(max_length=100, default='Otro', verbose_name='Categoría')
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name='Precio ($)')
    stock = models.IntegerField(default=0, verbose_name='Stock')
    unidad = models.CharField(max_length=20, choices=UNIDADES, default='unidad', verbose_name='Unidad')
    proveedor = models.CharField(max_length=200, blank=True, verbose_name='Proveedor')
    ubicacion = models.CharField(max_length=200, blank=True, verbose_name='Ubicación')
    notas = models.TextField(blank=True, verbose_name='Notas')
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, verbose_name='Imagen')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        ordering = ['-fecha_registro']

    def __str__(self):
        return f'{self.nombre} ({self.codigo_barras})'

    @property
    def valor_total(self):
        return self.precio * self.stock


class Cliente(models.Model):
    nombre = models.CharField(max_length=200, verbose_name='Nombre completo')
    cedula = models.CharField(max_length=20, unique=True, verbose_name='Cédula / RUC')
    telefono = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    direccion = models.TextField(blank=True, verbose_name='Dirección')
    whatsapp = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp (con código país)')
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'
        ordering = ['nombre']

    def __str__(self):
        return f'{self.nombre} ({self.cedula})'


ESTADOS_VENTA = [
    ('pagada', 'Pagada'),
    ('credito', 'Crédito'),
    ('vencida', 'Vencida'),
]


class Venta(models.Model):
    numero = models.CharField(max_length=20, unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='ventas')
    tipo_pago = models.CharField(max_length=20, choices=[('contado', 'Contado'), ('credito', 'Crédito')], default='contado')
    estado = models.CharField(max_length=20, choices=ESTADOS_VENTA, default='pagada')
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    descuento = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_pagado = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    saldo = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    plazo_dias = models.IntegerField(default=0)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    cuotas = models.IntegerField(default=1)
    notas = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f'Factura {self.numero} — {self.cliente.nombre}'

    def actualizar_saldo(self):
        pagado = self.pagos.aggregate(t=models.Sum('monto'))['t'] or 0
        self.total_pagado = pagado
        self.saldo = self.total - pagado
        if self.saldo <= 0:
            self.estado = 'pagada'
        elif self.tipo_pago == 'credito':
            self.estado = 'credito'
        self.save()


class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    def save(self, *args, **kwargs):
        self.subtotal = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)


class Pago(models.Model):
    METODOS = [
        ('efectivo', 'Efectivo'), ('transferencia', 'Transferencia'),
        ('tarjeta', 'Tarjeta'), ('otro', 'Otro'),
    ]
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='pagos')
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    metodo = models.CharField(max_length=20, choices=METODOS, default='efectivo')
    referencia = models.CharField(max_length=100, blank=True)
    notas = models.CharField(max_length=300, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']


class ConfigNegocio(models.Model):
    nombre = models.CharField(max_length=200, default='Mi Negocio')
    ruc = models.CharField(max_length=20, blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    direccion = models.TextField(blank=True)
    pie_pagina = models.CharField(max_length=300, blank=True, default='Gracias por su compra')
    logo_texto = models.CharField(max_length=10, blank=True, default='🏪')
    whatsapp_admin = models.CharField(max_length=20, blank=True, verbose_name='WhatsApp administrador')
    email_admin = models.CharField(max_length=100, blank=True, verbose_name='Email administrador')

    class Meta:
        verbose_name = 'Configuración del negocio'

    def __str__(self):
        return self.nombre

    @classmethod
    def get(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        if created:
            CategoriaProducto.get_defaults()
        return obj


class MovimientoStock(models.Model):
    TIPOS = [('entrada', 'Entrada'), ('salida', 'Salida'), ('ajuste', 'Ajuste')]
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='movimientos')
    tipo = models.CharField(max_length=20, choices=TIPOS)
    cantidad = models.IntegerField()
    motivo = models.CharField(max_length=300, blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
