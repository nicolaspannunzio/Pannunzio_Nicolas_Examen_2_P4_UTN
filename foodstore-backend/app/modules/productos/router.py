from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.categorias.schema import CategoriaEnProductoPublic
from app.modules.productos import service
from app.modules.productos.schema import (
    ClasificarCategoriaRequest,
    ProductoCreate,
    ProductoPublic,
    ProductoUpdate,
)

router = APIRouter(prefix="/api/v1/productos", tags=["Productos"])

SessionDep = Annotated[Session, Depends(get_session)]
IdPath = Annotated[int, Path(ge=1, description="Id del producto")]

R404 = {404: {"description": "Producto, unidad de venta o categoría inexistente"}}
R409 = {409: {"description": "Conflicto (nombre repetido, producto anulado, etc.)"}}
R422 = {422: {"description": "Validación fallida (p. ej. stock decimal en unidad contable)"}}


@router.post(
    "", response_model=ProductoPublic, status_code=status.HTTP_201_CREATED,
    summary="Crear un producto", responses={**R404, **R409, **R422},
)
def crear(data: ProductoCreate, session: SessionDep):
    return service.crear_producto(data, session)


@router.get("", response_model=List[ProductoPublic], summary="Listar productos con paginación y filtros")
def listar(
    session: SessionDep,
    skip: Annotated[int, Query(ge=0, description="Registros a saltear")] = 0,
    limit: Annotated[int, Query(ge=1, le=50, description="Máximo de registros")] = 10,
    activo: Annotated[Optional[bool], Query(description="Omitido o true: activos; false: anulados")] = None,
    disponible: Annotated[Optional[bool], Query(description="Filtra por disponible; omitido no filtra")] = None,
    categoria_id: Annotated[Optional[int], Query(description="Solo productos de esa categoría")] = None,
    search: Annotated[Optional[str], Query(description="Coincidencia parcial en el nombre")] = None,
):
    return service.listar_productos(session, skip, limit, activo, disponible, categoria_id, search)


@router.get(
    "/{id}", response_model=ProductoPublic,
    summary="Detalle (unidad de venta, categorías, stock y hay_stock)", responses=R404,
)
def obtener(id: IdPath, session: SessionDep):
    return service.obtener_producto_por_id(id, session)


@router.put(
    "/{id}", response_model=ProductoPublic, summary="Actualizar los campos propios del producto",
    responses={**R404, **R409, **R422},
)
def actualizar(id: IdPath, data: ProductoUpdate, session: SessionDep):
    return service.actualizar_producto(id, data, session)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Anular el producto (baja lógica)", responses={**R404, **R409},
)
def anular(id: IdPath, session: SessionDep):
    service.anular_producto(id, session)


# ------------------------------------------------ N:N Producto <-> Categoría
@router.post(
    "/{id}/categorias", response_model=CategoriaEnProductoPublic,
    status_code=status.HTTP_201_CREATED, summary="Clasificar el producto en una categoría",
    responses={**R404, **R409},
)
def clasificar(id: IdPath, data: ClasificarCategoriaRequest, session: SessionDep):
    return service.clasificar_producto(id, data.categoria_id, data.es_principal, session)


@router.get(
    "/{id}/categorias", response_model=List[CategoriaEnProductoPublic],
    summary="Listar las categorías del producto (indica la principal)", responses=R404,
)
def listar_categorias_producto(id: IdPath, session: SessionDep):
    return service.listar_categorias_de_producto(id, session)
