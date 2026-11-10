from datetime import datetime
from decimal import Decimal
from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field, PlainSerializer

from app.modules.categorias.schema import CategoriaEnProductoPublic
from app.modules.unidades_medida.model import UnidadMedidaPublic

# --- Tipos con validación declarada (Annotated + Field) ---
Nombre = Annotated[str, Field(min_length=3, max_length=100)]
Precio = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=2)]
Stock = Annotated[Decimal, Field(ge=0, max_digits=12, decimal_places=3)]
IdFK = Annotated[int, Field(gt=0)]

# En la respuesta, los Decimal se emiten como número JSON (no como string)
DecimalComoNumero = Annotated[Decimal, PlainSerializer(float, return_type=float, when_used="json")]


class ProductoBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: Nombre
    descripcion: Optional[str] = None
    precio_base: Precio
    unidad_venta_id: IdFK
    stock_cantidad: Stock = Decimal("0")
    disponible: bool = True


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(ProductoBase):
    """PUT: mismos campos que Create; reemplaza los campos propios del producto."""


class ProductoPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    precio_base: DecimalComoNumero
    stock_cantidad: DecimalComoNumero
    hay_stock: bool  # calculado en el servicio (RN-11); no se persiste
    disponible: bool
    activo: bool
    anulado_at: Optional[datetime] = None
    unidad_venta: UnidadMedidaPublic
    categorias: List[CategoriaEnProductoPublic] = []


class ClasificarCategoriaRequest(BaseModel):
    categoria_id: IdFK
    es_principal: bool = False
