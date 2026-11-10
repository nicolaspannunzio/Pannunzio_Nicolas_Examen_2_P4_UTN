from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field

Nombre = Annotated[str, Field(min_length=3, max_length=100)]


class CategoriaBase(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    nombre: Nombre
    descripcion: Optional[str] = None


class CategoriaCreate(CategoriaBase):
    pass


class CategoriaUpdate(CategoriaBase):
    """PUT: reemplaza nombre y descripcion (activo solo cambia con DELETE)."""


class CategoriaPublic(CategoriaBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    activo: bool
    anulado_at: Optional[datetime] = None


class CategoriaEnProductoPublic(BaseModel):
    """Categoría tal como se ve desde un producto, con su marca de principal."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: Optional[str] = None
    es_principal: bool = False
