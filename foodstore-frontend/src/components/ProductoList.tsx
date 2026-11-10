import type { Producto } from "../types";
import { ProductoItem } from "./ProductoItem";

interface ProductoListProps {
  productos: Producto[];
  idOcupado: number | null;
  onEditar: (producto: Producto) => void;
  onCambiarDisponibilidad: (producto: Producto) => void;
  onAnular: (id: number) => void;
}

export function ProductoList({
  productos,
  idOcupado,
  onEditar,
  onCambiarDisponibilidad,
  onAnular,
}: ProductoListProps) {
  if (productos.length === 0) {
    return (
      <div className="text-center py-16 bg-slate-800/40 border border-slate-700/50 rounded-2xl p-8">
        <div className="mx-auto mb-3 text-slate-500 text-3xl">📦</div>
        <h3 className="text-lg font-semibold text-white">No hay productos en el catálogo</h3>
        <p className="text-sm text-slate-400 mt-1">
          Comenzá dando de alta un nuevo producto con el botón superior.
        </p>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {productos.map((prod) => (
        <ProductoItem
          key={prod.id}
          producto={prod}
          ocupado={idOcupado === prod.id}
          onEditar={onEditar}
          onCambiarDisponibilidad={onCambiarDisponibilidad}
          onAnular={onAnular}
        />
      ))}
    </div>
  );
}
