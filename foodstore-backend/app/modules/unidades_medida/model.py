from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.modules.productos.model import Producto


class TipoUnidadMedida(str, Enum):
    PESO = "peso"
    VOLUMEN = "volumen"
    CONTABLE = "contable"


class UnidadMedida(SQLModel, table=True):
    __tablename__ = "unidades_medida"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(unique=True, index=True, nullable=False)
    simbolo: str = Field(unique=True, nullable=False)
    tipo: TipoUnidadMedida = Field(nullable=False)

    # 1:N — una unidad se usa como unidad de venta de muchos productos
    productos: List["Producto"] = Relationship(back_populates="unidad_venta")


class UnidadMedidaPublic(SQLModel):
    id: int
    nombre: str
    simbolo: str
    tipo: TipoUnidadMedida
