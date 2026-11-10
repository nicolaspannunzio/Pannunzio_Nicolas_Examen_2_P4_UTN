import type { Producto } from "../types";

interface ProductoItemProps {
  producto: Producto;
  ocupado: boolean; // hay una operación en curso sobre este producto
  onEditar: (producto: Producto) => void;
  onCambiarDisponibilidad: (producto: Producto) => void;
  onAnular: (id: number) => void;
}

const formatoPrecio = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});
const formatoStock = new Intl.NumberFormat("es-AR", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 3,
});

export function ProductoItem({
  producto,
  ocupado,
  onEditar,
  onCambiarDisponibilidad,
  onAnular,
}: ProductoItemProps) {
  const simbolo = producto.unidad_venta.simbolo;

  return (
    <div className="bg-slate-800/80 border border-slate-700/60 rounded-xl p-5 flex flex-col justify-between hover:border-slate-600 transition-all shadow-sm">
      <div>
        <div className="flex items-start justify-between gap-3 mb-2">
          <h3 className="font-semibold text-lg text-white leading-snug">{producto.nombre}</h3>
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-700 text-slate-300">
            {simbolo}
          </span>
        </div>

        <p className="text-sm text-slate-400 line-clamp-2 mb-4">
          {producto.descripcion || "Sin descripción disponible."}
        </p>

        <div className="grid grid-cols-2 gap-2 p-3 bg-slate-900/50 rounded-lg border border-slate-800 mb-4">
          <div>
            <span className="text-xs text-slate-400 block">Precio</span>
            <span className="text-base font-bold text-emerald-400">
              $ {formatoPrecio.format(producto.precio_base)} / {simbolo}
            </span>
          </div>
          <div>
            <span className="text-xs text-slate-400 block">Existencias</span>
            <span className="text-base font-semibold text-slate-200">
              stock: {formatoStock.format(producto.stock_cantidad)} {simbolo}
            </span>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 mb-4">
          <span
            className={`text-xs px-2.5 py-1 rounded-full font-medium inline-flex items-center gap-1.5 border ${
              producto.disponible
                ? "bg-emerald-950 text-emerald-300 border-emerald-800"
                : "bg-amber-950 text-amber-300 border-amber-800"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                producto.disponible ? "bg-emerald-400" : "bg-amber-400"
              }`}
            />
            {producto.disponible ? "Disponible" : "Venta desactivada"}
          </span>

          <span
            className={`text-xs px-2.5 py-1 rounded-full font-medium inline-flex items-center gap-1.5 border ${
              producto.hay_stock
                ? "bg-blue-950 text-blue-300 border-blue-800"
                : "bg-rose-950 text-rose-300 border-rose-800"
            }`}
          >
            <span
              className={`w-1.5 h-1.5 rounded-full ${
                producto.hay_stock ? "bg-blue-400" : "bg-rose-400"
              }`}
            />
            {producto.hay_stock ? "Hay stock" : "Sin stock"}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-2 pt-3 border-t border-slate-700/50">
        <button
          type="button"
          onClick={() => onEditar(producto)}
          disabled={ocupado}
          className="flex-1 py-1.5 px-3 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-semibold rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Editar
        </button>
        <button
          type="button"
          onClick={() => onCambiarDisponibilidad(producto)}
          disabled={ocupado}
          title={producto.disponible ? "Pausar la venta" : "Reanudar la venta"}
          className={`flex-1 py-1.5 px-3 text-xs font-semibold rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed ${
            producto.disponible
              ? "bg-amber-900/60 hover:bg-amber-900 text-amber-200"
              : "bg-emerald-900/60 hover:bg-emerald-900 text-emerald-200"
          }`}
        >
          Disponibilidad
        </button>
        <button
          type="button"
          onClick={() => onAnular(producto.id)}
          disabled={ocupado}
          title="Anular producto (baja lógica)"
          className="py-1.5 px-3 bg-rose-950/60 hover:bg-rose-900 text-rose-300 text-xs font-semibold rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Anular
        </button>
      </div>
    </div>
  );
}
