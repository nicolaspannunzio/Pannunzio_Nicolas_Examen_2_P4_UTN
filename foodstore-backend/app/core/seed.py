from sqlmodel import Session, select

from app.modules.unidades_medida.model import TipoUnidadMedida, UnidadMedida

UNIDADES_SEMILLA = [
    {"nombre": "kilogramo", "simbolo": "kg", "tipo": TipoUnidadMedida.PESO},
    {"nombre": "gramo", "simbolo": "g", "tipo": TipoUnidadMedida.PESO},
    {"nombre": "litro", "simbolo": "L", "tipo": TipoUnidadMedida.VOLUMEN},
    {"nombre": "mililitro", "simbolo": "mL", "tipo": TipoUnidadMedida.VOLUMEN},
    {"nombre": "pieza", "simbolo": "u", "tipo": TipoUnidadMedida.CONTABLE},
    {"nombre": "docena", "simbolo": "doc", "tipo": TipoUnidadMedida.CONTABLE},
]


def seed_unidades_medida(session: Session) -> None:
    """Inserta las unidades solo si la tabla está vacía (idempotente)."""
    if session.exec(select(UnidadMedida)).first() is not None:
        return
    session.add_all(UnidadMedida(**u) for u in UNIDADES_SEMILLA)
    session.commit()
