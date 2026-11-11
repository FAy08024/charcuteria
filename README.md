# Sistema de Gestión para Charcutería

## 1. Descripción del proyecto

Sistema web desarrollado con Django para administrar las operaciones de una charcutería que comercializa productos al detal y al por mayor.

El sistema permitirá registrar clientes, productos, inventario, ventas de contado, ventas a crédito para mayoristas, cuentas pendientes, abonos e historial de operaciones.

### Objetivo

Digitalizar los procesos comerciales del negocio para reducir errores manuales, mejorar el control de inventario y facilitar el seguimiento de las cuentas por cobrar.

### Tecnologías

- **Python:** lenguaje de programación.
- **Django:** framework para desarrollar el sistema.
- **HTML:** estructura de las páginas.
- **CSS:** diseño y presentación.
- **JavaScript:** interacciones de la interfaz.
- **SQLite:** base de datos inicial.
- **Git:** control de versiones.
- **GitHub:** repositorio y colaboración.

---

# 2. Estructura del proyecto

```text
proyecto-charcuteria/
│
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── views.py
│
├── usuarios/
├── clientes/
├── inventario/
├── ventas/
├── cuentas/
├── reportes/
│
├── templates/
│   ├── base.html
│   ├── inicio.html
│   ├── usuarios/
│   ├── clientes/
│   ├── inventario/
│   ├── ventas/
│   ├── cuentas/
│   └── reportes/
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── media/
│   └── productos/
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

### Función de cada aplicación

| Aplicación | Responsabilidad |
|---|---|
| `usuarios` | Autenticación, roles y permisos |
| `clientes` | Gestión de minoristas y mayoristas |
| `inventario` | Productos, existencias y entradas |
| `ventas` | Registro de ventas y facturas |
| `cuentas` | Deudas, vencimientos y abonos |
| `reportes` | Historial y consultas |

---

# 3. Instalación del proyecto desde GitHub

## 3.1. Clonar el repositorio

```powershell
git clone https://github.com/FAy08024/charcuteria.git
```

**¿Qué hace?** Descarga el proyecto de GitHub al computador.

Entrar a la carpeta descargada:

```powershell
cd charcuteria
```

**¿Qué hace?** Ubica la terminal dentro del proyecto.

Todos los comandos de `manage.py` deben ejecutarse desde la carpeta que contiene ese archivo.

## 3.2. Crear el entorno virtual

```powershell
py -m venv venv
```

**¿Qué hace?** Crea un entorno virtual llamado `venv` para instalar las dependencias del proyecto sin afectar otros programas de Python.

Activar en PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

Activar en CMD:

```cmd
venv\Scripts\activate.bat
```

**¿Qué hace?** Activa el entorno virtual.

Cuando esté activo aparecerá `(venv)` al comienzo de la terminal.

Desactivar:

```powershell
deactivate
```

**¿Qué hace?** Sale del entorno virtual.

## 3.3. Instalar las dependencias

```powershell
python -m pip install -r requirements.txt
```

**¿Qué hace?** Instala las bibliotecas que necesita el proyecto, utilizando el archivo de dependencias compartido por el equipo.

Actualizar `pip`, si es necesario:

```powershell
python -m pip install --upgrade pip
```

Comprobar la versión de Python:

```powershell
python --version
```

Comprobar la versión de Django:

```powershell
python -m django --version
```

---

# 4. Comandos para instalar y crear proyectos Django

Estos comandos son principalmente de referencia. **No es necesario volver a crear nuestro proyecto ni las aplicaciones existentes.**

Instalar Django:

```powershell
python -m pip install django
```

Crear un proyecto Django nuevo:

```powershell
django-admin startproject config .
```

**¿Qué hace?** Crea la configuración `config` y el archivo `manage.py` en la carpeta actual.

El punto final (`.`) indica que se utilizará la carpeta actual.

Crear una aplicación:

```powershell
python manage.py startapp nombre_app
```

**¿Qué hace?** Crea una aplicación Django con sus archivos iniciales.

### Aplicaciones utilizadas en la charcutería

```powershell
python manage.py startapp usuarios
python manage.py startapp clientes
python manage.py startapp inventario
python manage.py startapp ventas
python manage.py startapp cuentas
python manage.py startapp reportes
```

**Importante:** estas aplicaciones ya fueron creadas. No ejecutes nuevamente estos comandos dentro del proyecto actual.

---

# 5. Comandos para ejecutar Django

## Comprobar la configuración

```powershell
python manage.py check
```

**¿Qué hace?** Comprueba posibles errores en la configuración de Django, los modelos y las rutas, entre otros componentes.

## Aplicar las migraciones

```powershell
python manage.py migrate
```

**¿Qué hace?** Aplica las migraciones pendientes a la base de datos.

## Iniciar el servidor

```powershell
python manage.py runserver
```

**¿Qué hace?** Inicia el servidor de desarrollo.

Dirección local:

http://127.0.0.1:8000/

Panel administrativo:

http://127.0.0.1:8000/admin/

## Ejecutar en otro puerto

```powershell
python manage.py runserver 8080
```

**¿Qué hace?** Inicia Django en el puerto 8080.

Dirección:

http://127.0.0.1:8080/

## Detener el servidor

```text
Ctrl + C
```

**¿Qué hace?** Detiene el servidor desde la terminal.

---

# 6. Base de datos y modelos

Django utiliza el ORM para trabajar con los datos mediante clases de Python.

Los modelos se definen en archivos como:

```text
clientes/models.py
inventario/models.py
ventas/models.py
cuentas/models.py
```

## Crear migraciones

```powershell
python manage.py makemigrations
```

**¿Qué hace?** Detecta cambios en los modelos y genera archivos de migración.

Crear migraciones únicamente para una aplicación:

```powershell
python manage.py makemigrations clientes
```

## Aplicar migraciones

```powershell
python manage.py migrate
```

**¿Qué hace?** Actualiza la estructura de la base de datos según las migraciones pendientes.

## Consultar las migraciones

```powershell
python manage.py showmigrations
```

**¿Qué hace?** Muestra las migraciones disponibles y cuáles se han aplicado.

## Consultar SQL generado

```powershell
python manage.py sqlmigrate clientes 0001
```

**¿Qué hace?** Muestra el SQL correspondiente a la migración `0001` de clientes, si existe.

## Abrir consola de Django

```powershell
python manage.py shell
```

**¿Qué hace?** Permite ejecutar código Python con los modelos y la configuración del proyecto cargados.

Ejemplo:

```python
from clientes.models import Cliente

