from datetime import datetime, timezone
from decimal import Decimal
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select
from sqlalchemy.orm import selectinload

from app.modules.categorias.model import Categoria
from app.modules.categorias.schema import CategoriaEnProductoPublic
from app.modules.productos.model import Producto, ProductoCategoria
from app.modules.productos.schema import ProductoCreate, ProductoPublic, ProductoUpdate
from app.modules.unidades_medida.model import TipoUnidadMedida, UnidadMedida


def _no_encontrado(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


def _conflicto(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


# ---------------------------------------------------------------- helpers
def _obtener_producto(id: int, session: Session) -> Producto:
    producto = session.get(Producto, id)
    if producto is None:
        raise _no_encontrado(f"Producto con id {id} no encontrado")
    return producto


def _validar_unidad_y_stock(unidad_id: int, stock: Decimal, session: Session) -> None:
    """RN-03 (unidad existente) y RN-10 (stock entero si la unidad es contable)."""
    unidad = session.get(UnidadMedida, unidad_id)
    if unidad is None:
        raise _no_encontrado(f"Unidad de medida con id {unidad_id} no encontrada")
    if unidad.tipo == TipoUnidadMedida.CONTABLE and stock != stock.to_integral_value():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El stock de un producto con unidad contable debe ser un número entero",
        )


def _validar_nombre_unico(
    session: Session, nombre: str, excluir_id: Optional[int] = None
) -> None:
    """RN-02: el nombre es único entre los productos activos."""
    stmt = select(Producto).where(Producto.nombre == nombre, Producto.activo == True)  # noqa: E712
    if excluir_id is not None:
        stmt = stmt.where(Producto.id != excluir_id)
    if session.exec(stmt).first() is not None:
        raise _conflicto("Ya existe un producto activo con ese nombre")


def _a_categoria_publica(link: ProductoCategoria) -> CategoriaEnProductoPublic:
    cat = link.categoria
    return CategoriaEnProductoPublic(
        id=cat.id, nombre=cat.nombre, descripcion=cat.descripcion,
        es_principal=link.es_principal,
    )


def _a_public(prod: Producto) -> ProductoPublic:
    return ProductoPublic(
        id=prod.id,
        nombre=prod.nombre,
        descripcion=prod.descripcion,
        precio_base=prod.precio_base,
        stock_cantidad=prod.stock_cantidad,
        hay_stock=prod.stock_cantidad > 0,  # RN-11: se calcula en cada lectura
        disponible=prod.disponible,
        activo=prod.activo,
        anulado_at=prod.anulado_at,
        unidad_venta=prod.unidad_venta,
        categorias=[_a_categoria_publica(l) for l in prod.categorias_link],
    )


# ---------------------------------------------------------------- CRUD
def listar_productos(
    session: Session,
    skip: int = 0,
    limit: int = 10,
    activo: Optional[bool] = None,
    disponible: Optional[bool] = None,
    categoria_id: Optional[int] = None,
    search: Optional[str] = None,
) -> List[ProductoPublic]:
    # Omitido o true -> solo activos; false -> solo anulados
    stmt = select(Producto).where(Producto.activo == (True if activo is None else activo))
    if disponible is not None:
        stmt = stmt.where(Producto.disponible == disponible)
    if search:
        stmt = stmt.where(Producto.nombre.ilike(f"%{search}%"))
    if categoria_id is not None:
        # Subconsulta: evita filas duplicadas sin necesidad de DISTINCT
        stmt = stmt.where(
            Producto.id.in_(
                select(ProductoCategoria.producto_id).where(
                    ProductoCategoria.categoria_id == categoria_id
                )
            )
        )
    stmt = (
        stmt.options(
            selectinload(Producto.unidad_venta),
            selectinload(Producto.categorias_link).selectinload(ProductoCategoria.categoria),
        )
        .order_by(Producto.id)
        .offset(skip)
        .limit(limit)
    )
    return [_a_public(p) for p in session.exec(stmt).all()]


def obtener_producto_por_id(id: int, session: Session) -> ProductoPublic:
    return _a_public(_obtener_producto(id, session))


def crear_producto(data: ProductoCreate, session: Session) -> ProductoPublic:
    _validar_unidad_y_stock(data.unidad_venta_id, data.stock_cantidad, session)
    _validar_nombre_unico(session, data.nombre)

    prod = Producto(**data.model_dump())
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return _a_public(prod)


def actualizar_producto(id: int, data: ProductoUpdate, session: Session) -> ProductoPublic:
    prod = _obtener_producto(id, session)
    if not prod.activo:  # RN-05
        raise _conflicto("No se puede modificar un producto anulado")
    _validar_unidad_y_stock(data.unidad_venta_id, data.stock_cantidad, session)
    _validar_nombre_unico(session, data.nombre, excluir_id=id)

    # Solo los campos propios; activo y anulado_at nunca se tocan aquí (RN-12)
    for campo, valor in data.model_dump().items():
        setattr(prod, campo, valor)
    session.add(prod)
    session.commit()
    session.refresh(prod)
    return _a_public(prod)


def anular_producto(id: int, session: Session) -> None:
    prod = _obtener_producto(id, session)
    if not prod.activo:  # RN-04
        raise _conflicto("El producto ya se encuentra anulado")
    prod.activo = False
    prod.anulado_at = datetime.now(timezone.utc)
    session.add(prod)
    session.commit()
    # disponible y stock_cantidad se conservan (RN-12)


# ---------------------------------------------------------------- N:N
def clasificar_producto(
    producto_id: int, categoria_id: int, es_principal: bool, session: Session
) -> CategoriaEnProductoPublic:
    prod = _obtener_producto(producto_id, session)
    cat = session.get(Categoria, categoria_id)
    if cat is None:  # RN-03
        raise _no_encontrado(f"Categoría con id {categoria_id} no encontrada")

    if not prod.activo:  # RN-08
        raise _conflicto("No se puede clasificar un producto anulado")
    if not cat.activo:  # RN-08
        raise _conflicto("No se puede clasificar en una categoría anulada")
    if session.get(ProductoCategoria, (producto_id, categoria_id)) is not None:  # RN-07
        raise _conflicto("El producto ya está clasificado en esa categoría")

    if es_principal:  # RN-09: la principal anterior deja de serlo en la misma operación
        for link in session.exec(
            select(ProductoCategoria).where(
                ProductoCategoria.producto_id == producto_id,
                ProductoCategoria.es_principal == True,  # noqa: E712
            )
        ).all():
            link.es_principal = False
            session.add(link)

    link = ProductoCategoria(
        producto_id=producto_id, categoria_id=categoria_id, es_principal=es_principal
    )
    session.add(link)
    session.commit()
    session.refresh(link)
    return _a_categoria_publica(link)


def listar_categorias_de_producto(
    producto_id: int, session: Session
) -> List[CategoriaEnProductoPublic]:
    prod = _obtener_producto(producto_id, session)
    return [_a_categoria_publica(l) for l in prod.categorias_link]
