<div align="center">

# 📦 InventarioNube

### Sistema completo de inventario, ventas y facturación
### con escáner de cámara, voz y WhatsApp

[![Python](https://img.shields.io/badge/Python-3.12-blue?style=for-the-badge&logo=python)](https://python.org)
[![Django](https://img.shields.io/badge/Django-4.2-green?style=for-the-badge&logo=django)](https://djangoproject.com)
[![PWA](https://img.shields.io/badge/PWA-Instalable-purple?style=for-the-badge)](https://web.dev/pwa)
[![License](https://img.shields.io/badge/Licencia-MIT-orange?style=for-the-badge)](LICENSE)

**Desarrollado con la asistencia de [Claude](https://claude.ai) (Anthropic)**

[✨ Ver demo](#demo) · [🚀 Instalación](#instalación) · [📲 Solicitar instalación](#-solicitar-instalación-personalizada) · [💬 Contacto](#-contacto)

</div>

---

## 📸 Demo

> La app funciona directamente desde el navegador del celular, sin instalar nada en Play Store.

| Nueva Venta | Escáner | Factura JPG |
|---|---|---|
| Productos frecuentes con foto | Cámara detecta código automáticamente | Se genera y envía por WhatsApp |

---

## ✨ Funcionalidades principales

- 📷 **Escáner de códigos de barras** desde la cámara del celular
- 🎤 **Búsqueda por voz** en español — di el nombre del producto y lo encuentra
- 🗣️ **Respuestas audibles** — el sistema habla cuando hay errores o confirmaciones
- 🧾 **Factura en JPG** liviana, lista para compartir por WhatsApp
- 📲 **Envío por WhatsApp** automático al cliente al confirmar la venta
- 💳 **Ventas al contado y a crédito** con cuotas personalizadas
- 👥 **Historial de clientes** con fotos de productos comprados
- 📊 **Reportes por categoría** con fotos e índice único por producto
- 🎨 **Temas de color** configurables (8 temas incluidos)
- 📱 **PWA instalable** — funciona como app nativa en Android e iOS
- 👴 **Diseño accesible** — letras grandes, botones grandes, alto contraste

---

## 🚀 Instalación

### Requisitos previos
- Python 3.10+
- pip
- `libzbar` (para leer códigos de barras)

```bash
# Ubuntu / Debian
sudo apt-get install -y libzbar0

# macOS
brew install zbar

# Windows — descarga ZBar desde: http://zbar.sourceforge.net
```

### Pasos

```bash
git clone https://github.com/TU_USUARIO/inventario-nube.git
cd inventario-nube

python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

Abre en tu navegador: `http://localhost:8000`

Desde el celular (misma red WiFi): `http://[IP_DE_TU_PC]:8000`

### ⚙️ Configuración inicial

> **Para que la cámara funcione en Chrome Android:**
> 1. Abre `chrome://flags`
> 2. Busca `Insecure origins treated as secure`
> 3. Agrega `http://[TU_IP]:8000`
> 4. Toca Relaunch

---

## 🔧 Personalización

### Cambiar el nombre y logo del negocio
En la app ve a **⚙️ Configuración** y edita nombre, RUC, teléfono y pie de página de factura.

### Cambiar colores
En **⚙️ Configuración → Tema y colores** elige entre 8 temas disponibles.

### 🔒 Línea que debes cambiar antes de usar en producción

En el archivo `inventario_project/settings.py`, línea 8:

```python
# CAMBIA ESTA LÍNEA — usa una clave larga y única para tu negocio
SECRET_KEY = config('SECRET_KEY', default='django-insecure-cambia-esto-en-produccion-xyz123')
```

Genera tu propia clave en: https://djecrety.ir

---

## 🌐 Deploy en Railway.app

Ver guía completa paso a paso en: [GUIA_RAILWAY.md](GUIA_RAILWAY.md)

---

## 📲 Solicitar instalación personalizada

¿Quieres esta app instalada y configurada para tu negocio?

**Puedo configurártela con:**
- ✅ Tu nombre, logo y colores del negocio
- ✅ Tus categorías de productos
- ✅ Tu número de WhatsApp conectado
- ✅ Hosting en la nube 24/7 (Railway o VPS)
- ✅ Dominio personalizado (opcional)

### 👉 Para solicitar, abre un Issue en este repositorio

1. Clic en la pestaña **"Issues"** arriba
2. Clic en **"New Issue"**
3. Escribe tu nombre, país y tipo de negocio
4. Te respondo con los detalles

> 💡 Al abrir un Issue puedo ver quién está interesado, en qué país están y qué tipo de negocio tienen — sin que necesiten mi contacto directo hasta que yo les responda.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Django 4.2 + Python 3.12 | Backend y API REST |
| Quagga.js | Escáner de códigos de barras |
| Web Speech API | Reconocimiento y síntesis de voz |
| Canvas API | Generación de facturas JPG |
| WhatsApp wa.me | Envío de facturas |
| WhiteNoise | Archivos estáticos en producción |
| PWA + Service Worker | App instalable sin Play Store |
| OpenCV + pyzbar | Procesamiento de imágenes del servidor |

---

## 🤝 Créditos

Este proyecto fue desarrollado con la asistencia de **[Claude](https://claude.ai)**, el asistente de inteligencia artificial de [Anthropic](https://anthropic.com).

Claude ayudó a diseñar la arquitectura, escribir el código Django, la interfaz HTML/CSS/JS, la integración de voz, la generación de facturas JPG y la configuración para Railway.

> *"La mejor herramienta no es la que hace todo sola — es la que te ayuda a aprender mientras construyes."*

---

## 📄 Licencia

MIT License — libre para usar, modificar y distribuir con atribución.

---

## 💬 Contacto

¿Tienes preguntas o quieres colaborar?

- 🐛 **Bug o problema:** abre un [Issue](../../issues)
- 💡 **Sugerencia:** abre un [Issue](../../issues) con etiqueta `enhancement`
- 📧 **Contacto directo:** disponible en mi perfil de GitHub

---

<div align="center">

⭐ **Si este proyecto te fue útil, dale una estrella — ayuda a que más personas lo encuentren**

Made with 💙 + Claude AI · Ecuador 🇪🇨

</div>
