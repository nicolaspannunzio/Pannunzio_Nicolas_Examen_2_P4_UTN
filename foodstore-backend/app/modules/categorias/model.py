from datetime import datetime
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from app.modules.productos.model import ProductoCategoria

if TYPE_CHECKING:
    from app.modules.productos.model import Producto


class Categoria(SQLModel, table=True):
    __tablename__ = "categorias"

    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(nullable=False, index=True)
    descripcion: Optional[str] = Field(default=None)
    activo: bool = Field(default=True, nullable=False)
    anulado_at: Optional[datetime] = Field(default=None, nullable=True)

    # N:N con Producto a través de ProductoCategoria (link model)
    productos: List["Producto"] = Relationship(
        back_populates="categorias",
        link_model=ProductoCategoria,
        sa_relationship_kwargs={"overlaps": "categorias_link,categoria,producto"},
    )
