# Food Store — Frontend (React + TypeScript + Vite + Tailwind CSS 4)

Interfaz de administración del catálogo de productos (Programación IV — Parcial 2).
Usa `fetch` nativo, `useState` y `useEffect`; el estado del catálogo vive en `App.tsx`.

## Requisitos
- Node.js 20 o superior
- El backend corriendo en `http://127.0.0.1:8000` (ver `foodstore-backend/README.md`)

## Instalación y ejecución
```bash
npm install
npm run dev
```
Abrir http://localhost:5173 (origen habilitado por CORS en el backend).

Si el backend corre en otra dirección, crear un archivo `.env` con:
```
VITE_API_URL=http://127.0.0.1:8000/api/v1
```

## Scripts
- `npm run dev` — servidor de desarrollo
- `npm run build` — chequeo de tipos (`tsc`, modo estricto) y build de producción
- `npm run lint` — ESLint

## Estructura
```
src/
├── components/   # Navbar, ProductoList, ProductoItem, ProductoModal
├── types/        # interfaces Producto, UnidadMedida, Categoria (mismos campos que la API)
├── App.tsx       # estado, efectos y llamadas a la API
├── main.tsx
└── index.css     # @import "tailwindcss"
```
