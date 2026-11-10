import { useEffect, useState } from "react";
import type { Producto, ProductoFormData, UnidadMedida } from "./types";
import { Navbar } from "./components/Navbar";
import { ProductoList } from "./components/ProductoList";
import { ProductoModal } from "./components/ProductoModal";

const API_BASE: string = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000/api/v1";

const MSG_SIN_CONEXION = "No se pudo conectar con el servidor de Food Store";

/** Extrae el mensaje de error de la API. FastAPI devuelve {"detail": "..."} en 404/409
 *  y {"detail": [{"msg": "..."}, ...]} en los 422 de validación de Pydantic. */
async function mensajeDeError(res: Response, porDefecto: string): Promise<string> {
  try {
    const cuerpo: unknown = await res.json();
    if (typeof cuerpo === "object" && cuerpo !== null && "detail" in cuerpo) {
      const detail = cuerpo.detail;
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        const mensajes = detail
          .map((d: unknown) =>
            typeof d === "object" && d !== null && "msg" in d ? String(d.msg) : "",
          )
          .filter(Boolean);
        if (mensajes.length > 0) return mensajes.join(". ");
      }
    }
  } catch {
    // el cuerpo no era JSON: se usa el mensaje por defecto
  }
  return porDefecto;
}

/** Un fallo de red de fetch es un TypeError sin información útil para el usuario. */
function mensajeDeExcepcion(err: unknown, porDefecto: string): string {
  if (err instanceof TypeError) return MSG_SIN_CONEXION;
  return err instanceof Error ? err.message : porDefecto;
}

async function pedirProductos(): Promise<Producto[]> {
  const res = await fetch(`${API_BASE}/productos?limit=50`);
  if (!res.ok) throw new Error(await mensajeDeError(res, "No se pudo cargar el catálogo"));
  return (await res.json()) as Producto[];
}

async function pedirUnidades(): Promise<UnidadMedida[]> {
  const res = await fetch(`${API_BASE}/unidades-medida`);
  if (!res.ok) throw new Error(await mensajeDeError(res, "No se pudieron cargar las unidades"));
  return (await res.json()) as UnidadMedida[];
}

