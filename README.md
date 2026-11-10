# Food Store — Catálogo de Productos

Sistema de administración del catálogo de **Food Store**: categorías, productos con su unidad de venta y stock propio, y clasificación de productos en una o más categorías.

**Programación IV**  -Segunda Evaluación Parcial- <br>
· Tecnicatura Universitaria en Programación (UTN) · 

## Stack

| Capa | Tecnologías |
| --- | --- |
| Backend | Python 3.12+, FastAPI, SQLModel, Pydantic v2, PostgreSQL 15+ (psycopg 3) |
| Frontend | React 19, TypeScript (strict), Vite, Tailwind CSS 4, `fetch` nativo |

## Estructura

```
foodstore-backend/    # API REST (módulos: unidades_medida, categorias, productos)
foodstore-frontend/   # Interfaz de administración de productos
```

Cada carpeta tiene su propio `README.md` con el detalle de instalación.

## Puesta en marcha

### 1. Base de datos
Crear una base vacía en PostgreSQL:
```sql
CREATE DATABASE foodstore_db;
```

### 2. Backend
```powershell
cd foodstore-backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
Copy-Item .env.example .env           # Linux/macOS: cp .env.example .env
# editar .env con tu usuario/contraseña de PostgreSQL
fastapi dev app/main.py
```
- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs

### 3. Frontend
```bash
cd foodstore-frontend
npm install
npm run dev
```
Abrir http://localhost:5173

## Funcionalidades

- **Productos**: alta, listado paginado con filtros (`activo`, `disponible`, `categoria_id`, `search`), detalle, edición, pausa de venta y baja lógica.
- **Stock por unidad de venta**: cada producto lleva su stock en la unidad en que se vende (kg, L, u, doc...). Para unidades contables el stock debe ser entero. `hay_stock` se calcula en cada lectura.
- **Categorías**: CRUD con baja lógica; anular una categoría no anula sus productos.
- **Clasificación N:N**: un producto pertenece a varias categorías y tiene a lo sumo una principal.
- **Baja lógica en todo**: nada se elimina físicamente (`activo = false` + `anulado_at`).

## Endpoints principales (`/api/v1`)

| Recurso | Endpoints |
| --- | --- |
| Unidades de medida | `GET /unidades-medida` |
| Categorías | `POST` · `GET` · `GET /{id}` · `PUT /{id}` · `DELETE /{id}` sobre `/categorias` |
| Productos | `POST` · `GET` · `GET /{id}` · `PUT /{id}` · `DELETE /{id}` sobre `/productos` |
| Clasificación | `POST /productos/{id}/categorias` · `GET /productos/{id}/categorias` |

Los errores se devuelven como `{"detail": ...}` con códigos 404 (no existe), 409 (conflicto de negocio) y 422 (validación).

## Pruebas de la API

Los archivos `foodstore-backend/tests/productos.http` y `relaciones.http` se ejecutan con la extensión **REST Client** de VS Code y cubren los endpoints, filtros y escenarios de error.

## Autor

**Nicolás A. Pannunzio** – Full Stack Developer & QA Automation  
🔗 [Perfil de LinkedIn](https://www.linkedin.com/in/nicolas-a-pannunzio-/)
