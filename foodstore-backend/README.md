# Food Store — Backend (FastAPI + SQLModel + PostgreSQL)

API REST del catálogo de productos (Programación IV — Parcial 2).

## Requisitos
- Python 3.12 o superior
- PostgreSQL 15 o superior

## 1. Base de datos
Crear la base vacía (por ejemplo desde DBeaver o `psql`):
```sql
CREATE DATABASE foodstore_db;
```
Las tablas se crean solas al iniciar la API y el seed de `UnidadMedida`
(kg, g, L, mL, u, doc) solo inserta si la tabla está vacía.

> Si ya tenías tablas de una versión anterior, borrá y recreá la base:
> `create_all` no modifica tablas existentes.

## 2. Instalación (PowerShell)
Desde la carpeta `foodstore-backend`:
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```
Linux/macOS: `source .venv/bin/activate` en lugar del segundo comando.

> Si PowerShell bloquea el script de activación, ejecutar antes (solo afecta a esa terminal):
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`

## 3. Configurar la conexión a PostgreSQL
La cadena de conexión se define en `app/core/database.py` (`DATABASE_URL`), que la
lee del archivo `.env`:
```powershell
Copy-Item .env.example .env        # Linux/macOS: cp .env.example .env
```
Editar `.env` con tus datos:
```
DATABASE_URL=postgresql+psycopg://USUARIO:CONTRASEÑA@localhost:5432/foodstore_db
```
- El `.env` **no se sube al repositorio** (está en `.gitignore`); `.env.example` sí.
- Si la contraseña tiene caracteres especiales (`@ : / #`), codificarlos (`@` → `%40`).
- Si no existe `.env`, se usa `postgresql+psycopg://postgres:postgres@localhost:5432/foodstore_db`.
- Una variable de entorno `DATABASE_URL` del sistema tiene prioridad sobre el `.env`.

## 4. Ejecución
```powershell
fastapi dev app/main.py
```
- API: http://127.0.0.1:8000
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## Pruebas
Con la extensión *REST Client* de VS Code, abrir y ejecutar de arriba hacia abajo
(sobre una base recién creada):
- `tests/productos.http` — CRUD de productos, filtros, stock, errores 404/409/422.
- `tests/relaciones.http` — categorías, clasificación N:N, categoría principal.

## Estructura
```
app/
├── main.py              # app, CORS, routers, lifespan (tablas + seed)
├── core/                # database.py (engine, sesión), seed.py
└── modules/
    ├── unidades_medida/ # model, router (catálogo de solo lectura)
    ├── categorias/      # model, schema, service, router
    └── productos/       # model (+ ProductoCategoria), schema, service, router
```
