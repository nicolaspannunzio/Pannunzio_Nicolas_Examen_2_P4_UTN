from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.modules.categorias.model import Categoria
from app.modules.categorias.schema import CategoriaCreate, CategoriaUpdate


def _conflicto(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


def obtener_categoria_por_id(id: int, session: Session) -> Categoria:
    categoria = session.get(Categoria, id)
    if categoria is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Categoría con id {id} no encontrada",
        )
    return categoria


def _validar_nombre_unico(
    session: Session, nombre: str, excluir_id: Optional[int] = None
) -> None:
    """RN-02: el nombre es único entre las categorías activas."""
    stmt = select(Categoria).where(Categoria.nombre == nombre, Categoria.activo == True)  # noqa: E712
    if excluir_id is not None:
        stmt = stmt.where(Categoria.id != excluir_id)
    if session.exec(stmt).first() is not None:
        raise _conflicto("Ya existe una categoría activa con ese nombre")


def listar_categorias(
    session: Session, activo: Optional[bool] = None, search: Optional[str] = None
) -> List[Categoria]:
    # Omitido o true -> solo activas; false -> solo anuladas
    stmt = select(Categoria).where(Categoria.activo == (True if activo is None else activo))
    if search:
        stmt = stmt.where(Categoria.nombre.ilike(f"%{search}%"))
    return list(session.exec(stmt.order_by(Categoria.id)).all())


def crear_categoria(data: CategoriaCreate, session: Session) -> Categoria:
    _validar_nombre_unico(session, data.nombre)
    categoria = Categoria(nombre=data.nombre, descripcion=data.descripcion)
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def actualizar_categoria(id: int, data: CategoriaUpdate, session: Session) -> Categoria:
    categoria = obtener_categoria_por_id(id, session)
    if not categoria.activo:  # RN-05
        raise _conflicto("No se puede modificar una categoría anulada")
    _validar_nombre_unico(session, data.nombre, excluir_id=id)
    categoria.nombre = data.nombre
    categoria.descripcion = data.descripcion
    session.add(categoria)
    session.commit()
    session.refresh(categoria)
    return categoria


def anular_categoria(id: int, session: Session) -> None:
    categoria = obtener_categoria_por_id(id, session)
    if not categoria.activo:  # RN-04
        raise _conflicto("La categoría ya se encuentra anulada")
    categoria.activo = False
    categoria.anulado_at = datetime.now(timezone.utc)
    session.add(categoria)
    session.commit()
    # RN-06: no se toca ningún producto ni sus vínculos