Cliente.objects.all()
```

Consultar todos los clientes registrados.

Para salir:

```python
exit()
```

### Advertencia importante

Los modelos, migraciones y relaciones deben coordinarse entre los integrantes.

No se recomienda eliminar migraciones existentes o borrar la base de datos para resolver errores sin comprobar primero sus consecuencias.

---

# 7. Django Admin

Django incluye un panel administrativo para gestionar los modelos registrados en `admin.py`.

## Crear superusuario

```powershell
python manage.py createsuperuser
```

**¿Qué hace?** Crea una cuenta administrativa con acceso completo al panel de Django.

Django solicitará usuario, correo electrónico (según configuración) y contraseña.

## Cambiar contraseña de usuario

```powershell
python manage.py changepassword nombre_usuario
```

**¿Qué hace?** Cambia la contraseña de un usuario existente.

## Acceder al panel

Iniciar el servidor:

```powershell
python manage.py runserver
```

Entrar a:

http://127.0.0.1:8000/admin/

### Archivos importantes

- `models.py`: define la información y las relaciones.
- `admin.py`: configura cómo administrar los modelos.
- `forms.py`: define formularios y validaciones.
- `views.py`: procesa solicitudes.
- `urls.py`: define direcciones.
- `services.py`: puede contener operaciones complejas del negocio.

---

# 8. Configuración de templates, static y media

## Templates

En `config/settings.py`:

```python
'DIRS': [BASE_DIR / 'templates'],
```

**¿Qué hace?** Permite encontrar los archivos HTML de la carpeta global `templates`.

Ejemplo:

```python
return render(request, 'inicio.html')
```

## Static

En `settings.py`:

```python
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