export function App() {
  // Estado del catálogo (vive acá; los hijos lo reciben por props)
  const [productos, setProductos] = useState<Producto[]>([]);
  const [unidades, setUnidades] = useState<UnidadMedida[]>([]);
  const [cargando, setCargando] = useState<boolean>(true);
  const [errorGlobal, setErrorGlobal] = useState<string | null>(null);

  // Estado del modal
  const [modalAbierto, setModalAbierto] = useState<boolean>(false);
  const [productoSeleccionado, setProductoSeleccionado] = useState<Producto | null>(null);
  const [errorModal, setErrorModal] = useState<string | null>(null);

  // Operaciones sobre una fila (disponibilidad / anulación)
  const [idOcupado, setIdOcupado] = useState<number | null>(null);
  const [errorAccion, setErrorAccion] = useState<string | null>(null);

  // Se incrementa para volver a disparar la carga inicial (botón Reintentar)
  const [intentos, setIntentos] = useState<number>(0);

  // Refresco tras alta / edición / disponibilidad / anulación (sin spinner a pantalla completa)
  const refrescarProductos = async () => {
    try {
      setProductos(await pedirProductos());
      setErrorGlobal(null);
    } catch (err) {
      setErrorGlobal(mensajeDeExcepcion(err, "Error al actualizar el catálogo"));
    }
  };

  // Carga inicial del catálogo y de las unidades de medida
  useEffect(() => {
    let cancelado = false;
    Promise.all([pedirProductos(), pedirUnidades()])
      .then(([dataProd, dataUni]) => {
        if (cancelado) return;
        setProductos(dataProd);
        setUnidades(dataUni);
      })
      .catch((err: unknown) => {
        if (!cancelado) setErrorGlobal(mensajeDeExcepcion(err, "Error al cargar la información"));
      })
      .finally(() => {
        if (!cancelado) setCargando(false);
      });
    return () => {
      cancelado = true;
    };
  }, [intentos]);

  const reintentar = () => {
    setErrorGlobal(null);
    setCargando(true);
    setIntentos((n) => n + 1);
  };

  const abrirModalCrear = () => {
    setProductoSeleccionado(null);
    setErrorModal(null);
    setModalAbierto(true);
  };

  const abrirModalEditar = (producto: Producto) => {
    setProductoSeleccionado(producto);
    setErrorModal(null);
    setModalAbierto(true);
  };

  const cerrarModal = () => {
    setModalAbierto(false);
    setErrorModal(null);
  };

  const guardarProducto = async (formData: ProductoFormData) => {
    setErrorModal(null);
    const editando = productoSeleccionado !== null;
    const url = editando
      ? `${API_BASE}/productos/${productoSeleccionado.id}`
      : `${API_BASE}/productos`;

    try {
      const res = await fetch(url, {
        method: editando ? "PUT" : "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      if (!res.ok) throw new Error(await mensajeDeError(res, "Error al guardar el producto"));

      cerrarModal();
      await refrescarProductos();
    } catch (err) {
      // 409 (nombre repetido), 422, etc.: el modal queda abierto mostrando el error
      setErrorModal(mensajeDeExcepcion(err, "Error al guardar el producto"));
    }
  };

  const cambiarDisponibilidad = async (producto: Producto) => {
    setErrorAccion(null);
    setIdOcupado(producto.id);
    try {
      const body: ProductoFormData = {
        nombre: producto.nombre,
        descripcion: producto.descripcion ?? "",
        precio_base: producto.precio_base,
        stock_cantidad: producto.stock_cantidad,
        disponible: !producto.disponible,
        unidad_venta_id: producto.unidad_venta.id,
      };
      const res = await fetch(`${API_BASE}/productos/${producto.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await mensajeDeError(res, "Error al cambiar la disponibilidad"));
      await refrescarProductos();
    } catch (err) {
      setErrorAccion(mensajeDeExcepcion(err, "Error al cambiar la disponibilidad"));
    } finally {
      setIdOcupado(null);
    }
  };

  const anularProducto = async (id: number) => {
    if (!window.confirm("¿Seguro que querés anular este producto?")) return;

    setErrorAccion(null);
    setIdOcupado(id);
    try {
      const res = await fetch(`${API_BASE}/productos/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error(await mensajeDeError(res, "Error al anular el producto"));
      await refrescarProductos();
    } catch (err) {
      setErrorAccion(mensajeDeExcepcion(err, "Error al anular el producto"));
    } finally {
      setIdOcupado(null);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 flex flex-col font-sans">
      <Navbar onNuevoProducto={abrirModalCrear} />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-6 flex justify-between items-end">
          <div>
            <h2 className="text-2xl font-bold text-white tracking-tight">Catálogo de productos</h2>
            <p className="text-sm text-slate-400 mt-1">
              Gestión de stock, disponibilidad y precios vigentes.
            </p>
          </div>
          {!cargando && !errorGlobal && (
            <span className="text-xs text-slate-400 font-medium">
              Productos activos: {productos.length}
            </span>
          )}
        </div>

        {errorAccion && (
          <div
            role="alert"
            className="p-3 bg-rose-950 border border-rose-800 text-rose-300 rounded-xl mb-6 flex justify-between items-center text-sm"
          >
            <span>{errorAccion}</span>
            <button
              type="button"
              onClick={() => setErrorAccion(null)}
              className="px-2 text-rose-300 hover:text-white cursor-pointer"
              aria-label="Cerrar aviso"
            >
              ✕
            </button>
          </div>
        )}

        {cargando && (
          <div className="flex flex-col items-center justify-center py-20" role="status">
            <div className="w-10 h-10 border-4 border-emerald-500 border-t-transparent rounded-full animate-spin mb-4" />
            <p className="text-slate-400 font-medium text-sm">Cargando catálogo de productos...</p>
          </div>
        )}

        {!cargando && errorGlobal && (
          <div
            role="alert"
            className="p-4 bg-rose-950 border border-rose-800 text-rose-300 rounded-xl mb-6 flex justify-between items-center"
          >
            <span>{errorGlobal}</span>
            <button
              type="button"
              onClick={reintentar}
              className="px-3 py-1 bg-rose-900 hover:bg-rose-800 text-white rounded text-xs font-semibold cursor-pointer"
            >
              Reintentar
            </button>
          </div>
        )}

        {!cargando && !errorGlobal && (
          <ProductoList
            productos={productos}
            idOcupado={idOcupado}
            onEditar={abrirModalEditar}
            onCambiarDisponibilidad={cambiarDisponibilidad}
            onAnular={anularProducto}
          />
        )}
      </main>

      <ProductoModal
        isOpen={modalAbierto}
        onClose={cerrarModal}
        onSubmit={guardarProducto}
        productoAEditar={productoSeleccionado}
        unidades={unidades}
        errorServidor={errorModal}
      />
    </div>
  );
}

export default App;
