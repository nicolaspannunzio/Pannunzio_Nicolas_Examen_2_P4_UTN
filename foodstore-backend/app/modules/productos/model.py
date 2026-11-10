from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Numeric
from sqlmodel import Field, Relationship, SQLModel

from app.modules.unidades_medida.model import UnidadMedida

if TYPE_CHECKING:
    from app.modules.categorias.model import Categoria


class ProductoCategoria(SQLModel, table=True):
    """Link model N:N Producto <-> Categoria, con atributo propio es_principal."""

    __tablename__ = "producto_categoria"

    producto_id: int = Field(foreign_key="productos.id", primary_key=True)
    categoria_id: int = Field(foreign_key="categorias.id", primary_key=True)
    es_principal: bool = Field(default=False, nullable=False)

    producto: Optional["Producto"] = Relationship(
        back_populates="categorias_link",
        sa_relationship_kwargs={"overlaps": "categorias,productos"},
    )
    categoria: Optional["Categoria"] = Relationship(
        sa_relationship_kwargs={"overlaps": "categorias,productos"},
    )


class Producto(SQLModel, table=True):
    __tablename__ = "productos"

    id: Optional[int] = Field(default=None, primary_key=True)
    unidad_venta_id: int = Field(foreign_key="unidades_medida.id", nullable=False)
    nombre: str = Field(nullable=False, index=True)
    descripcion: Optional[str] = Field(default=None)
    precio_base: Decimal = Field(sa_column=Column(Numeric(12, 2), nullable=False))
    # Expresado en la unidad de venta (kg, u, L...). hay_stock NO se persiste (RN-11).
    stock_cantidad: Decimal = Field(
        default=Decimal("0"),
        sa_column=Column(Numeric(12, 3), nullable=False, server_default="0"),
    )
    disponible: bool = Field(default=True, nullable=False)
    activo: bool = Field(default=True, nullable=False)
    anulado_at: Optional[datetime] = Field(default=None, nullable=True)

    # 1:N con UnidadMedida
    unidad_venta: Optional[UnidadMedida] = Relationship(back_populates="productos")

    # N:N con Categoria (navegación directa) y acceso al atributo es_principal
    categorias_link: List[ProductoCategoria] = Relationship(
        back_populates="producto",
        sa_relationship_kwargs={"overlaps": "categorias,productos"},
    )
    categorias: List["Categoria"] = Relationship(
        back_populates="productos",
        link_model=ProductoCategoria,
        sa_relationship_kwargs={"overlaps": "categorias_link,categoria,producto"},
    )