**¿Qué hace?** Configura los archivos CSS, JavaScript e imágenes estáticas.

Para utilizarlos en HTML:

```html
{% load static %}

<link rel="stylesheet" href="{% static 'css/estilos.css' %}">
```

## Media

En `settings.py`:

```python
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

**¿Qué hace?** Configura los archivos subidos al sistema, como imágenes de productos.

En `config/urls.py`, para servir archivos multimedia durante el desarrollo:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )
```

Esta configuración de entrega de archivos multimedia es solamente para desarrollo.

## Recopilar archivos estáticos

```powershell
python manage.py collectstatic
```

**¿Qué hace?** Reúne los archivos estáticos para preparar su distribución en un entorno de despliegue.

Necesita una configuración adecuada de `STATIC_ROOT`. No suele ser necesario durante el desarrollo local con `DEBUG=True`.

---

# 9. Pruebas y diagnóstico

Ejecutar las pruebas:

```powershell
python manage.py test
```

**¿Qué hace?** Ejecuta las pruebas automatizadas del proyecto.

Probar una aplicación:

```powershell
python manage.py test clientes
```

Comprobar preparación básica para despliegue:

```powershell
python manage.py check --deploy
```

**¿Qué hace?** Ejecuta verificaciones adicionales relacionadas con seguridad y despliegue. Algunas advertencias son esperables si todavía estamos desarrollando localmente.

Abrir una consola interactiva:

```powershell
python manage.py shell
```

Mostrar ayuda general:

```powershell
python manage.py help
```

Mostrar ayuda de un comando:

```powershell
python manage.py help migrate
```

---

# 10. Git y GitHub

Git permite registrar versiones del código.

GitHub permite almacenar el repositorio y colaborar con otros desarrolladores.

## Consultar el estado

```powershell
git status
```

**¿Qué hace?** Muestra archivos modificados, agregados o pendientes de confirmar.

## Inicializar Git

```powershell
git init
```

**¿Qué hace?** Inicializa un repositorio local.

No hace falta si el proyecto fue clonado de GitHub.

## Consultar la rama actual

```powershell
git branch
```

## Ver las ramas locales y remotas

```powershell
git branch -a
```

## Agregar todos los cambios

```powershell
git add .
```

**¿Qué hace?** Prepara los cambios para el próximo commit, respetando las exclusiones de `.gitignore`.

## Agregar un archivo específico

```powershell
git add clientes/models.py
```

**¿Qué hace?** Prepara únicamente ese archivo.

## Crear un commit

```powershell
git commit -m "feat: crear modelo Cliente"
```

**¿Qué hace?** Registra una versión de los cambios preparados.

Ejemplos de mensajes:

```powershell
git commit -m "feat: agregar gestion de productos"
git commit -m "feat: registrar abonos"
git commit -m "fix: corregir validacion de inventario"
git commit -m "docs: actualizar README"
```

## Subir los commits

```powershell
git push
```

**¿Qué hace?** Envía los commits locales a la rama remota configurada.

Para enviar explícitamente a `main`:

```powershell
git push origin main
```

## Descargar cambios del repositorio

```powershell
git pull
```

**¿Qué hace?** Descarga e integra los cambios de la rama remota correspondiente.

Para actualizar `main`:

```powershell
git pull origin main
```

## Consultar historial de commits

```powershell
git log --oneline
```

**¿Qué hace?** Muestra los commits anteriores de forma resumida.

## Consultar cambios no preparados

```powershell
git diff
```

**¿Qué hace?** Muestra los cambios que todavía no se han agregado con `git add`.

## Consultar repositorios remotos

```powershell
git remote -v
```

**¿Qué hace?** Permite comprobar la dirección del repositorio de GitHub.

---

# 11. Ramas de trabajo para los tres integrantes

Para evitar conflictos, utilizaremos ramas independientes.

### Integrante 1: interfaz

```powershell
git switch -c desarrollo/interfaz
git push -u origin desarrollo/interfaz
```

Responsable de:

- HTML.
- CSS.
- Bootstrap.
- Plantillas.
- Diseño de navegación.

### Integrante 2: base de datos

