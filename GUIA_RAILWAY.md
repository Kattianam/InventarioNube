# 🚀 Guía para subir InventarioNube a Railway.app

## ¿Qué vas a lograr?
Tu app estará en internet 24/7 con una URL pública como:
https://inventarionube-production.up.railway.app

Cualquier celular en cualquier red podrá acceder sin necesitar WiFi.

---

## PASO 1 — Crear cuenta en GitHub (si no tienes)

1. Ve a https://github.com
2. Clic en "Sign up"
3. Pon tu correo, contraseña y nombre de usuario
4. Confirma tu correo

---

## PASO 2 — Instalar Git en tu PC (Windows)

1. Ve a https://git-scm.com/download/win
2. Descarga e instala (opciones por defecto están bien)
3. Abre PowerShell y verifica:
   ```
   git --version
   ```
   Debe aparecer: git version 2.x.x

---

## PASO 3 — Subir tu proyecto a GitHub

Abre PowerShell en la carpeta inventario_app y ejecuta:

```powershell
# Configurar tu identidad (solo la primera vez)
git config --global user.email "tu@correo.com"
git config --global user.name "Tu Nombre"

# Inicializar repositorio
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "InventarioNube v9 - primera versión"

# Crear repositorio en GitHub
# Ve a github.com → New repository → Nombre: inventario-nube → Create repository
# Luego copia el comando que te da GitHub, algo como:
git remote add origin https://github.com/TU_USUARIO/inventario-nube.git
git branch -M main
git push -u origin main
```

---

## PASO 4 — Crear cuenta en Railway

1. Ve a https://railway.app
2. Clic en "Login" → "Login with GitHub"
3. Autoriza Railway a acceder a tu GitHub

---

## PASO 5 — Crear proyecto en Railway

1. En Railway, clic en "New Project"
2. Elige "Deploy from GitHub repo"
3. Selecciona tu repositorio "inventario-nube"
4. Railway detecta automáticamente que es Django ✓

---

## PASO 6 — Agregar base de datos PostgreSQL

1. En tu proyecto Railway, clic en "+ New"
2. Selecciona "Database" → "PostgreSQL"
3. Railway la crea automáticamente y conecta con tu app

---

## PASO 7 — Configurar variables de entorno

En Railway → tu servicio Django → "Variables":

| Variable | Valor |
|----------|-------|
| SECRET_KEY | una_clave_larga_y_segura_123abc |
| DEBUG | False |
| ALLOWED_HOSTS | .railway.app |

Railway ya agrega DATABASE_URL automáticamente cuando conectas PostgreSQL.

---

## PASO 8 — Hacer deploy

1. Railway detecta cambios en GitHub automáticamente
2. El primer deploy toma 3-5 minutos
3. Ve a "Deployments" para ver el progreso
4. Cuando dice "Success" ✓, clic en el link que te da Railway

---

## PASO 9 — Dominio personalizado (opcional)

En Railway → Settings → Domains:
- Puedes usar el dominio gratis: xxx.up.railway.app
- O conectar tu propio dominio: www.minegocio.com (~$10/año en Namecheap)

---

## Costos Railway

| Plan | Precio | Incluye |
|------|--------|---------|
| Hobby (gratis) | $0/mes | 500 horas/mes (suficiente si lo usas en horario de trabajo) |
| Pro | $5/mes | Siempre activo, sin límites |

**Recomendación:** empieza con el plan gratis. Si necesitas que esté disponible las 24 horas del día, actualiza a Pro por $5/mes.

---

## Actualizar la app en el futuro

Cuando hagas cambios a tus archivos, solo ejecuta:
```powershell
git add .
git commit -m "descripción del cambio"
git push
```
Railway despliega automáticamente en 2-3 minutos.

---

## ¿Problemas? Verifica esto:

1. ¿El deploy falló? → Ve a "Deployments" → clic en el deploy fallido → lee los logs
2. ¿La app abre pero hay error 500? → Revisa que SECRET_KEY y ALLOWED_HOSTS estén bien
3. ¿Las imágenes no se ven? → Normal en Railway gratuito (no tiene almacenamiento persistente). Solución: usar Cloudinary para imágenes (puedo ayudarte con eso después)

---

Generado con Claude (Anthropic) — InventarioNube v9
