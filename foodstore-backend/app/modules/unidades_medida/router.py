from typing import List

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.modules.unidades_medida.model import UnidadMedida, UnidadMedidaPublic

router = APIRouter(prefix="/api/v1/unidades-medida", tags=["Unidades de Medida"])


@router.get(
    "",
    response_model=List[UnidadMedidaPublic],
    summary="Listar el catálogo de unidades de medida",
    description="Catálogo de solo lectura (seed inicial). Origen del selector de unidad de venta.",
)
def listar_unidades(session: Session = Depends(get_session)):
    return session.exec(select(UnidadMedida).order_by(UnidadMedida.id)).all()