```powershell
git switch -c desarrollo/base-datos
git push -u origin desarrollo/base-datos
```

Responsable de:

- Modelos Django.
- Relaciones.
- Migraciones.
- Configuración administrativa.

### Integrante 3: funcionalidades

```powershell
git switch -c desarrollo/funcionalidades
git push -u origin desarrollo/funcionalidades
```

Responsable de:

- Vistas.
- Formularios.
- Validaciones.
- Ventas.
- Deudas.
- Abonos.

**Importante:** estos comandos de creación de ramas se ejecutan una sola vez por rama. Cada integrante debe crear únicamente su propia rama.

---

# 12. Comandos para trabajar con ramas

## Cambiar de rama

```powershell
git switch main
```

Cambia a `main`.

```powershell
git switch desarrollo/base-datos
```

Cambia a la rama de base de datos, si ya existe localmente.

## Crear una rama nueva

```powershell
git switch -c nombre-rama
```

Crea una rama y cambia a ella.

## Actualizar la rama principal

```powershell
git switch main
git pull origin main
```

## Actualizar la rama de trabajo con main

Primero guardar o confirmar los cambios locales.

Después:

```powershell
git switch desarrollo/base-datos
git merge main
```

**¿Qué hace?** Integra los cambios de `main` en la rama de base de datos.

Si aparecen conflictos, deben resolverse antes de continuar.

## Subir una rama nueva

```powershell
git push -u origin desarrollo/base-datos
```

**¿Qué hace?** Publica la rama y configura su seguimiento remoto.

En GitHub se recomienda crear un **Pull Request** para revisar e integrar los cambios a `main`.

---

# 13. Rutina diaria de trabajo

Antes de comenzar a programar:

```powershell
git status
git switch desarrollo/base-datos
git pull
```

Se debe utilizar la rama correspondiente a cada integrante.

Después de programar:

```powershell
python manage.py check
python manage.py test
git status
git add .
git commit -m "feat: avance del modulo"
git push
```

**¿Para qué sirve esta rutina?**

1. Comprobar y actualizar el código.
2. Trabajar en la rama correspondiente.
3. Verificar la configuración.
4. Ejecutar pruebas.
5. Registrar los cambios.
6. Compartir los avances.

No ejecutar `git pull` con cambios locales sin guardar cuando puedan generar conflictos.

---

# 14. Archivo .gitignore

El archivo `.gitignore` evita subir archivos locales o sensibles.

Configuración recomendada:

```gitignore
# Entorno virtual
venv/
.venv/

# Python
__pycache__/
*.pyc

# Base de datos local
db.sqlite3
db.sqlite3-journal

# Variables privadas
.env
.env.*

# Archivos subidos
media/

# Archivos recopilados
staticfiles/

# Archivos del editor
.vscode/
.idea/

# Sistema operativo
.DS_Store
Thumbs.db
```

Las migraciones de Django sí deben subirse a GitHub.

Si `db.sqlite3` ya estaba siendo rastreado, ejecutar:

```powershell
git rm --cached db.sqlite3
```

**¿Qué hace?** Deja de rastrear la base de datos local sin eliminar el archivo del computador.

Después:

```powershell
git add .gitignore
git commit -m "chore: excluir archivos locales"
git push
```

Esto no elimina copias anteriores del archivo en el historial de Git.

---

# 15. Actualizar las dependencias

Cuando un integrante instala una biblioteca nueva, debe actualizar el archivo de dependencias.

```powershell
python -m pip freeze > requirements.txt
```

**¿Qué hace?** Guarda las bibliotecas instaladas y sus versiones.

Antes de usarlo, comprobar que el entorno virtual esté activo y no contenga dependencias ajenas al proyecto.

Los demás integrantes actualizan sus dependencias con:

```powershell
python -m pip install -r requirements.txt
```

## Instalar Pillow

```powershell
python -m pip install Pillow
```

**¿Para qué sirve?** Permite trabajar con campos de imágenes en Django.

## Instalar Jazzmin (opcional)

```powershell
python -m pip install django-jazzmin
```

**¿Para qué sirve?** Personaliza la apariencia del panel administrativo de Django.

