// Los nombres de campo coinciden exactamente con los que devuelve la API.

export type TipoUnidadMedida = "peso" | "volumen" | "contable";

export interface UnidadMedida {
  id: number;
  nombre: string;
  simbolo: string;
  tipo: TipoUnidadMedida;
}

export interface Categoria {
  id: number;
  nombre: string;
  descripcion: string | null;
  activo: boolean;
  anulado_at: string | null;
}

/** Categoría tal como viene anidada dentro de un producto. */
export interface CategoriaEnProducto {
  id: number;
  nombre: string;
  descripcion: string | null;
  es_principal: boolean;
}

export interface Producto {
  id: number;
  nombre: string;
  descripcion: string | null;
  precio_base: number;
  stock_cantidad: number; // expresado en la unidad de venta
  hay_stock: boolean; // calculado por el backend (stock_cantidad > 0)
  disponible: boolean;
  activo: boolean;
  anulado_at: string | null;
  unidad_venta: UnidadMedida;
  categorias: CategoriaEnProducto[];
}

/** Cuerpo que se envía en POST y PUT /productos. */
export interface ProductoFormData {
  nombre: string;
  descripcion: string;
  precio_base: number;
  stock_cantidad: number;
  disponible: boolean;
  unidad_venta_id: number;
}
