import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import type { Producto, ProductoFormData, UnidadMedida } from "../types";

interface ProductoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: ProductoFormData) => Promise<void>;
  productoAEditar: Producto | null;
  unidades: UnidadMedida[];
  errorServidor: string | null;
}

/** Estado del formulario: los campos numéricos se editan como texto y se convierten al enviar. */
interface FormState {
  nombre: string;
  descripcion: string;
  precio_base: string;
  stock_cantidad: string;
  disponible: boolean;
  unidad_venta_id: string;
}

const claseInput =
  "w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-emerald-500 disabled:opacity-50";
const claseLabel = "block text-xs font-semibold text-slate-300 mb-1";

function estadoInicial(producto: Producto | null, unidades: UnidadMedida[]): FormState {
  if (producto) {
    return {
      nombre: producto.nombre,
      descripcion: producto.descripcion ?? "",
      precio_base: String(producto.precio_base),
      stock_cantidad: String(producto.stock_cantidad),
      disponible: producto.disponible,
      unidad_venta_id: String(producto.unidad_venta.id),
    };
  }
  return {
    nombre: "",
    descripcion: "",
    precio_base: "",
    stock_cantidad: "0",
    disponible: true,
    unidad_venta_id: unidades[0] ? String(unidades[0].id) : "",
  };
}

export function ProductoModal({
  isOpen,
  onClose,
  onSubmit,
  productoAEditar,
  unidades,
  errorServidor,
}: ProductoModalProps) {
  if (!isOpen) return null;

  // El formulario se monta de cero cada vez que el modal se abre (vacío al crear,
  // con los datos del producto al editar), por eso no hace falta un useEffect.
  return (
    <FormularioProducto
      key={productoAEditar?.id ?? "nuevo"}
      onClose={onClose}
      onSubmit={onSubmit}
      productoAEditar={productoAEditar}
      unidades={unidades}
      errorServidor={errorServidor}
    />
  );
}

type FormularioProps = Omit<ProductoModalProps, "isOpen">;

function FormularioProducto({
  onClose,
  onSubmit,
  productoAEditar,
  unidades,
  errorServidor,
}: FormularioProps) {
  const [form, setForm] = useState<FormState>(() => estadoInicial(productoAEditar, unidades));
  const [guardando, setGuardando] = useState(false);

  const unidad = unidades.find((u) => u.id === Number(form.unidad_venta_id));
  const esContable = unidad?.tipo === "contable";

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>,
  ) => {
    const { name, value } = e.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setGuardando(true);
    try {
      await onSubmit({
        nombre: form.nombre.trim(),
        descripcion: form.descripcion.trim(),
        precio_base: Number(form.precio_base),
        stock_cantidad: Number(form.stock_cantidad),
        disponible: form.disponible,
        unidad_venta_id: Number(form.unidad_venta_id),
      });
    } finally {
      setGuardando(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-sm">
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-titulo"
        className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-lg shadow-2xl overflow-hidden"
      >
        <div className="p-5 border-b border-slate-800 flex justify-between items-center">
          <h2 id="modal-titulo" className="text-lg font-bold text-white">
            {productoAEditar ? "Editar producto" : "Nuevo producto"}
          </h2>
          <button
            type="button"
            onClick={onClose}
            aria-label="Cerrar"
            className="text-slate-400 hover:text-white transition-colors cursor-pointer"
          >
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {errorServidor && (
            <div
              role="alert"
              className="p-3 bg-rose-950/80 border border-rose-800 text-rose-300 text-sm rounded-lg"
            >
              {errorServidor}
            </div>
          )}

          <div>
            <label htmlFor="nombre" className={claseLabel}>
              Nombre (mín. 3 caracteres) *
            </label>
            <input
              id="nombre"
              name="nombre"
              type="text"
              required
              minLength={3}
              value={form.nombre}
              onChange={handleChange}
              className={claseInput}
              placeholder="Ej. Sorrentinos de ricota"
            />
          </div>

          <div>
            <label htmlFor="descripcion" className={claseLabel}>
              Descripción
            </label>
            <textarea
              id="descripcion"
              name="descripcion"
              rows={2}
              value={form.descripcion}
              onChange={handleChange}
              className={claseInput}
              placeholder="Detalle o ingredientes..."
            />
          </div>

          <div>
            <label htmlFor="unidad_venta_id" className={claseLabel}>
              Unidad de venta *
            </label>
            <select
              id="unidad_venta_id"
              name="unidad_venta_id"
              required
              value={form.unidad_venta_id}
              onChange={handleChange}
              className={claseInput}
            >
              {unidades.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.nombre} ({u.simbolo}) — {u.tipo}
                </option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label htmlFor="precio_base" className={claseLabel}>
                Precio ($ / {unidad?.simbolo ?? "unidad"}) *
              </label>
              <input
                id="precio_base"
                name="precio_base"
                type="number"
                step="0.01"
                min="0"
                required
                value={form.precio_base}
                onChange={handleChange}
                className={claseInput}
              />
            </div>

            <div>
              <label htmlFor="stock_cantidad" className={claseLabel}>
                Stock ({unidad?.simbolo ?? "unidad"}) *
              </label>
              <input
                id="stock_cantidad"
                name="stock_cantidad"
                type="number"
                step={esContable ? "1" : "0.001"}
                min="0"
                required
                value={form.stock_cantidad}
                onChange={handleChange}
                className={claseInput}
              />
              {esContable && (
                <p className="text-xs text-slate-500 mt-1">Unidad contable: solo números enteros.</p>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2 pt-2">
            <input
              id="disponible"
              type="checkbox"
              checked={form.disponible}
              onChange={(e) => setForm((prev) => ({ ...prev, disponible: e.target.checked }))}
              className="w-4 h-4 rounded bg-slate-800 border-slate-700 accent-emerald-500"
            />
            <label htmlFor="disponible" className="text-sm text-slate-300">
              Disponible para la venta
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-slate-800">
            <button
              type="button"
              onClick={onClose}
              disabled={guardando}
              className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 text-sm font-semibold rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={guardando || unidades.length === 0}
              className="px-4 py-2 bg-emerald-500 hover:bg-emerald-400 text-slate-950 text-sm font-bold rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {guardando ? "Guardando..." : "Guardar"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