También requiere agregar `jazzmin` a `INSTALLED_APPS` antes de `django.contrib.admin`.

---

# 16. Errores comunes

### Error: No module named django

Causa posible: el entorno virtual no está activo o Django no está instalado.

Solución:

```powershell
.\venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Error: No module named nombre_app

Comprobar que la aplicación existe y está registrada en `INSTALLED_APPS`.

### Error: URLconf does not appear to have any patterns

Comprobar el archivo `urls.py` de la aplicación mencionada.

Debe contener al menos:

```python
from django.urls import path

urlpatterns = []
```

### Error: TemplateDoesNotExist

Comprobar que `settings.py` tenga:

```python
'DIRS': [BASE_DIR / 'templates'],
```

Y que la vista utilice la ruta correcta:

```python
return render(request, 'inicio.html')
```

### Error: no such table

Es posible que falten migraciones.

```powershell
python manage.py makemigrations
python manage.py migrate
```

### Error: puerto ocupado

Utilizar otro puerto:

```powershell
python manage.py runserver 8080
```

### Error: Git rechaza el push

Primero comprobar la rama:

```powershell
git branch
git status
```

Después revisar los commits remotos antes de integrar cambios. No usar `git push --force` como solución habitual.

---

# 17. Reglas del proyecto

- Solo el administrador puede autorizar clientes mayoristas.
- Las ventas de contado se registran como pagadas.
- Solo los mayoristas autorizados pueden comprar a crédito.
- El sistema debe impedir ventas superiores al inventario disponible.
- Los abonos deben ser mayores que cero y no superar el saldo pendiente.
- Las operaciones deben conservar fecha, hora y usuario responsable.
- Los registros históricos deben conservarse.
- Los plazos, recargos y momento de facturación deben validarse con el negocio antes de implementar reglas definitivas.

---

# 18. Seguridad y buenas prácticas

- No subir contraseñas ni claves secretas a GitHub.
- No incluir bases de datos con información real de clientes en el repositorio.
- No modificar directamente la rama `main` sin coordinación.
- Registrar las migraciones de los modelos.
- Probar las funcionalidades antes de integrar cambios.
- Utilizar transacciones para operaciones que modifican ventas, saldos e inventario.
- Conservar respaldos de información.
- Mantener actualizadas las dependencias.

---

# 19. Comandos esenciales de consulta rápida

| Comando | ¿Para qué sirve? |
|---|---|
| `python manage.py runserver` | Iniciar servidor |
| `python manage.py check` | Revisar configuración |
| `python manage.py makemigrations` | Crear migraciones |
| `python manage.py migrate` | Aplicar migraciones |
| `python manage.py createsuperuser` | Crear administrador |
| `python manage.py shell` | Abrir consola Django |
| `python manage.py test` | Ejecutar pruebas |
| `python manage.py startapp nombre` | Crear una aplicación |
| `git status` | Revisar cambios |
| `git add .` | Preparar cambios |
| `git commit -m "mensaje"` | Guardar versión |
| `git push` | Subir cambios |
| `git pull` | Descargar e integrar cambios |
| `git branch` | Consultar ramas |
| `git switch nombre` | Cambiar de rama |
| `git switch -c nombre` | Crear y cambiar de rama |
| `git log --oneline` | Consultar historial |
| `pip freeze > requirements.txt` | Actualizar dependencias |

---

# 20. Estado y objetivo de desarrollo

El proyecto se encuentra en desarrollo.

La estructura inicial contempla seis aplicaciones Django y una distribución de trabajo entre interfaz, base de datos y funcionalidades.

La prioridad es completar el siguiente proceso:

1. Registrar clientes y productos.
2. Consultar inventario.
3. Registrar ventas de contado.
4. Registrar ventas a crédito para mayoristas autorizados.
5. Controlar las cuentas pendientes.
6. Registrar abonos.
7. Actualizar saldos.
8. Consultar historial de operaciones.

Una vez completadas estas funciones, se realizarán pruebas de permisos, inventario, consistencia de transacciones y manejo de errores.

---

**Proyecto académico de Ingeniería de Software — Ingeniería de Sistemas.**

Repositorio: https://github.com/FAy08024/charcuteria