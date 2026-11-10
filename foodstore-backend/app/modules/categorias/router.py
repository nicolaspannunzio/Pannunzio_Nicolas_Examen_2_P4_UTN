from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Path, Query, status
from sqlmodel import Session

from app.core.database import get_session
from app.modules.categorias import service
from app.modules.categorias.schema import CategoriaCreate, CategoriaPublic, CategoriaUpdate

router = APIRouter(prefix="/api/v1/categorias", tags=["Categorías"])

SessionDep = Annotated[Session, Depends(get_session)]
IdPath = Annotated[int, Path(ge=1, description="Id de la categoría")]

R404 = {404: {"description": "Categoría no encontrada"}}
R409 = {409: {"description": "Conflicto (nombre repetido o categoría anulada)"}}


@router.post(
    "", response_model=CategoriaPublic, status_code=status.HTTP_201_CREATED,
    summary="Crear una categoría", responses=R409,
)
def crear(data: CategoriaCreate, session: SessionDep):
    return service.crear_categoria(data, session)


@router.get("", response_model=List[CategoriaPublic], summary="Listar categorías")
def listar(
    session: SessionDep,
    activo: Annotated[Optional[bool], Query(description="Omitido o true: activas; false: anuladas")] = None,
    search: Annotated[Optional[str], Query(description="Coincidencia parcial en el nombre")] = None,
):
    return service.listar_categorias(session, activo, search)


@router.get(
    "/{id}", response_model=CategoriaPublic, summary="Detalle de una categoría", responses=R404,
)
def obtener(id: IdPath, session: SessionDep):
    return service.obtener_categoria_por_id(id, session)


@router.put(
    "/{id}", response_model=CategoriaPublic, summary="Actualizar nombre y descripción",
    responses={**R404, **R409},
)
def actualizar(id: IdPath, data: CategoriaUpdate, session: SessionDep):
    return service.actualizar_categoria(id, data, session)


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT,
    summary="Anular una categoría (baja lógica)", responses={**R404, **R409},
)
def anular(id: IdPath, session: SessionDep):
    service.anular_categoria(id, session)
